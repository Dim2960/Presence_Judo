from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from ..services.stats_service import (
    piechart_repart_presence,
    barChart_repart_presence,
    heatmap_presence_mois_cours
)

# Création du blueprint pour les statistiques
stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/Statistique_generale')
@login_required
def statistique_generale():
    """
    Génère et affiche les statistiques générales de présence.
    
    Returns:
        Response: Page des statistiques générales ou JSON en cas d'erreur.
    """
    try:
        piechart = piechart_repart_presence()
        barChart = barChart_repart_presence()
        heatmap = heatmap_presence_mois_cours()
        return render_template('visu_generale.html', pieChart=piechart, barChart=barChart, HeatMap=heatmap)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stats_bp.route('/Statistique_groupe')
@login_required
def statistique_groupe():
    """
    Affiche les statistiques de groupe.
    
    Returns:
        Response: Page des statistiques de groupe.
    """
    return render_template('visu_grp.html')