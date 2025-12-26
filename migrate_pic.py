from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text("ALTER TABLE store_config ADD COLUMN pic_name VARCHAR(100) DEFAULT 'Manager'"))
        conn.commit()
    print("Added pic_name column to store_config")
