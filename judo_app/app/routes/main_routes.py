# Copyright (c) 2025 Dimitri Lefebvre
# Tous droits réservés. Ce fichier fait partie d'un logiciel propriétaire.
# Son utilisation est soumise aux conditions définies dans le fichier LICENSE.

from flask import (
    Blueprint, 
    render_template, 
    session, 
    request, 
    jsonify
)
from flask_login import (
    login_required, 
    current_user
)
from datetime import datetime
from ..extensions import db
from ..models import (
    Cours, 
    RelationUserCours
)
from ..services.stats_service import (
    piechart_repart_presence,
    barChart_repart_presence,
    heatmap_presence_mois_cours
)

# Création du blueprint principal
main_bp = Blueprint('main', __name__)

@main_bp.route('/', endpoint='index')
@login_required
def index():
    """
    Affiche la page d'accueil.
    """
    return render_template('index.html')

@main_bp.route('/mon_profil')
@login_required
def mon_profil():
    """
    Affiche la page du profil utilisateur.
    """
    return render_template('profil_perso.html')

@main_bp.route('/configuration_cours', methods=['GET', 'POST'])
@login_required
def configuration_cours():
    """
    Gère la configuration des cours.
    """
    return render_template('config_cours.html')

@main_bp.route('/appel_menu')
@login_required
def appel_menu():
    """
    Affiche le menu des appels de présence.
    """
    session['id_appel'] = 0
    current_user_id = current_user.id
    
    if not current_user_id:
        return "Utilisateur non connecté", 403
    
    cours_list = (
        db.session.query(Cours)
        .join(RelationUserCours, Cours.id == RelationUserCours.id_cours)
        .filter(RelationUserCours.id_user == current_user_id)
        .order_by(Cours.nom_cours)
        .all()
    )
    
    return render_template('appel_menu.html', cours=cours_list)

@main_bp.route('/correction_appel', methods=['POST'])
@login_required
def correction_appel():
    """
    Gère la correction des appels de présence.
    """
    id_cours = request.form.get('id_cours')
    id_appel = request.form.get('id_appel')
    session['id_appel'] = id_appel
    session['id_cours'] = id_cours
    
    return render_template('correction_appel.html', id_cours=id_cours, id_appel=id_appel)

@main_bp.route('/correction_cours', methods=['POST', 'GET'])
@login_required
def correction_cours():
    """
    Gère la correction des cours.
    """
    id_cours = request.form.get('id_cours')
    session['id_cours'] = id_cours
    nom_cours = request.form.get('nom_cours', '')
    
    return render_template('correction_cours.html', id_cours=id_cours, nom_cours=nom_cours)

@main_bp.route('/appel_encours', methods=['POST'])
@login_required
def appel_encours():
    """
    Gère l'affichage des appels en cours.
    """
    nom_cours = request.form.get('nom_cours')
    id_cours = request.form.get('id_cours')
    
    if session.get('id_cours') != id_cours:
        session['data_cache'] = dict()
    
    session['id_cours'] = id_cours
    today = datetime.now().strftime("%A %d %B %Y")
    
    return render_template('appel_encours.html', nom_cours=nom_cours, id_cours=id_cours, today=today)

@main_bp.route('/statistique_generale')
@login_required
def statistique_generale():
    """
    Affiche les statistiques générales de présence.
    """
    try:
        piechart = piechart_repart_presence()
        barChart = barChart_repart_presence()
        heatmap = heatmap_presence_mois_cours()
        
        return render_template('visu_generale.html', pieChart=piechart, barChart=barChart, HeatMap=heatmap)
    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500

@main_bp.route('/statistique_groupe')
@login_required
def statistique_groupe():
    """
    Affiche les statistiques de groupe.
    """
    return render_template('visu_grp.html')

@main_bp.route('/menu_correction_appel')
@login_required
def menu_correction_appel():
    """
    Affiche le menu de correction des appels.
    """
    return render_template('menu_correction_appel.html')
