import sqlite3

def force_add_columns():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    
    # Check what columns exist
    cursor.execute("PRAGMA table_info(customer)")
    print("Initial Columns:", [r[1] for r in cursor.fetchall()])

    # Try adding total_debt if missing
    try:
        cursor.execute("ALTER TABLE customer ADD COLUMN total_debt FLOAT DEFAULT 0.0")
        print("Success: Added total_debt")
    except sqlite3.OperationalError as e:
        print(f"Error adding total_debt: {e}")
        
    try:
        cursor.execute("ALTER TABLE customer ADD COLUMN created_at DATETIME")
        print("Success: Added created_at")
    except sqlite3.OperationalError as e:
        print(f"Error adding created_at: {e}")

    try:
        cursor.execute("ALTER TABLE customer ADD COLUMN points INTEGER DEFAULT 0")
        print("Success: Added points")
    except sqlite3.OperationalError as e:
        print(f"Error adding points: {e}")

    # Verify
    cursor.execute("PRAGMA table_info(customer)")
    print("Final Columns:", [r[1] for r in cursor.fetchall()])
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    force_add_columns()
