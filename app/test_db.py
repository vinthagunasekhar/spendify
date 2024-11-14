# app/test_db.py
import asyncio
from app.db.utils import test_connection

async def main():
    is_connected = await test_connection()
    if is_connected:
        print("✅ Successfully connected to the database!")
    else:
        print("❌ Failed to connect to the database!")

if __name__ == "__main__":
    asyncio.run(main())