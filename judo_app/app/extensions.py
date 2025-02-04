from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session

# Initialisation des extensions Flask
db = SQLAlchemy()
login_manager = LoginManager()
sess = Session()

@login_manager.user_loader
def load_user(user_id):
    """
    Charge l'utilisateur à partir de l'ID stocké dans la session.
    
    Args:
        user_id (int): ID de l'utilisateur.
    
    Returns:
        Connexion_user: L'utilisateur correspondant ou None si introuvable.
    """
    from .models import Connexion_user
    try:
        return Connexion_user.query.get(int(user_id))
    except:
        return None

# Configuration de la vue de connexion par défaut pour les utilisateurs non authentifiés
login_manager.login_view = 'auth.login'  # type: ignore # Nom du Blueprint + nom de la fonction
