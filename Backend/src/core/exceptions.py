from typing import Optional, Any


class BusinessException(Exception):
    """Base exception for business logic errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "BUSINESS_ERROR",
        status_code: int = 400,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundException(BusinessException):
    """Exception for resource not found."""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)},
        )


class UnauthorizedException(BusinessException):
    """Exception for unauthorized access."""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
        )


class ForbiddenException(BusinessException):
    """Exception for forbidden access."""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
        )


class ValidationException(BusinessException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ConflictException(BusinessException):
    """Exception for conflicting resources."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details,
        )


class RateLimitException(BusinessException):
    """Exception for rate limiting."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


class LoanEligibilityException(BusinessException):
    """Exception for loan eligibility issues."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="LOAN_ELIGIBILITY_ERROR",
            status_code=400,
            details=details,
        )


class CollateralException(BusinessException):
    """Exception for collateral-related issues."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="COLLATERAL_ERROR",
            status_code=400,
            details=details,
        )


class PaymentException(BusinessException):
    """Exception for payment-related issues."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="PAYMENT_ERROR",
            status_code=400,
            details=details,
        )