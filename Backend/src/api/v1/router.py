from fastapi import APIRouter
from src.api.v1 import auth, users, loans, collateral, payments, admin

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(loans.router)
api_router.include_router(collateral.router)
api_router.include_router(payments.router)
api_router.include_router(admin.router)