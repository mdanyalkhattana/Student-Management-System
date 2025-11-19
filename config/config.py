from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_CONNECTION: Optional[str] = None
    DB_DRIVER: Optional[str] = None
    FRONTEND_URL: Optional[str] = None
    GOOGLE_CLIENT_SECRET:Optional[str] 

    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS:int
    
    SMTP_EMAIL: str
    SMTP_PASSWORD: str
    SMTP_SERVER: str
    SMTP_PORT: int
    
    GOOGLE_CLIENT_ID:str
    GOOGLE_CLIENT_SECRET:str
    GOOGLE_REDIRECT_URI: Optional[str] = None
    # for email verification link
    SERVER_URL: Optional[str] = None


    class Config:
        env_file = ".env"


      
# class setting:
# 	PROJECT_NAME="websocket_project"
# 	PROJECT_VERSION="0.1.1"

      

    
settings = Settings()
