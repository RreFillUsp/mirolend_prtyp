# scripts/seed_data.py
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.database import get_db_context
from src.core.security import get_password_hash
from src.models.user import User
from src.models.collateral import CollateralItem
from src.models.loan import LoanApplication, LoanContract, Repayment


async def seed_database():
    """Seed database with sample data."""
    print("=" * 60)
    print("🌱 Seeding database with sample data...")
    print("=" * 60)
    
    try:
        async with get_db_context() as db:
            # Create admin user
            admin = User(
                id=uuid.uuid4(),
                email="admin@microlend.co.bw",
                phone="+26771234567",
                password_hash=get_password_hash("Admin123!"),
                first_name="Admin",
                last_name="User",
                is_verified=True,
                is_active=True,
                is_admin=True,
                kyc_status="verified",
                credit_score=800,
            )
            db.add(admin)
            print("✅ Admin user created")
            
            # Create regular users
            users = []
            for i in range(1, 4):
                user = User(
                    id=uuid.uuid4(),
                    email=f"user{i}@example.com",
                    phone=f"+26771{i}23456",
                    password_hash=get_password_hash("Test123!"),
                    first_name=f"Test{i}",
                    last_name=f"User{i}",
                    is_verified=True,
                    is_active=True,
                    is_admin=False,
                    kyc_status="verified",
                    credit_score=600 + i * 50,
                    monthly_income=5000 + i * 2000,
                    employment_status="employed",
                    employer=f"Company {i}",
                )
                db.add(user)
                users.append(user)
                print(f"✅ User{i} created: user{i}@example.com / Test123!")
            
            await db.commit()
            await db.refresh(admin)
            for user in users:
                await db.refresh(user)
            
            # Create collateral items for users
            collateral_items = []
            for i, user in enumerate(users):
                collateral = CollateralItem(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    item_type="phone" if i % 2 == 0 else "laptop",
                    brand="Samsung" if i % 2 == 0 else "Apple",
                    model="Galaxy S23" if i % 2 == 0 else "MacBook Pro",
                    estimated_value=5000 + i * 2000,
                    condition="good",
                    is_verified=True,
                    is_encumbered=False,
                )
                db.add(collateral)
                collateral_items.append(collateral)
                print(f"✅ Collateral added for User{i+1}: {collateral.brand} {collateral.model}")
            
            await db.commit()
            
            # Create loan applications
            for i, user in enumerate(users):
                application = LoanApplication(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    collateral_id=collateral_items[i].id if i < len(collateral_items) else None,
                    amount=2000 + i * 1500,
                    interest_rate=15.0,
                    term_months=6,
                    monthly_installment=350 + i * 250,
                    total_repayment=2100 + i * 1500,
                    status="approved" if i % 2 == 0 else "pending",
                    purpose="Buy electronics" if i % 2 == 0 else "School fees",
                    created_at=datetime.now() - timedelta(days=i * 5),
                )
                db.add(application)
                print(f"✅ Loan application created for User{i+1}: P{application.amount}")
                
                # Create contract for approved applications
                if i % 2 == 0:
                    contract = LoanContract(
                        id=uuid.uuid4(),
                        application_id=application.id,
                        user_id=user.id,
                        contract_number=f"ML-2024-{i+1:04d}",
                        principal=application.amount,
                        interest_total=application.total_repayment - application.amount,
                        total_amount_due=application.total_repayment,
                        start_date=datetime.now().date() - timedelta(days=i * 10),
                        end_date=datetime.now().date() + timedelta(days=30 * 6 - i * 10),
                        status="active",
                        signed_by_customer=True,
                        signed_at=datetime.now() - timedelta(days=i * 9),
                    )
                    db.add(contract)
                    print(f"✅ Contract created for User{i+1}: {contract.contract_number}")
                    
                    # Create repayments
                    for j in range(6):
                        due_date = datetime.now().date() + timedelta(days=30 * (j - i))
                        repayment = Repayment(
                            id=uuid.uuid4(),
                            contract_id=contract.id,
                            user_id=user.id,
                            amount=application.monthly_installment,
                            due_date=due_date,
                            status="paid" if due_date < datetime.now().date() else "pending",
                            paid_date=due_date if due_date < datetime.now().date() else None,
                        )
                        db.add(repayment)
                        print(f"  - Repayment {j+1}: P{repayment.amount} due {due_date}")
            
            await db.commit()
        
        print("=" * 60)
        print("✅ Database seeded successfully!")
        print("=" * 60)
        print("")
        print("📋 Sample Users:")
        print("  👤 Admin: admin@microlend.co.bw / Admin123!")
        print("  👤 User1: user1@example.com / Test123!")
        print("  👤 User2: user2@example.com / Test123!")
        print("  👤 User3: user3@example.com / Test123!")
        print("")
        print("📱 Sample Data:")
        print("  - 3 users with collateral items")
        print("  - 3 loan applications (2 approved, 1 pending)")
        print("  - 2 active loan contracts with repayments")
        print("")
        print("🔗 Access the application:")
        print("  - Frontend: http://localhost:3000")
        print("  - Backend API: http://localhost:8000")
        print("  - API Docs: http://localhost:8000/docs")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_database())