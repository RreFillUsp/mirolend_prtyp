# scripts/init_db.py
import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.database import init_db, create_tables
from src.core.config import settings


async def main():
    print("=" * 60)
    print("🚀 Initializing Database...")
    print("=" * 60)
    print(f"📁 Database URL: {settings.DATABASE_URL}")
    print(f"📁 Project Root: {project_root}")
    print("")
    
    try:
        # Create tables
        create_tables()
        
        print("✅ Database initialized successfully!")
        print(f"📁 Database file: {project_root}/microlend.db")
        print("")
        print("Next steps:")
        print("1. Run the backend: uvicorn app:app --reload")
        print("2. Seed data: python scripts/seed_data.py")
        print("3. Access API docs: http://localhost:8000/docs")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())