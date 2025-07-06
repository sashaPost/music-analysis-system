# from pathlib import Path
from dotenv import dotenv_values


required_keys = dotenv_values(".env")
example_keys = dotenv_values(".env.example")

missing = [key for key in required_keys if key not in example_keys]
extra = [key for key in example_keys if key not in required_keys]

if missing:
    print("❌ Missing keys in .env.example:", missing)
if extra:
    print("⚠️  Extra keys in .env.example:", extra)

if not missing and not extra:
    print("✅ .env.example is in sync with .env")
