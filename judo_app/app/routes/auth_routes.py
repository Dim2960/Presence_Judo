# Copyright (c) 2025 Dimitri Lefebvre
# Tous droits réservés. Ce fichier fait partie d'un logiciel propriétaire.
# Son utilisation est soumise aux conditions définies dans le fichier LICENSE.

from flask import (
    Blueprint, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    session
)
from flask_login import (
    login_user, 
    logout_user, 
    login_required
)
from werkzeug.security import check_password_hash
from ..models import Connexion_user

# Création du blueprint pour l'authentification
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Gère la connexion des utilisateurs.
    
    Returns:
        Response: Page de connexion ou redirection après authentification.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Veuillez renseigner tous les champs.', 'warning')
            return redirect(url_for('auth.login'))
        
        user = Connexion_user.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            session.permanent = True
            return redirect(url_for('main.index'))
        
        flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Gère l'inscription des nouveaux utilisateurs.
    
    Returns:
        Response: Page d'inscription.
    """
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Déconnecte l'utilisateur et le redirige vers la page de connexion.
    
    Returns:
        Response: Redirection vers la page de connexion.
    """
    logout_user()
    return redirect(url_for('auth.login'))
