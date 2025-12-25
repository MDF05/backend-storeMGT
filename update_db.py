import sqlite3
import os

def upgrade_db():
    db_path = 'store.db'
    if not os.path.exists(db_path):
        print("store.db not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Checking schema for 'customer'...")
    cursor.execute("PRAGMA table_info(customer)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns: {columns}")

    if 'total_debt' not in columns:
        try:
            cursor.execute("ALTER TABLE customer ADD COLUMN total_debt FLOAT DEFAULT 0.0")
            print("Added total_debt to customer")
        except Exception as e:
            print(f"Error adding total_debt: {e}")
    else:
        print("total_debt already exists.")

    print("Checking schema for 'transaction'...")
    cursor.execute("PRAGMA table_info(`transaction`)")
    t_columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns: {t_columns}")

    if 'paid_amount' not in t_columns:
        try:
            cursor.execute("ALTER TABLE `transaction` ADD COLUMN paid_amount FLOAT DEFAULT 0.0")
            print("Added paid_amount to transaction")
        except Exception as e:
            print(f"Error adding paid_amount: {e}")
    
    if 'payment_method' not in t_columns:
        try:
            cursor.execute("ALTER TABLE `transaction` ADD COLUMN payment_method VARCHAR(50) DEFAULT 'cash'")
            print("Added payment_method to transaction")
        except Exception as e:
            print(f"Error adding payment_method: {e}")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    upgrade_db()
