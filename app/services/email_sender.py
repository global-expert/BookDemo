import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailDeliveryError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EmailConfigurationError(EmailDeliveryError):
    pass


def send_otp_email(recipient_email: str, otp_code: str) -> None:
    if settings.smtp_suppress_send:
        return

    if not settings.smtp_host or not settings.smtp_from_address:
        raise EmailConfigurationError("SMTP settings are not configured")

    message = EmailMessage()
    message["Subject"] = "Your OTP Verification Code"
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_address}>"
    message["To"] = recipient_email
    message.set_content(
        "Your OTP code is: "
        f"{otp_code}\n\n"
        "This code will expire in 10 minutes."
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    except smtplib.SMTPAuthenticationError as exc:
        raise EmailDeliveryError("SMTP authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD.") from exc
    except smtplib.SMTPConnectError as exc:
        raise EmailDeliveryError("Unable to connect to SMTP server. Check SMTP_HOST and SMTP_PORT.") from exc
    except smtplib.SMTPServerDisconnected as exc:
        raise EmailDeliveryError("SMTP server disconnected unexpectedly during send.") from exc
    except smtplib.SMTPException as exc:
        raise EmailDeliveryError(f"SMTP error: {exc}") from exc
    except TimeoutError as exc:
        raise EmailDeliveryError("SMTP connection timed out.") from exc
    except Exception as exc:
        raise EmailDeliveryError("Failed to send OTP email") from exc
