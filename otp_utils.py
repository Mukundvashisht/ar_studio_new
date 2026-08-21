import os
import smtplib
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

class OTPManager:
    """
    A utility class to handle OTP generation, verification, and email sending.
    """
    
    @staticmethod
    def generate_otp(length=6):
        """
        Generate a random numeric OTP of specified length.
        
        Args:
            length (int): Length of the OTP (default: 6)
            
        Returns:
            str: The generated OTP
        """
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def is_otp_expired(otp_created_at, expiry_minutes=5):
        """
        Check if an OTP has expired.
        
        Args:
            otp_created_at (datetime): When the OTP was created
            expiry_minutes (int): Number of minutes before OTP expires (default: 5)
            
        Returns:
            bool: True if expired, False otherwise
        """
        if not otp_created_at:
            return True
        return datetime.utcnow() > otp_created_at + timedelta(minutes=expiry_minutes)
    
    @classmethod
    def send_otp_email(cls, recipient_email, otp):
        """
        Send an OTP to the specified email address using Gmail SMTP.
        
        Args:
            recipient_email (str): Email address to send OTP to
            otp (str): The OTP to send
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Email configuration - these should be set in your .env file
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not all([smtp_username, smtp_password]):
            current_app.logger.error("SMTP credentials not configured")
            return False
            
        # Create message
        subject = "Your OTP for Account Verification"
        body = f"""
        <h2>Email Verification</h2>
        <p>Your OTP for email verification is: <strong>{otp}</strong></p>
        <p>This OTP is valid for 5 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        """
        
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        try:
            # Connect to SMTP server and send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send OTP email: {str(e)}")
            return False
