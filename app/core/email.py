from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from aiosmtplib import SMTP
from email.message import EmailMessage
from app.core.config import settings
from app.core.logging_config import logger

template_dir = Path(__file__).parent.parent / "templates" / "emails"
template_env = Environment(loader=FileSystemLoader(template_dir))


async def send_email(
    to_email: str,
    subject: str,
    template_name: str,
    context: dict,
) -> bool:
    try:
        template = template_env.get_template(template_name)
        html_content = template.render(**context)
        
        message = EmailMessage()
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(html_content, subtype="html")
        
        # Подключаемся без SSL, затем включаем STARTTLS
        smtp = SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT)
        await smtp.connect()
        await smtp.starttls()  # Включаем шифрование
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        await smtp.send_message(message)
        await smtp.quit()
        
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False


async def send_welcome_email(to_email: str, username: str):
    return await send_email(
        to_email=to_email,
        subject="Добро пожаловать в Плавательный портал!",
        template_name="welcome.html",
        context={"username": username}
    )


async def send_password_reset_email(to_email: str, token: str):
    reset_link = f"http://localhost:8000/auth/reset-password-page?token={token}"
    return await send_email(
        to_email=to_email,
        subject="Сброс пароля",
        template_name="password_reset.html",
        context={"reset_link": reset_link, "token": token}
    )
