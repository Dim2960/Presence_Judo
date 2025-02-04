from flask import (
                        Blueprint, 
                        render_template, 
                        session, request, 
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

main_bp = Blueprint('main', __name__)



@main_bp.route('/', endpoint='index')
@login_required
def index():
    return render_template('index.html')


@main_bp.route('/mon_profil')
@login_required
def mon_profil() :
    return render_template('profil_perso.html')


@main_bp.route('/configuration_cours', methods=['GET', 'POST'])
@login_required
def configuration_cours() :
    return render_template('config_cours.html')


@main_bp.route('/appel_menu')
@login_required
def appel_menu() :
    
    session['id_appel'] = 0

    current_user_id = current_user.id

    if not current_user_id:
        return "Utilisateur non connecté", 403  # Bloquer l'accès si pas connecté
    

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
    id_cours = request.form.get('id_cours')
    id_appel = request.form.get('id_appel')

    session['id_appel'] = id_appel
    session['id_cours'] = id_cours

    return render_template('correction_appel.html', id_cours=id_cours, id_appel=id_appel)


@main_bp.route('/correction_cours', methods=['POST', 'GET'])
@login_required
def correction_cours():
    id_cours = request.form.get('id_cours')
    session['id_cours'] = id_cours
    nom_cours = request.form.get('nom_cours', '')

    return render_template('correction_cours.html', id_cours=id_cours, nom_cours=nom_cours)


@main_bp.route('/appel_encours', methods=['POST'])
@login_required
def appel_encours():
    nom_cours = request.form.get('nom_cours')
    id_cours = request.form.get('id_cours')


    # Stocker dans la session
    if  session.get('id_cours') != id_cours :
        session['data_cache'] = dict()

    session['id_cours'] = id_cours

    today = datetime.now().strftime("%A %d %B %Y")

    return render_template('appel_encours.html', nom_cours=nom_cours, id_cours=id_cours, today=today)


@main_bp.route('/Statistique_generale')
@login_required
def Statistique_generale() :
    try: 

        piechart = piechart_repart_presence()

        barChart = barChart_repart_presence()

        HeatMap= heatmap_presence_mois_cours()

        return render_template('visu_generale.html', pieChart=piechart, barChart=barChart, HeatMap=HeatMap)
    
    except Exception as e:
        return jsonify({"error": f"  : {str(e)}"}), 500


@main_bp.route('/Statistique_groupe')
@login_required
def Statistique_groupe() :
    return render_template('visu_grp.html')


@main_bp.route('/menu_correction_appel')
@login_required
def menu_correction_appel() :
    return render_template('menu_correction_appel.html')
