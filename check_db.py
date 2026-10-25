# check_db.py - View database contents
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "microlend.db")

def check_database():
    """Check and display database contents."""
    print("=" * 60)
    print("📁 Database Viewer")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print("")
    
    if not os.path.exists(DB_PATH):
        print("❌ Database file not found!")
        print("Please run: python setup_db.py first")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("📋 Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    print("")
    
    # Check users table
    try:
        cursor.execute("SELECT id, email, phone, first_name, last_name, created_at FROM users;")
        users = cursor.fetchall()
        print(f"👥 Users ({len(users)}):")
        if users:
            for user in users:
                print(f"  - {user[1]} | {user[2]} | {user[3]} {user[4]} | {user[5]}")
        else:
            print("  (No users found)")
    except sqlite3.OperationalError as e:
        print(f"❌ Users table error: {e}")
    print("")
    
    # Check collateral items
    try:
        cursor.execute("SELECT id, user_id, item_type, brand, model, estimated_value FROM collateral_items;")
        items = cursor.fetchall()
        print(f"📱 Collateral Items ({len(items)}):")
        if items:
            for item in items:
                print(f"  - {item[2]} {item[3]} {item[4]} | P{item[5]} | User: {item[1][:8]}...")
        else:
            print("  (No collateral items found)")
    except sqlite3.OperationalError as e:
        print(f"❌ Collateral table error: {e}")
    print("")
    
    # Check loan applications
    try:
        cursor.execute("SELECT id, user_id, amount, status, created_at FROM loan_applications;")
        loans = cursor.fetchall()
        print(f"💰 Loan Applications ({len(loans)}):")
        if loans:
            for loan in loans:
                print(f"  - P{loan[2]} | {loan[3]} | {loan[4]}")
        else:
            print("  (No loan applications found)")
    except sqlite3.OperationalError as e:
        print(f"❌ Loan table error: {e}")
    
    conn.close()
    print("")
    print("=" * 60)

def delete_user(email):
    """Delete a specific user by email."""
    if not email:
        print("❌ Please provide an email")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT email, first_name, last_name FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ User not found: {email}")
        conn.close()
        return
    
    print(f"🗑️ Deleting user: {user[0]} ({user[1]} {user[2]})")
    confirm = input("Are you sure? (y/n): ")
    
    if confirm.lower() == 'y':
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        print("✅ User deleted successfully!")
    else:
        print("❌ Cancelled")
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "delete" and len(sys.argv) > 2:
            delete_user(sys.argv[2])
        else:
            print("Usage:")
            print("  python check_db.py              - View all data")
            print("  python check_db.py delete EMAIL - Delete a user")
    else:
        check_database()