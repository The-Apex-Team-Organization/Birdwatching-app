import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    BLACKLIST_REDIRECT_URL = "https://zakon.rada.gov.ua/laws/show/2341-14#n1668"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    REGION       = os.getenv("REGION")

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')