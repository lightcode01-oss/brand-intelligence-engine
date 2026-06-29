import uuid
import re
from datetime import datetime, timezone
from typing import Optional, Sequence, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.collaboration import CommentThread, Comment, Mention
from app.models.user import User
from app.repositories.collaboration import SqlAlchemyCommentThreadRepository, SqlAlchemyCommentRepository
from app.services.collaboration.websocket import manager

class CommentsService:
    """Manages brand name comment threads, resolutions, pins, and mentions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.thread_repo = SqlAlchemyCommentThreadRepository(db)
        self.comment_repo = SqlAlchemyCommentRepository(db)

    async def get_or_create_thread(
        self, workspace_id: uuid.UUID, project_id: uuid.UUID, name_id: uuid.UUID
    ) -> CommentThread:
        """Retrieves active thread or creates a new one for a generated name ID."""
        thread = await self.thread_repo.get_by_name(name_id)
        if not thread:
            thread = CommentThread(
                workspace_id=workspace_id,
                project_id=project_id,
                name_id=name_id
            )
            thread = await self.thread_repo.create(thread)
            await self.db.flush()
        return thread

    async def add_comment(
        self, thread_id: uuid.UUID, user_id: uuid.UUID, content: str, parent_id: Optional[uuid.UUID] = None
    ) -> Comment:
        """Adds a comment or reply reply inside a thread, parses mentions, and broadcasts changes."""
        comment = Comment(
            thread_id=thread_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id
        )
        comment = await self.comment_repo.create(comment)
        await self.db.flush()
        
        # Load thread metadata to broadcast
        thread = await self.thread_repo.get(thread_id)
        
        # Parse mentions asynchronously
        await self._parse_and_create_mentions(comment, content, thread.workspace_id)
        
        # Trigger WebSocket updates
        if thread:
            await manager.broadcast_to_workspace(
                workspace_id=thread.workspace_id,
                event="comment_created",
                data={
                    "id": str(comment.id),
                    "thread_id": str(thread_id),
                    "user_id": str(user_id),
                    "content": content,
                    "parent_id": str(parent_id) if parent_id else None,
                    "created_at": comment.created_at.isoformat() if comment.created_at else None
                }
            )
            
        return comment

    async def edit_comment(self, comment_id: uuid.UUID, user_id: uuid.UUID, new_content: str) -> Optional[Comment]:
        """Edits an existing comment and broadcasts edits if owner matches."""
        comment = await self.comment_repo.get(comment_id)
        if not comment or comment.user_id != user_id:
            return None
            
        comment.content = new_content
        comment.is_edited = True
        await self.comment_repo.update(comment)
        await self.db.flush()
        
        thread = await self.thread_repo.get(comment.thread_id)
        if thread:
            await manager.broadcast_to_workspace(
                workspace_id=thread.workspace_id,
                event="comment_edited",
                data={
                    "id": str(comment.id),
                    "thread_id": str(thread.id),
                    "content": new_content,
                    "updated_at": comment.updated_at.isoformat() if comment.updated_at else None
                }
            )
        return comment

    async def delete_comment(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Soft-deletes a comment block if owner matches."""
        comment = await self.comment_repo.get(comment_id)
        if not comment or comment.user_id != user_id:
            return False
            
        thread_id = comment.thread_id
        await self.comment_repo.delete(comment_id)
        await self.db.flush()
        
        thread = await self.thread_repo.get(thread_id)
        if thread:
            await manager.broadcast_to_workspace(
                workspace_id=thread.workspace_id,
                event="comment_deleted",
                data={
                    "id": str(comment_id),
                    "thread_id": str(thread_id)
                }
            )
        return True

    async def toggle_pin(self, comment_id: uuid.UUID) -> Optional[Comment]:
        """Pins or unpins a comment in a thread."""
        comment = await self.comment_repo.get(comment_id)
        if not comment:
            return None
            
        comment.is_pinned = not comment.is_pinned
        await self.comment_repo.update(comment)
        await self.db.flush()
        
        thread = await self.thread_repo.get(comment.thread_id)
        if thread:
            await manager.broadcast_to_workspace(
                workspace_id=thread.workspace_id,
                event="comment_pinned",
                data={
                    "id": str(comment.id),
                    "thread_id": str(thread.id),
                    "is_pinned": comment.is_pinned
                }
            )
        return comment

    async def resolve_thread(self, thread_id: uuid.UUID, user_id: uuid.UUID) -> Optional[CommentThread]:
        """Resolves comment thread state and triggers websocket notification."""
        thread = await self.thread_repo.get(thread_id)
        if not thread:
            return None
            
        thread.is_resolved = True
        thread.resolved_by = user_id
        thread.resolved_at = datetime.now(timezone.utc)
        await self.thread_repo.update(thread)
        await self.db.flush()
        
        await manager.broadcast_to_workspace(
            workspace_id=thread.workspace_id,
            event="thread_resolved",
            data={
                "thread_id": str(thread_id),
                "resolved_by": str(user_id),
                "resolved_at": thread.resolved_at.isoformat()
            }
        )
        return thread

    async def list_comments_by_name(self, name_id: uuid.UUID) -> List[Comment]:
        """Lists comments attached to a specific name ID."""
        thread = await self.thread_repo.get_by_name(name_id)
        if not thread:
            return []
        return list(await self.comment_repo.list_by_thread(thread.id))

    async def _parse_and_create_mentions(self, comment: Comment, content: str, workspace_id: uuid.UUID):
        """Helper extracting @username references and saving mention and notification alerts."""
        # Find usernames like @john
        usernames = re.findall(r"@(\w+)", content)
        if not usernames:
            return
            
        for username in set(usernames):
            # Query user by email prefix (or mock display name match)
            stmt = select(User).where(
                User.email.like(f"{username.lower()}%"),
                User.deleted_at == None
            )
            target_user = (await self.db.execute(stmt)).scalar()
            
            if target_user:
                # Save mention mapping
                mention = Mention(comment_id=comment.id, user_id=target_user.id)
                self.db.add(mention)
                
                # Create Notification alert
                from app.models.user import Notification
                alert = Notification(
                    user_id=target_user.id,
                    type="IN_APP",
                    category="mention",
                    title="You were mentioned",
                    message=f"Someone mentioned you in a comment: \"{content[:60]}\"",
                    sender_id=comment.user_id,
                    data_json={"comment_id": str(comment.id), "thread_id": str(comment.thread_id)}
                )
                self.db.add(alert)
                await self.db.flush()
                
                # Notify target user via WebSocket
                await manager.send_to_user(
                    user_id=str(target_user.id),
                    event="notification_received",
                    data={
                        "id": str(alert.id),
                        "category": "mention",
                        "title": alert.title,
                        "message": alert.message,
                        "created_at": alert.created_at.isoformat() if alert.created_at else None
                    }
                )
