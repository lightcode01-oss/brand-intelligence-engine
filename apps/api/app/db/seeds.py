import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.future import select
from app.core.database import async_session_maker
from app.models.user import User, Subscription, FeatureFlag
from app.models.workspace import Workspace, WorkspaceMember

async def seed_database() -> None:
    print("🌱 Starting database seeding...")
    async with async_session_maker() as session:
        async with session.begin():
            # 1. Seed default user roles/accounts if empty
            user_exists = (await session.execute(select(User).filter_by(email="admin@nomen.ai"))).scalar()
            if not user_exists:
                admin_user = User(
                    email="admin@nomen.ai",
                    password_hash="argon2id_hashed_password_placeholder_change_me",
                    role="ADMIN",
                    status="ACTIVE"
                )
                session.add(admin_user)
                await session.flush() # Flush to populate ID
                
                # Link Subscription
                admin_sub = Subscription(
                    user_id=admin_user.id,
                    tier="FREE",
                    status="ACTIVE",
                    limit_reset_at=datetime.now(timezone.utc) + timedelta(days=30),
                    monthly_query_count=0
                )
                session.add(admin_sub)
                
                # Link Default Workspace
                default_ws = Workspace(
                    slug="default-workspace",
                    display_name="Default Workspace"
                )
                session.add(default_ws)
                await session.flush()
                
                # Link Membership
                membership = WorkspaceMember(
                    workspace_id=default_ws.id,
                    user_id=admin_user.id,
                    role="owner"
                )
                session.add(membership)
                print("   - Seeding admin, subscription, default workspace complete.")
            else:
                print("   - Admin user already exists. Seeding skipped.")

            # 2. Seed initial Feature Flags
            flags = [
                {"name": "ai-search-generation", "is_enabled": True, "description": "Enables LLM name generation pipeline."},
                {"name": "uspto-trademark-clearance", "is_enabled": False, "description": "Enables live TSDR scraping checks."},
                {"name": "premium-export-downloads", "is_enabled": True, "description": "Enables zipped vector packages compilation."}
            ]
            
            for flag_data in flags:
                flag_exists = (await session.execute(select(FeatureFlag).filter_by(name=flag_data["name"]))).scalar()
                if not flag_exists:
                    new_flag = FeatureFlag(**flag_data)
                    session.add(new_flag)
                    print(f"   - Seeding feature flag '{flag_data['name']}' complete.")
                else:
                    print(f"   - Feature flag '{flag_data['name']}' already exists. Seeding skipped.")
                    
    print("✅ Database seeding successfully resolved.")

if __name__ == "__main__":
    asyncio.run(seed_database())
