import sqlite3

def check_and_fix():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    
    print("Checking 'customer' table...")
    cursor.execute("PRAGMA table_info(customer)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")

    if 'created_at' not in columns:
        print("Missing 'created_at'. Adding it...")
        try:
            cursor.execute("ALTER TABLE customer ADD COLUMN created_at DATETIME")
            print("Success.")
        except Exception as e:
            print(f"Error: {e}")
            
    if 'points' not in columns:
        print("Missing 'points'. Adding it...")
        try:
            cursor.execute("ALTER TABLE customer ADD COLUMN points INTEGER DEFAULT 0")
            print("Success.")
        except Exception as e:
            print(f"Error: {e}")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    check_and_fix()
