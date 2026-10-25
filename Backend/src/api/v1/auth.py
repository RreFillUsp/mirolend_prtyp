from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    RefreshToken,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from src.services.auth_service import AuthService
from src.core.security import get_current_user
from src.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    auth_service = AuthService(db)
    return await auth_service.register(user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password."""
    auth_service = AuthService(db)
    return await auth_service.login(credentials)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    refresh_data: RefreshToken,
    db: AsyncSession = Depends(get_db),
):
    """Get a new access token using a refresh token."""
    auth_service = AuthService(db)
    return await auth_service.refresh_token(refresh_data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
)
async def logout(
    current_user: User = Depends(get_current_user),
):
    """Logout the current user."""
    # In a real implementation, you would blacklist the token
    return None


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request password reset",
)
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset email."""
    auth_service = AuthService(db)
    await auth_service.request_password_reset(request.email)
    return {"message": "Password reset email sent if account exists"}


@router.post(
    "/password-reset/confirm",
    response_model=TokenResponse,
    summary="Confirm password reset",
)
async def confirm_password_reset(
    confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using token."""
    auth_service = AuthService(db)
    return await auth_service.confirm_password_reset(confirm.token, confirm.new_password)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Get the current user's profile."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_profile(
    user_data: UserRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    auth_service = AuthService(db)
    return await auth_service.update_profile(current_user.id, user_data)