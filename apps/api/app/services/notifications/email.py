from abc import ABC, abstractmethod
from email.mime.text import MIMEText
import smtplib
import os
from app.core.logging import logger

class AbstractEmailProvider(ABC):
    """Abstract interface defining platform email notification deliveries."""
    
    @abstractmethod
    async def send_email(self, to_address: str, subject: str, message_body: str) -> bool:
        """Sends an email and returns the delivery success flag."""
        pass

class MockEmailProvider(AbstractEmailProvider):
    """Fallback email provider writing messages directly to system loggers."""
    
    async def send_email(self, to_address: str, subject: str, message_body: str) -> bool:
        logger.info(f"[Email Dispatch (Mock)] To: {to_address} | Subject: {subject} | Content: {message_body}")
        return True

class SmtpEmailProvider(AbstractEmailProvider):
    """Concrete SMTP email sender integration."""
    
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "localhost")
        self.port = int(os.getenv("SMTP_PORT", "1025")) # Defaults to Mailpit port
        self.user = os.getenv("SMTP_USER", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.from_addr = os.getenv("SMTP_FROM", "hello@nomen.ai")
        
    async def send_email(self, to_address: str, subject: str, message_body: str) -> bool:
        msg = MIMEText(message_body)
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = to_address
        
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.user:
                    server.login(self.user, self.password)
                server.sendmail(self.from_addr, [to_address], msg.as_string())
            return True
        except Exception as exc:
            logger.error(f"SMTP delivery failed: {str(exc)}")
            return False
