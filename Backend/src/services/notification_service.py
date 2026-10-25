from typing import Optional, List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
import smtplib
import json
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class NotificationService:
    """Notification service for emails and SMS."""
    
    def __init__(self):
        self.smtp_server = getattr(settings, "SMTP_SERVER", None)
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_username = getattr(settings, "SMTP_USERNAME", None)
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", None)
        self.from_email = settings.FROM_EMAIL
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email."""
        try:
            if settings.SENDGRID_API_KEY:
                # Use SendGrid
                return await self._send_sendgrid(to_email, subject, html_content)
            else:
                # Use SMTP
                return await self._send_smtp(to_email, subject, html_content, text_content)
        except Exception as e:
            logger.error("Failed to send email", error=str(e), to_email=to_email)
            return False
    
    async def _send_sendgrid(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SendGrid."""
        # This is a placeholder - implement with SendGrid SDK
        logger.info("Sending email via SendGrid", to=to_email, subject=subject)
        return True
    
    async def _send_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send email using SMTP."""
        if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            logger.warning("SMTP not configured, logging email instead")
            logger.info(f"Email to {to_email}: {subject}")
            return True
        
        # Implement SMTP sending
        return True
    
    async def send_sms(
        self,
        phone_number: str,
        message: str,
    ) -> bool:
        """Send an SMS."""
        try:
            if settings.AFRICASTALKING_USERNAME:
                return await self._send_africastalking(phone_number, message)
            elif settings.TWILIO_ACCOUNT_SID:
                return await self._send_twilio(phone_number, message)
            else:
                logger.info(f"SMS to {phone_number}: {message}")
                return True
        except Exception as e:
            logger.error("Failed to send SMS", error=str(e), to=phone_number)
            return False
    
    async def _send_africastalking(self, phone_number: str, message: str) -> bool:
        """Send SMS using Africa's Talking."""
        # This is a placeholder - implement with Africa's Talking SDK
        logger.info("Sending SMS via Africa's Talking", to=phone_number, message=message)
        return True
    
    async def _send_twilio(self, phone_number: str, message: str) -> bool:
        """Send SMS using Twilio."""
        # This is a placeholder - implement with Twilio SDK
        logger.info("Sending SMS via Twilio", to=phone_number, message=message)
        return True
    
    # Template methods
    async def send_welcome_email(self, user_email: str, first_name: str):
        """Send welcome email to new user."""
        html = f"""
        <h1>Welcome to MicroLend Botswana!</h1>
        <p>Hello {first_name},</p>
        <p>Thank you for joining MicroLend. You can now apply for loans using your collateral.</p>
        <p>Get started by completing your KYC verification.</p>
        <a href="https://app.microlend.co.bw/kyc">Complete KYC</a>
        """
        await self.send_email(user_email, "Welcome to MicroLend!", html)
    
    async def send_loan_approved_email(self, user_email: str, amount: float, contract_number: str):
        """Send loan approval email."""
        html = f"""
        <h1>Your Loan Has Been Approved!</h1>
        <p>Congratulations! Your loan of P{amount:,.2f} has been approved.</p>
        <p>Contract Number: {contract_number}</p>
        <p>Funds will be disbursed within 24 hours.</p>
        <a href="https://app.microlend.co.bw/dashboard">View Dashboard</a>
        """
        await self.send_email(user_email, "Loan Approved! 🎉", html)
    
    async def send_payment_reminder(
        self,
        user_email: str,
        first_name: str,
        amount: float,
        due_date: str,
    ):
        """Send payment reminder."""
        html = f"""
        <h1>Payment Reminder</h1>
        <p>Hello {first_name},</p>
        <p>Your payment of P{amount:,.2f} is due on {due_date}.</p>
        <p>Please make your payment on time to avoid late fees.</p>
        <a href="https://app.microlend.co.bw/payments">Make Payment</a>
        """
        await self.send_email(user_email, "Payment Reminder", html)