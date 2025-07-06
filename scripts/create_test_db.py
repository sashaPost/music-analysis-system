from dotenv import load_dotenv
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from urllib.parse import urlparse

load_dotenv(dotenv_path=Path(".env.dev"))


def create_test_db():
    test_db_url = os.getenv("DATABASE_URL", "")
    if not test_db_url:
        raise RuntimeError("DATABASE_URL is not set")

    parsed = urlparse(test_db_url)
    db_name = parsed.path.lstrip("/") + "_test"
    sync_url = test_db_url.replace("+asyncpg", "")  # strip async driver
    admin_url = sync_url.replace(f"/{parsed.path.lstrip('/')}", "/postgres")

    print(f"Connecting to: {admin_url}")
    print(f"Checking for test DB: {db_name}")

    conn = psycopg2.connect(admin_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if DB already exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    exists = cur.fetchone()

    if exists:
        print(f"✅ Test DB '{db_name}' already exists.")
    else:
        cur.execute(f'CREATE DATABASE "{db_name}"')
        print(f"✅ Created test DB: {db_name}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        create_test_db()
    except Exception as e:
        print(f"❌ Failed to create test database: {e}")
