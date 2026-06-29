import uuid
from typing import List, Optional
from fastapi import APIRouter, Request, Depends, status, HTTPException, WebSocket, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.security.jwt import decode_jwt
from app.models.user import User
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.collaboration import (
    CommentCreate, CommentUpdate, CommentResponse, CommentThreadResponse,
    FavoriteResponse, CollectionCreate, CollectionResponse, CollectionItemResponse
)
from app.services.collaboration.comments import CommentsService
from app.services.collaboration.favorites import FavoritesService
from app.services.collaboration.collections import CollectionsService
from app.services.collaboration.websocket import manager

router = APIRouter(tags=["Collaboration & Real-Time"])

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    workspace_id: uuid.UUID = Query(...)
):
    """Establishes real-time persistent connections, handles authorization and presence updates."""
    try:
        payload = decode_jwt(token)
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        await websocket.close(code=1008) # Policy Violation
        return
        
    await manager.connect(websocket, str(user_id), str(workspace_id))
    try:
        while True:
            # Standby listening for client signals (e.g. heartbeat or settings changes)
            message = await websocket.receive_text()
    except Exception:
        pass
    finally:
        await manager.disconnect(websocket, str(user_id), str(workspace_id))

# --- Comments Endpoints ---

@router.post("/comment-threads", response_model=StandardResponse[CommentThreadResponse], status_code=status.HTTP_201_CREATED)
async def get_or_create_comment_thread(
    request: Request,
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    name_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[CommentThreadResponse]:
    service = CommentsService(db)
    thread = await service.get_or_create_thread(workspace_id, project_id, name_id)
    return wrap_success_response(thread, request, "Comment thread initialized.")

@router.post("/comment-threads/{thread_id}/comments", response_model=StandardResponse[CommentResponse], status_code=status.HTTP_201_CREATED)
async def add_comment(
    request: Request,
    thread_id: uuid.UUID,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[CommentResponse]:
    service = CommentsService(db)
    comment = await service.add_comment(
        thread_id=thread_id,
        user_id=current_user.id,
        content=payload.content,
        parent_id=payload.parent_id
    )
    return wrap_success_response(comment, request, "Comment added successfully.")

@router.put("/comments/{comment_id}", response_model=StandardResponse[CommentResponse])
async def edit_comment(
    request: Request,
    comment_id: uuid.UUID,
    payload: CommentUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[CommentResponse]:
    service = CommentsService(db)
    comment = await service.edit_comment(comment_id, current_user.id, payload.content)
    if not comment:
        raise HTTPException(status_code=403, detail="Unauthorized to edit comment or comment not found.")
    return wrap_success_response(comment, request, "Comment edited successfully.")

@router.delete("/comments/{comment_id}", response_model=StandardResponse[dict])
async def delete_comment(
    request: Request,
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    service = CommentsService(db)
    success = await service.delete_comment(comment_id, current_user.id)
    if not success:
        raise HTTPException(status_code=403, detail="Unauthorized to delete comment or comment not found.")
    return wrap_success_response({"id": comment_id, "deleted": True}, request, "Comment deleted.")

@router.put("/comments/{comment_id}/pin", response_model=StandardResponse[CommentResponse])
async def toggle_pin_comment(
    request: Request,
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[CommentResponse]:
    service = CommentsService(db)
    comment = await service.toggle_pin(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")
    return wrap_success_response(comment, request, "Comment pin state updated.")

@router.put("/comment-threads/{thread_id}/resolve", response_model=StandardResponse[CommentThreadResponse])
async def resolve_comment_thread(
    request: Request,
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[CommentThreadResponse]:
    service = CommentsService(db)
    thread = await service.resolve_thread(thread_id, current_user.id)
    if not thread:
        raise HTTPException(status_code=404, detail="Comment thread not found.")
    return wrap_success_response(thread, request, "Comment thread resolved.")

@router.get("/names/{name_id}/comments", response_model=StandardResponse[List[CommentResponse]])
async def list_comments_by_name(
    request: Request,
    name_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[CommentResponse]]:
    service = CommentsService(db)
    comments = await service.list_comments_by_name(name_id)
    return wrap_success_response(comments, request, "Comments list retrieved.")

# --- Favorites Endpoints ---

@router.post("/names/{name_id}/favorite", response_model=StandardResponse[dict])
async def toggle_favorite(
    request: Request,
    name_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    service = FavoritesService(db)
    is_starred = await service.toggle_favorite(current_user.id, workspace_id, name_id)
    return wrap_success_response(
        {"name_id": name_id, "is_starred": is_starred},
        request,
        "Favorite state updated successfully."
    )

@router.get("/favorites", response_model=StandardResponse[List[FavoriteResponse]])
async def list_favorites(
    request: Request,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[FavoriteResponse]]:
    service = FavoritesService(db)
    favorites = await service.list_workspace_favorites(workspace_id, current_user.id)
    return wrap_success_response(favorites, request, "Starred names list retrieved.")

# --- Collections Endpoints ---

@router.post("/collections", response_model=StandardResponse[CollectionResponse], status_code=status.HTTP_201_CREATED)
async def create_collection(
    request: Request,
    workspace_id: uuid.UUID,
    payload: CollectionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[CollectionResponse]:
    service = CollectionsService(db)
    col = await service.create_collection(workspace_id, current_user.id, payload.name, payload.description)
    return wrap_success_response(col, request, "Collection folder created.")

@router.put("/collections/{collection_id}", response_model=StandardResponse[CollectionResponse])
async def update_collection(
    request: Request,
    collection_id: uuid.UUID,
    payload: CollectionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[CollectionResponse]:
    service = CollectionsService(db)
    col = await service.update_collection(collection_id, payload.name, payload.description)
    if not col:
        raise HTTPException(status_code=404, detail="Collection folder not found.")
    return wrap_success_response(col, request, "Collection folder updated.")

@router.delete("/collections/{collection_id}", response_model=StandardResponse[dict])
async def delete_collection(
    request: Request,
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    service = CollectionsService(db)
    success = await service.delete_collection(collection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Collection folder not found.")
    return wrap_success_response({"id": collection_id, "deleted": True}, request, "Collection folder deleted.")

@router.get("/collections", response_model=StandardResponse[List[CollectionResponse]])
async def list_collections(
    request: Request,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[CollectionResponse]]:
    service = CollectionsService(db)
    cols = await service.list_workspace_collections(workspace_id)
    return wrap_success_response(cols, request, "Collection folders lists retrieved.")

@router.post("/collections/{collection_id}/items", response_model=StandardResponse[CollectionItemResponse], status_code=status.HTTP_201_CREATED)
async def add_item_to_collection(
    request: Request,
    collection_id: uuid.UUID,
    name_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[CollectionItemResponse]:
    service = CollectionsService(db)
    item = await service.add_name_to_collection(collection_id, name_id)
    return wrap_success_response(item, request, "Item added to collection folder.")

@router.delete("/collections/{collection_id}/items/{name_id}", response_model=StandardResponse[dict])
async def remove_item_from_collection(
    request: Request,
    collection_id: uuid.UUID,
    name_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    service = CollectionsService(db)
    removed = await service.remove_name_from_collection(collection_id, name_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Item map reference not found in collection.")
    return wrap_success_response({"collection_id": collection_id, "name_id": name_id, "removed": True}, request, "Item removed.")

@router.get("/collections/{collection_id}/items", response_model=StandardResponse[List[CollectionItemResponse]])
async def list_collection_items(
    request: Request,
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[List[CollectionItemResponse]]:
    service = CollectionsService(db)
    items = await service.list_items_by_collection(collection_id)
    return wrap_success_response(items, request, "Collection items retrieved.")
