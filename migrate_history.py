from app import app, db
from models import StockHistory

def migrate():
    with app.app_context():
        print("Migrating: Creating stock_history table...")
        try:
            db.create_all() # This will create any missing tables, including stock_history
            print("Migration successful: stock_history table created.")
        except Exception as e:
            print(f"Error migrating: {e}")

if __name__ == "__main__":
    migrate()
