from fastapi_mail import ConnectionConfig, FastMail

mail_connection_config = ConnectionConfig(
    MAIL_USERNAME="noreply@richsmmsofts.ru",
    MAIL_PASSWORD="decaf460-458d-48f3-b312-e4891af8441f",
    MAIL_FROM="noreply@richsmmsofts.ru",
    MAIL_PORT=587,
    MAIL_SERVER="mail.hosting.reg.ru",
    MAIL_FROM_NAME="RichSMM",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fastmail = FastMail(mail_connection_config)
