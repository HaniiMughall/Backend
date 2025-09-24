import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-prod")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change")

    # ⚡ Online MySQL ka link yahan daalna hoga (Render/PlanetScale/ClearDB)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://<USERNAME>:<PASSWORD>@<HOST>/<DBNAME>"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
