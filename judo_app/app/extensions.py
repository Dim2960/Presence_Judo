# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session

db = SQLAlchemy()
login_manager = LoginManager()
sess = Session()

@login_manager.user_loader
def load_user(user_id):
    from .models import Connexion_user
    try:
        return Connexion_user.query.get(int(user_id))
    except:
        return None

# Optionnel : redirection par défaut si non connecté
login_manager.login_view = 'auth.login'  # type: ignore  # <-- Nom du Blueprint + nom de la fonction
