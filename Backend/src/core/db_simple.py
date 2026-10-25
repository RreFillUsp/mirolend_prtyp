import sqlite3
import uuid
from datetime import datetime
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "microlend.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print("📁 Creating database at:", DB_PATH)
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            national_id TEXT UNIQUE,
            date_of_birth TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            employment_status TEXT,
            employer TEXT,
            monthly_income REAL,
            credit_score INTEGER DEFAULT 500,
            is_verified INTEGER DEFAULT 0,
            is_email_verified INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0,
            kyc_status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add is_email_verified column if missing (for existing DBs)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_email_verified INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # Collateral items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collateral_items (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            brand TEXT,
            model TEXT,
            serial_number TEXT UNIQUE,
            imei TEXT UNIQUE,
            estimated_value REAL NOT NULL,
            condition TEXT DEFAULT 'good',
            description TEXT,
            images TEXT,
            registry_reference TEXT,
            security_interest_registered INTEGER DEFAULT 0,
            is_encumbered INTEGER DEFAULT 0,
            is_verified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Loan applications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loan_applications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            collateral_id TEXT,
            amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            term_months INTEGER NOT NULL,
            monthly_installment REAL,
            total_repayment REAL,
            purpose TEXT,
            status TEXT DEFAULT 'pending',
            approved_by TEXT,
            approval_date TEXT,
            approval_notes TEXT,
            disbursement_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (collateral_id) REFERENCES collateral_items (id)
        )
    """)

    # Verification tokens table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verification_tokens (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")
    return True

# ---------- USER ----------
def get_user_by_email(email):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    if row is None:
        return None
    # Convert to dict
    return dict(row)
def get_user_by_phone(phone):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(email, phone, password_hash, first_name, last_name):
    user_id = str(uuid.uuid4())
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (
            id, email, phone, password_hash, first_name, last_name,
            is_verified, is_active, is_admin, kyc_status, credit_score, is_email_verified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, email, phone, password_hash, first_name, last_name,
        0, 1, 0, "pending", 500, 0
    ))
    conn.commit()
    conn.close()
    return user_id

# ---------- LOANS ----------
def create_loan_application(user_id, amount, term_months, purpose, collateral_id=None):
    loan_id = str(uuid.uuid4())
    conn = get_connection()
    c = conn.cursor()
    monthly_rate = 0.20
    total_interest = amount * monthly_rate * term_months
    total_repayment = amount + total_interest
    monthly_payment = total_repayment / term_months
    c.execute("""
        INSERT INTO loan_applications (
            id, user_id, collateral_id, amount, interest_rate, term_months,
            monthly_installment, total_repayment, purpose, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        loan_id, user_id, collateral_id, amount, 20.0, term_months,
        round(monthly_payment, 2), round(total_repayment, 2), purpose,
        'pending', datetime.now().isoformat(), datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return loan_id

def get_loan_applications_by_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM loan_applications WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    loans = c.fetchall()
    conn.close()
    return loans

def get_loan_application_by_id(loan_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM loan_applications WHERE id = ?", (loan_id,))
    loan = c.fetchone()
    conn.close()
    return loan

def update_loan_status(loan_id, status, approved_by=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE loan_applications
        SET status = ?, approved_by = ?, approval_date = ?, updated_at = ?
        WHERE id = ?
    """, (status, approved_by, datetime.now().isoformat(), datetime.now().isoformat(), loan_id))
    conn.commit()
    conn.close()
    return True

# ---------- COLLATERAL ----------
def create_collateral(user_id, item_type, brand, model, estimated_value, condition='good', description='', images=None):
    item_id = str(uuid.uuid4())
    conn = get_connection()
    c = conn.cursor()
    images_json = json.dumps(images or [])
    c.execute("""
        INSERT INTO collateral_items (
            id, user_id, item_type, brand, model, estimated_value,
            condition, description, images, is_verified, is_encumbered
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_id, user_id, item_type, brand, model, estimated_value,
        condition, description, images_json, 0, 0
    ))
    conn.commit()
    conn.close()
    return item_id

def get_collateral_by_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM collateral_items WHERE user_id = ?", (user_id,))
    items = c.fetchall()
    conn.close()
    return items

def get_collateral_by_id(collateral_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM collateral_items WHERE id = ?", (collateral_id,))
    item = c.fetchone()
    conn.close()
    return item

# ---------- VERIFICATION TOKENS ----------
def create_verification_token(user_id, token, expires_at):
    """Store a verification token with expiration."""
    conn = get_connection()
    c = conn.cursor()
    # expires_at should be in SQLite-friendly format: "YYYY-MM-DD HH:MM:SS"
    c.execute("""
        INSERT INTO verification_tokens (id, user_id, token, expires_at)
        VALUES (?, ?, ?, ?)
    """, (str(uuid.uuid4()), user_id, token, expires_at))
    conn.commit()
    conn.close()

def get_verification_token(token):
    """Get a valid (non-expired) verification token."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM verification_tokens 
        WHERE token = ? AND expires_at > datetime('now')
    """, (token,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_verification_token(token):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM verification_tokens WHERE token = ?", (token,))
    conn.commit()
    conn.close()

def verify_user_email(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_email_verified = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# ---------- ACTIVITIES ----------
def get_user_activities(user_id):
    conn = get_connection()
    c = conn.cursor()
    activities = []

    try:
        c.execute("SELECT created_at FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if user:
            activities.append({
                "type": "registration",
                "title": "Account Created",
                "description": "You joined MicroLend",
                "timestamp": user["created_at"],
                "icon": "user-plus"
            })
    except:
        pass

    try:
        c.execute("""
            SELECT id, amount, status, created_at, approval_date, disbursement_date
            FROM loan_applications
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        loans = c.fetchall()
        for loan in loans:
            activities.append({
                "type": "loan_application",
                "title": f"Loan Application of P{loan['amount']:,.2f}",
                "description": f"Status: {loan['status'].title()}",
                "timestamp": loan['created_at'],
                "loan_id": loan['id'],
                "icon": "file-text"
            })
            if loan['status'].lower() == 'approved' and loan.get('approval_date'):
                activities.append({
                    "type": "loan_approved",
                    "title": f"Loan Approved: P{loan['amount']:,.2f}",
                    "description": "Your loan was approved!",
                    "timestamp": loan['approval_date'],
                    "loan_id": loan['id'],
                    "icon": "check-circle"
                })
            if loan['status'].lower() == 'disbursed' and loan.get('disbursement_date'):
                activities.append({
                    "type": "loan_disbursed",
                    "title": f"Funds Disbursed: P{loan['amount']:,.2f}",
                    "description": "Money has been sent to your account.",
                    "timestamp": loan['disbursement_date'],
                    "loan_id": loan['id'],
                    "icon": "credit-card"
                })
    except:
        pass

    conn.close()
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return activities

def dict_from_row(row):
    if row is None:
        return None
    return dict(row)