"""Database setup script"""
import sys
# import os
from pathlib import Path
import asyncio

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.db.database import Base
from app.config import settings


async def run_create() -> None:
    engine: AsyncEngine = create_async_engine(
        str(settings.database_url), 
        echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("✅ Database tables created successfully.")


if __name__ == "__main__":
    try:
        asyncio.run(run_create())
        print("✅ Database setup complete.")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")


# def create_tables() -> None:
#     """Create all database tables"""
#     engine = create_async_engine(str(settings.database_url), echo=True)
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     await engine.dispose()
#     print("✅ Database tables created successfully.")


# def main() -> None:
#     asyncio.run(create_tables())


# if __name__ == "__main__":
#     try:
#         main()
#         print("✅ Database setup complete.")
#     except Exception as e:
#         print(f"❌ Database setup failed: {e}")
