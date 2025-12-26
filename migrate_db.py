from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        print("Migrating: Adding low_stock_threshold to product table...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE product ADD COLUMN low_stock_threshold INTEGER DEFAULT 10"))
                conn.commit()
            print("Migration successful: Added low_stock_threshold column.")
        except Exception as e:
            if "duplicate column name" in str(e) or "already exists" in str(e):
                print("Column already exists. Skipping.")
            else:
                print(f"Error migrating: {e}")

if __name__ == "__main__":
    migrate()
