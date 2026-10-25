from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid
import jwt
import hashlib
import secrets
from fastapi import File, UploadFile
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException, Depends, status, Form, File, UploadFile, Body

# Add these missing imports
from sqlalchemy.orm import Session
from src.core.database import get_db

# Import simple database
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.core.db_simple import init_db, get_user_by_email, get_user_by_phone, create_user,get_user_activities
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.core.db_simple import (
init_db,
    get_user_by_email,
    get_user_by_phone,
    get_user_by_id,
    create_user,
    create_loan_application,
    get_loan_applications_by_user,
    get_loan_application_by_id,
    update_loan_status,
    get_collateral_by_user,
    get_collateral_by_id,
    create_collateral,
    get_user_activities,
    create_verification_token,
    get_verification_token,
    delete_verification_token,
    verify_user_email)


app = FastAPI(
    title="MicroLend Botswana",
    description="Micro-lending platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def send_verification_email(email, token, first_name):
    """Send a verification email with the token."""
    verify_link = f"{FRONTEND_URL}/verify-email?token={token}"
    
    # If email credentials are not configured, just print the link to console
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print(f"🔗 Verification link (email not configured): {verify_link}")
        return True
    
    subject = "Verify your email - MicroLend"
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #2563eb;">Welcome to MicroLend, {first_name}!</h1>
        <p style="font-size: 16px; color: #333;">Thanks for signing up. Please verify your email address to get started.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verify_link}" style="background-color: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold;">Verify Email</a>
        </div>
        <p style="font-size: 14px; color: #666;">Or copy this link into your browser:</p>
        <p style="font-size: 14px; word-break: break-all; background: #f3f4f6; padding: 10px; border-radius: 4px;">{verify_link}</p>
        <p style="font-size: 14px; color: #999;">This link expires in 24 hours.</p>
        <p style="font-size: 14px; color: #999;">If you didn't sign up, please ignore this email.</p>
    </body>
    </html>
    """
    text = f"Welcome to MicroLend! Verify your email: {verify_link}"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = email
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, [email], msg.as_string())
        server.quit()
        print(f"✅ Verification email sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        print(f"🔗 Verification link (fallback): {verify_link}")
        return True  # Return True so registration continues
security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Get current user ID from JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Models
class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    phone: str
    first_name: str
    last_name: str
    created_at: Optional[str] = None

# Simple password hashing with SHA256
def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt."""
    salt = secrets.token_hex(16)
    combined = salt + password
    hash_value = hashlib.sha256(combined.encode()).hexdigest()
    result = f"{salt}:{hash_value}"
    print(f"🔐 Password hashed: {result[:20]}...")
    return result

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        print(f"🔐 Verifying password...")
        print(f"   Plain: {plain_password}")
        print(f"   Hash: {hashed_password[:20]}...")
        
        # Split the stored hash
        parts = hashed_password.split(":")
        if len(parts) != 2:
            print(f"❌ Invalid hash format: {hashed_password}")
            return False
            
        salt, stored_hash = parts
        print(f"   Salt: {salt[:10]}...")
        
        # Compute hash with the same salt
        combined = salt + plain_password
        computed_hash = hashlib.sha256(combined.encode()).hexdigest()
        print(f"   Computed: {computed_hash[:20]}...")
        print(f"   Stored: {stored_hash[:20]}...")
        
        result = computed_hash == stored_hash
        print(f"   Match: {result}")
        return result
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    print("🚀 Starting application...")
    try:
        init_db()
        print("✅ Application started successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Registration
@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    try:
        print(f"📝 Registering user: {user_data.email}")
        
        # Check if user exists (existing code)
        existing = get_user_by_email(user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        existing_phone = get_user_by_phone(user_data.phone)
        if existing_phone:
            raise HTTPException(status_code=400, detail="User with this phone number already exists")
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user with is_email_verified = 0
        user_id = create_user(
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        # Generate verification token (valid 24h)
        token = secrets.token_urlsafe(32)
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        create_verification_token(user_id, token, expires_at)
        
        # Send verification email
        email_sent = send_verification_email(user_data.email, token, user_data.first_name)
        
        print(f"✅ User registered: {user_data.email} (ID: {user_id})")
        
        return {
            "id": user_id,
            "email": user_data.email,
            "phone": user_data.phone,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "created_at": datetime.now().isoformat(),
            "requires_verification": True,
            "email_sent": email_sent
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/v1/auth/login")
async def login(credentials: UserLogin):
    try:
        print(f"📝 Login attempt: {credentials.email}")
        
        user = get_user_by_email(credentials.email)
        if not user:
            print("❌ User not found")
            raise HTTPException(401, detail="Invalid credentials")
        
        # Ensure user is a dict
        if not isinstance(user, dict):
            print(f"⚠️ User is not a dict: {type(user)}")
            user = dict(user)
        
        print(f"✅ User found: {user.get('email')}")
        
        # Verify password
        try:
            password_valid = verify_password(credentials.password, user.get("password_hash", ""))
        except Exception as e:
            print(f"❌ Password verification error: {e}")
            raise HTTPException(500, detail="Password verification error")
        
        if not password_valid:
            print("❌ Invalid password")
            raise HTTPException(401, detail="Invalid credentials")
        
        if not user.get("is_active", 1):
            print("❌ Account deactivated")
            raise HTTPException(403, detail="Account deactivated")
        
        # Generate token
        try:
            token = jwt.encode(
                {"sub": user["id"], "email": user["email"]},
                "your-secret-key",
                algorithm="HS256"
            )
        except Exception as e:
            print(f"❌ Token generation error: {e}")
            raise HTTPException(500, detail="Token generation failed")
        
        print(f"✅ User logged in: {user['email']}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "firstName": user["first_name"],
                "lastName": user["last_name"],
                "phone": user["phone"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, detail=f"Login failed: {str(e)}")
        
@app.get("/api/v1/auth/verify-email")
async def verify_email(token: str):
    """Verify user's email using the token."""
    row = get_verification_token(token)
    if not row:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    user_id = row["user_id"]
    verify_user_email(user_id)
    delete_verification_token(token)
    
    print(f"✅ Email verified for user: {user_id}")
    return {"message": "Email verified successfully. You can now login."}
# Get current user (mock for now)
@app.get("/api/v1/users/me")
async def get_current_user():
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "phone": "+26712345678",
        "first_name": "John",
        "last_name": "Doe",
        "is_verified": True,
        "kyc_status": "verified"
    }

# Collateral endpoints
class CollateralCreate(BaseModel):
    item_type: str
    brand: Optional[str] = None
    model: Optional[str] = None
    estimated_value: float

# Add these imports at the top
from fastapi import File, UploadFile
from typing import List

@app.post("/api/v1/auth/resend-verification")
async def resend_verification(email: str = Body(..., embed=True)):
    """Resend verification email to the user."""
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["is_email_verified"]:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Delete old tokens and create new
    # We'll just create a new one; old ones will expire anyway
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
    create_verification_token(user["id"], token, expires_at)
    
    sent = send_verification_email(email, token, user["first_name"])
    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    return {"message": "Verification email resent. Please check your inbox."}

@app.post("/api/v1/collateral")
async def create_collateral(
    item_type: str = Form(...),
    brand: str = Form(None),
    model: str = Form(None),
    estimated_value: float = Form(...),
    condition: str = Form("good"),
    description: str = Form(""),
    photos: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Create a new collateral item with photo uploads."""
    try:
        print(f"📝 Creating collateral for user: {user_id}")
        print(f"   Type: {item_type}, Brand: {brand}, Model: {model}")
        
        # Validate photos
        if len(photos) < 2:
            raise HTTPException(
                status_code=400,
                detail="Please upload at least 2 photos"
            )
        
        # Save photos (for now, we'll store as base64 or save to disk)
        # In production, upload to S3 or cloud storage
        # For development, we'll save to a local folder
        import os
        import shutil
        from datetime import datetime
        
        upload_dir = os.path.join("uploads", "collateral", user_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        saved_images = []
        for photo in photos[:2]:  # Only save first 2
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{photo.filename}"
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            
            # Store relative path
            saved_images.append(f"/uploads/collateral/{user_id}/{filename}")
        
        # Create collateral in database
        collateral_id = create_collateral(
            user_id=user_id,
            item_type=item_type,
            brand=brand,
            model=model,
            estimated_value=estimated_value,
            condition=condition,
            description=description,
            images=saved_images
        )
        
        print(f"✅ Collateral created: {collateral_id}")
        
        return {
            "id": collateral_id,
            "user_id": user_id,
            "item_type": item_type,
            "brand": brand,
            "model": model,
            "estimated_value": estimated_value,
            "condition": condition,
            "description": description,
            "images": saved_images,
            "status": "pending_verification",
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Collateral creation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create collateral: {str(e)}"
        )

@app.get("/api/v1/collateral")
async def list_collateral():
    return [
        {
            "id": str(uuid.uuid4()),
            "item_type": "phone",
            "brand": "Samsung",
            "model": "Galaxy S23",
            "estimated_value": 8000,
            "is_verified": True
        },
        {
            "id": str(uuid.uuid4()),
            "item_type": "laptop",
            "brand": "Dell",
            "model": "XPS 15",
            "estimated_value": 15000,
            "is_verified": False
        }
    ]

# Loan endpoints
class LoanCreate(BaseModel):
    amount: float
    term_months: int
    collateral_id: Optional[str] = None
    purpose: Optional[str] = None

from src.core.db_simple import (
    init_db, get_user_by_email, get_user_by_phone, create_user,
    create_loan_application, get_loan_applications_by_user,
    get_loan_application_by_id, update_loan_status,
    get_collateral_by_user, get_collateral_by_id
)

# app.py - Replace loan endpoints with these

# Import additional functions from db_simple
from src.core.db_simple import (
    init_db, get_user_by_email, get_user_by_phone, create_user,
    create_loan_application, get_loan_applications_by_user,
    get_loan_application_by_id, update_loan_status,
    get_collateral_by_user, get_collateral_by_id
)

# Update the create loan endpoint
@app.post("/api/v1/loans/applications")
async def create_loan_application_endpoint(
    loan_data: LoanCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new loan application - REAL DATABASE."""
    try:
        print(f"📝 New loan application for user: {user_id}")
        print(f"   Amount: P{loan_data.amount}")
        print(f"   Term: {loan_data.term_months} months")
        
        # Validate user exists
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        # Create loan in database
        loan_id = create_loan_application(
            user_id=user_id,
            amount=loan_data.amount,
            term_months=loan_data.term_months,
            purpose=loan_data.purpose,
            collateral_id=loan_data.collateral_id
        )
        
        # Get the created loan
        loan = get_loan_application_by_id(loan_id)
        
        print(f"✅ Loan application created: {loan_id}")
        
        return {
            "id": loan["id"],
            "user_id": loan["user_id"],
            "amount": loan["amount"],
            "interest_rate": loan["interest_rate"],
            "term_months": loan["term_months"],
            "monthly_installment": loan["monthly_installment"],
            "total_repayment": loan["total_repayment"],
            "purpose": loan["purpose"],
            "status": loan["status"],
            "created_at": loan["created_at"]
        }
        
    except Exception as e:
        print(f"❌ Loan application error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create loan application: {str(e)}"
        )

# Get user's loans
@app.get("/api/v1/loans/applications")
async def get_user_loans(
    user_id: str = Depends(get_current_user_id)
):
    """Get all loan applications for the current user - REAL DATABASE."""
    try:
        print(f"📝 Fetching loans for user: {user_id}")
        
        loans = get_loan_applications_by_user(user_id)
        
        result = []
        for loan in loans:
            result.append({
                "id": loan["id"],
                "amount": loan["amount"],
                "interest_rate": loan["interest_rate"],
                "term_months": loan["term_months"],
                "monthly_installment": loan["monthly_installment"],
                "total_repayment": loan["total_repayment"],
                "purpose": loan["purpose"],
                "status": loan["status"],
                "created_at": loan["created_at"]
            })
        
        print(f"✅ Found {len(result)} loans")
        return result
        
    except Exception as e:
        print(f"❌ Error fetching loans: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch loans: {str(e)}"
        )

# Get single loan by ID
@app.get("/api/v1/loans/applications/{loan_id}")
async def get_loan_details(
    loan_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific loan application with full details - REAL DATABASE."""
    try:
        print(f"📝 Fetching loan details for ID: {loan_id}")
        
        # Get the loan
        loan = get_loan_application_by_id(loan_id)
        if not loan:
            raise HTTPException(
                status_code=404,
                detail="Loan not found"
            )
        
        # Verify ownership
        if loan["user_id"] != user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to view this loan"
            )
        
        # Get collateral if exists
        collateral_info = None
        if loan["collateral_id"]:
            collateral = get_collateral_by_id(loan["collateral_id"])
            if collateral:
                collateral_info = {
                    "id": collateral["id"],
                    "item_type": collateral["item_type"],
                    "brand": collateral["brand"],
                    "model": collateral["model"],
                    "estimated_value": collateral["estimated_value"],
                    "condition": collateral["condition"],
                    "is_verified": bool(collateral["is_verified"])
                }
        
        # Get repayments (mock for now - will be implemented later)
        repayments = [
            {"id": "rep-1", "due_date": "2024-02-20", "amount": loan["monthly_installment"], "status": "pending", "paid_date": None},
            {"id": "rep-2", "due_date": "2024-03-20", "amount": loan["monthly_installment"], "status": "pending", "paid_date": None},
            {"id": "rep-3", "due_date": "2024-04-20", "amount": loan["monthly_installment"], "status": "pending", "paid_date": None},
            {"id": "rep-4", "due_date": "2024-05-20", "amount": loan["monthly_installment"], "status": "pending", "paid_date": None},
            {"id": "rep-5", "due_date": "2024-06-20", "amount": loan["monthly_installment"], "status": "pending", "paid_date": None},
            {"id": "rep-6", "due_date": "2024-07-20", "amount": loan["monthly_installment"], "status": "pending", "paid_date": None},
        ]
        
        # Calculate totals
        total_interest = loan["total_repayment"] - loan["amount"]
        
        # Generate contract number
        contract_number = f"ML-{loan['created_at'][:7].replace('-', '')}-{loan['id'][:6].upper()}"
        
        return {
            "id": loan["id"],
            "contract_number": contract_number,
            "amount": loan["amount"],
            "interest_rate": loan["interest_rate"],
            "term_months": loan["term_months"],
            "monthly_installment": loan["monthly_installment"],
            "total_repayment": loan["total_repayment"],
            "total_interest": round(total_interest, 2),
            "purpose": loan["purpose"],
            "status": loan["status"],
            "created_at": loan["created_at"],
            "approved_date": loan.get("approval_date"),
            "disbursement_date": None,  # Will be updated later
            "start_date": loan["created_at"][:10] if loan["created_at"] else None,
            "end_date": None,  # Will be calculated
            "next_payment_date": None,  # Will be calculated
            "collateral": collateral_info,
            "repayments": repayments
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching loan: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch loan details: {str(e)}"
        )

@app.get("/api/v1/users/activities")
async def get_user_activities_endpoint(
    user_id: str = Depends(get_current_user_id)
):
    """Get all activities for the current user."""
    try:
        activities = get_user_activities(user_id)
        return activities
    except Exception as e:
        print(f"❌ Error fetching activities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch activities"
        )

# Get user's collateral
@app.get("/api/v1/collateral")
async def get_user_collateral(
    user_id: str = Depends(get_current_user_id)
):
    """Get all collateral items for the current user - REAL DATABASE."""
    try:
        print(f"📝 Fetching collateral for user: {user_id}")
        
        items = get_collateral_by_user(user_id)
        
        result = []
        for item in items:
            result.append({
                "id": item["id"],
                "item_type": item["item_type"],
                "brand": item["brand"],
                "model": item["model"],
                "estimated_value": item["estimated_value"],
                "condition": item["condition"],
                "is_verified": bool(item["is_verified"]),
                "is_encumbered": bool(item["is_encumbered"]),
                "created_at": item["created_at"]
            })
        
        return result
        
    except Exception as e:
        print(f"❌ Error fetching collateral: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch collateral: {str(e)}"
        )
