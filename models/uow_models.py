from .email_verification_model import EmailVerificationToken
from .session_model import Session
from .user_model import User


class UnitOfWorkModels:
    User = User
    EmailVerificationToken = EmailVerificationToken
    Session = Session