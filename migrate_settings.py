from app import app, db
from models import StoreConfig

def migrate():
    with app.app_context():
        print("Migrating: Creating StoreConfig table...")
        db.create_all() # This creates any missing tables
        
        # Ensure default config exists
        if not StoreConfig.query.first():
            print("Creating default StoreConfig...")
            default_config = StoreConfig()
            db.session.add(default_config)
            db.session.commit()
            print("Default config created.")
        else:
            print("StoreConfig already exists.")

if __name__ == "__main__":
    migrate()
