# src/core/config.py - Simplified version
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    # API
    APP_NAME: str = "MicroLend Botswana"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./microlend.db"
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Security
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    
    # Loan Settings
    MIN_LOAN_AMOUNT: float = 100.0
    MAX_LOAN_AMOUNT: float = 50000.0
    DEFAULT_INTEREST_RATE: float = 20.0
    MAX_INTEREST_RATE: float = 24.0
    MIN_TERM_MONTHS: int = 1
    MAX_TERM_MONTHS: int = 12

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()