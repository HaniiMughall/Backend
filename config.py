import os

class Config:
    SECRET_KEY = "change-me"
    JWT_SECRET_KEY = "jwt-secret-change"

    # Aiven MySQL connection string
    # Aiven credentials removed from repo
    # Use environment variable instead
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
