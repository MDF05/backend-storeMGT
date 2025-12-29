import os
import shutil
from app import app, db


def reset_database():
    print("*** RESET DATABASE: Remove migrations and recreate schema ***")
    print("This will DROP ALL DATA and REMOVE migration history in the 'migrations/' folder.")
    confirm = input("Type 'RESET' to proceed: ")
    if confirm != 'RESET':
        print('Aborted by user.')
        return

    # Remove migrations folder if exists
    migrations_path = os.path.join(os.path.dirname(__file__), 'migrations')
    if os.path.isdir(migrations_path):
        try:
            shutil.rmtree(migrations_path)
            print(f'Removed migrations folder: {migrations_path}')
        except Exception as e:
            print(f'Failed to remove migrations folder: {e}')
    else:
        print('No migrations folder found; skipping removal.')

    # Drop and recreate all tables
    with app.app_context():
        try:
            db.drop_all()
            print('Dropped all tables.')
        except Exception as e:
            print('Error while dropping tables:', e)

        try:
            db.create_all()
            print('Created tables from models.')
        except Exception as e:
            print('Error while creating tables:', e)

    print('Reset complete. You can now (optionally) run `flask db init` and create new migrations.')


if __name__ == '__main__':
    reset_database()
