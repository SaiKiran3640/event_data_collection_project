from database.db_config import SessionLocal
from sqlalchemy import text  # ✅ Add this import

def test_connection():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # ✅ Correct usage
        print("✅ Successfully connected to the MySQL database!")
    except Exception as e:
        print("❌ Connection failed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
