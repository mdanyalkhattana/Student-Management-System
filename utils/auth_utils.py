from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config.config import settings
from schemas.auth_schema import TokenData
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import settings
from jinja2 import Environment, FileSystemLoader
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from config.config import settings
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from jose import jwt
from jose import jwt, JWTError
from config.config import settings

SERVER_URL = settings.SERVER_URL
 
oauth2_scheme = HTTPBearer()

def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"status": "error", "message": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract actual token string
        token_str = token.credentials

        payload = jwt.decode(
            token_str,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

        return TokenData(id=user_id, email=email)

    except JWTError:
        raise credentials_exception

def send_verification_email(to_email: str, verify_token: str):    
    subject = "Verify your account"
    verify_link = f"{SERVER_URL}/auth/verify-email?token={verify_token}"

    body = f"""
    <h2>Verify Your Account</h2>
    <p>Click below to verify your email:</p>
    <a href="{verify_link}" target="_blank">Verify My Account</a>
    <br><br>
    <p>If you did not request this, please ignore this email.</p>
    """

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.send_message(msg)

def send_reset_password_email(to_email: str, reset_token: str):
    """Send email with reset password link using HTML template"""
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("reset_password_email.html")

    reset_link = f"{SERVER_URL}/auth/reset-form?token={reset_token}"
    html_content = template.render(reset_link=reset_link)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset Your Password"
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.send_message(msg)

# utils/google_oauth.py
# Load settings from .env
config_data = {
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
    "GOOGLE_REDIRECT_URI": settings.GOOGLE_REDIRECT_URI
}
config = Config(environ=config_data)

# Initialize OAuth client
oauth = OAuth(config)

# Register Google OAuth2
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# password hasher instance
ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Encrypt the password before saving."""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if the password entered matches the hashed one."""
    try:
        return ph.verify(hashed_password, plain_password)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token with optional expiration.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decode JWT and return payload or None if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None