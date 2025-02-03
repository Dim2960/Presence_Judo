# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import db, login_manager, sess
from .routes.main_routes import main_bp
from .routes.auth_routes import auth_bp
from .routes.api_routes import api_bp
from .routes.stats_routes import stats_bp

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Charger la configuration
    app.config.from_object(Config)

    # Initialiser les extensions
    db.init_app(app)
    login_manager.init_app(app)
    sess.init_app(app)  # Flask-Session

    # Enregistrer les Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(stats_bp)


    # Dans create_app(), après avoir créé l’app :
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        try:
            db.session.remove()
        except Exception as e:
            print(f"Erreur lors de la fermeture de la session : {e}")

    # Retourner l'instance de l'app Flask
    return app
