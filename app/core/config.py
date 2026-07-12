import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # project
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    # admin
    ADMIN_USER: str = os.getenv("ADMIN_USER")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD")
    # db
    DB_LOCAL_URL: str = os.getenv("DATABASE_LOCAL_URL")
    DATABASE_URL: str = os.getenv("DATABASE_URL")


settings = Settings()
