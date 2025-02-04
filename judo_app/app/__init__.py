from flask import Flask
from .config import Config
from .extensions import db, login_manager, sess
from .routes.main_routes import main_bp
from .routes.auth_routes import auth_bp
from .routes.api_routes import api_bp
from .routes.stats_routes import stats_bp

def create_app():
    """
    Initialise et configure l'application Flask.
    
    Returns:
        Flask: Instance de l'application Flask configurée.
    """
    app = Flask(__name__)
    
    # Charger la configuration de l'application
    app.config.from_object(Config)
    
    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    sess.init_app(app)
    
    # Enregistrement des blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(stats_bp)
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """
        Ferme la session de la base de données à la fin de chaque requête.
        """
        try:
            db.session.remove()
        except Exception as e:
            app.logger.error(f"Erreur lors de la fermeture de la session : {e}")
    
    return app