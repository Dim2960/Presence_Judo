# app/routes/stats_routes.py
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from ..services.stats_service import (
    piechart_repart_presence,
    barChart_repart_presence,
    heatmap_presence_mois_cours
)

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/Statistique_generale')
@login_required
def Statistique_generale():
    try:
        piechart = piechart_repart_presence()
        barChart = barChart_repart_presence()
        HeatMap = heatmap_presence_mois_cours()
        return render_template('visu_generale.html', pieChart=piechart, barChart=barChart, HeatMap=HeatMap)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stats_bp.route('/Statistique_groupe')
@login_required
def Statistique_groupe():
    return render_template('visu_grp.html')
