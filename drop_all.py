from app import app, db
import os
import sys

def drop_everything():
    with app.app_context():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        print("Detected SQLALCHEMY_DATABASE_URI:", uri)
        print("WARNING: This will DROP ALL TABLES in the configured database.")
        confirm = input("Type 'YES' to continue: ")
        if confirm != 'YES':
            print('Aborted by user.')
            return

        try:
            db.drop_all()
            print('All tables dropped via SQLAlchemy (db.drop_all()).')

            # If using a local SQLite file, offer to delete it as well
            if uri and uri.startswith('sqlite:///'):
                db_path = uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    delete = input(f"Detected SQLite file at '{db_path}'. Type 'DELETE' to remove the file: ")
                    if delete == 'DELETE':
                        try:
                            os.remove(db_path)
                            print(f"Deleted SQLite file: {db_path}")
                        except Exception as e:
                            print(f"Failed to delete SQLite file: {e}")
                else:
                    print(f"SQLite path {db_path} does not exist on disk.")

            print('Done.')
        except Exception as e:
            print('Error during drop_all:', e)

if __name__ == '__main__':
    drop_everything()
