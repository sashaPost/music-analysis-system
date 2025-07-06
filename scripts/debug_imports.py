"""Debug script to check import issues"""
import sys
import os
from pathlib import Path

def debug_imports() -> None:
    """Debug script to check import issues in the app directory."""
    print("=== Debug Information ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    
    # Check if app directory exists
    project_root = Path(__file__).parent.parent
    app_dir = project_root / "app"
    print(f"Project root: {project_root}")
    print(f"App directory exists: {app_dir.exists()}")
    
    if app_dir.exists():
        print(f"App directory contents: {list(app_dir.iterdir())}")
        
        # Check for __init__.py files
        init_files = [
            app_dir / "__init__.py",
            app_dir / "db" / "__init__.py",
            app_dir / "config.py",
            app_dir / "db" / "database.py"
        ]
        
        for file_path in init_files:
            print(f"{file_path.name} exists: {file_path.exists()}")
    
    # Try importing step by step
    sys.path.insert(0, str(project_root))
    
    try:
        print("\nTrying to import sqlalchemy...")
        from sqlalchemy import create_engine
        print("✓ SQLAlchemy import successful")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
    
    try:
        print("\nTrying to import app...")
        import app
        print("✓ App import successful")
    except ImportError as e:
        print(f"✗ App import failed: {e}")
    
    try:
        print("\nTrying to import app.config...")
        from app.config import settings
        print("✓ Config import successful")
        print(f"Database URL: {settings.database_url}")
    except ImportError as e:
        print(f"✗ Config import failed: {e}")
    
    try:
        print("\nTrying to import app.db.database...")
        from app.db.database import Base
        print("✓ Database import successful")
    except ImportError as e:
        print(f"✗ Database import failed: {e}")


if __name__ == "__main__":
    debug_imports()
