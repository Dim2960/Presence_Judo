# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Chargement des variables depuis le fichier .env

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default_secret_key")

    db_user = os.getenv("AZURE_MYSQL_USERNAME")
    db_password = os.getenv("AZURE_MYSQL_PASSWORD")
    db_host = os.getenv("AZURE_MYSQL_HOST")
    db_name = os.getenv("AZURE_MYSQL_DATABASE")
    ssl_cert = os.getenv("MYSQL_SSL_CA")  # si besoin

    # Exemple de config pour MySQL
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '/tmp/flask_session'
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'judoapp_'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Autres configs
    # DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1"]
