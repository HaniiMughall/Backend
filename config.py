import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mysecret123")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwtsecret123")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL environment variable not set!")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
