# app/services/stats_service.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime, timedelta
from flask import jsonify
from ..models import execute_query

def extractAppel():
    try:
        # Charger les données 
        query = f"""
            SELECT 
                a.*, 
                c.nom_cours 
            FROM 
                appel a 
            JOIN 
                cours c ON a.id_cours = c.id;
        """
        
        df = execute_query(query)

        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données Checkcouple idcours et date"}), 500
            
        return df
    
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données Checkcouple idcours et date : {str(e)}"}), 500


def repart_presence_general(df) :
        
    if isinstance(df, pd.DataFrame):
        presence_counts = df['present'].value_counts(normalize=False).get(1, 0)
        absence_counts = df['absent'].value_counts(normalize=False).get(1, 0)
        retard_counts = df['retard'].value_counts(normalize=False).get(1, 0)
        absence_excuse_counts = df['absence_excuse'].value_counts(normalize=False).get(1, 0)

        df = pd.DataFrame({
            'Category': ['Présent', 'Absent', 'Excusé', 'Retard'],
            'Value': [presence_counts, absence_counts, retard_counts, absence_excuse_counts]
        })

    else:
        return jsonify({"error": "Erreur lors de la récupération des données. df est None"}), 500
    
    return df


def repart_presence_cours(df):
    if not isinstance(df, pd.DataFrame):
        return jsonify({"error": "Erreur lors de la récupération des données. df est None"}), 500
    
    # Group by id_cours and aggregate the boolean columns
    result = df.groupby('nom_cours').agg({
        'present': lambda x: x.eq(1).sum(),
        'absent': lambda x: x.eq(1).sum(), 
        'retard': lambda x: x.eq(1).sum(),
        'absence_excuse': lambda x: x.eq(1).sum()
    }).reset_index()

    # Melt the dataframe to get categories in one column
    df_melted = pd.melt(
        result,
        id_vars=['nom_cours'],
        value_vars=['present', 'absent', 'retard', 'absence_excuse'],
        var_name='Category',
        value_name='Value'
    )

    # Map French labels
    category_map = {
        'present': 'Présent',
        'absent': 'Absent',
        'retard': 'Retard',
        'absence_excuse': 'Excusé'
    }
    df_melted['Category'] = df_melted['Category'].map(category_map)



    return df_melted


def graphToImg(fig):
    # Sauvegarde du graphique dans un buffer mémoire
    pngImage = io.BytesIO()
    fig.savefig(pngImage, format='png')
    pngImage.seek(0)  # Repositionnement au début du buffer

    # Encodage en base64
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.read()).decode('utf8')

    return pngImageB64String


def piechart(df: pd.DataFrame, titre: str): 
    colors = sns.color_palette('pastel')[0:len(df)]

    # Création de la figure avec une taille plus grande
    fig, ax = plt.subplots(figsize=(8, 8))  # Ajuste la taille ici

    ax.pie(
        df['Value'],
        labels=df['Category'].tolist(),
        colors=colors,
        autopct='%.0f%%',
        startangle=90,  # Pour commencer à 90° et améliorer la lisibilité
        textprops={'fontsize': 12}  # Augmenter la taille du texte
    )

    ax.set_title(titre, fontsize=14)  # Augmenter la taille du titre
    ax.set_aspect('equal')  # Assurer un cercle parfait

    # Suppression de la couleur de fond
    ax.set_facecolor("none")  # Fond de l'axe transparent
    fig.patch.set_alpha(0)  # Fond de la figure transparent

    # Suppression des marges inutiles
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Ajustement automatique de la mise en page
    plt.tight_layout()

    return fig


def barchart(df: pd.DataFrame, titre: str): 

    # Calcul du pourcentage par cours
    total_par_cours = df.groupby('nom_cours')['Value'].transform('sum')
    df['Value'] = (df['Value'] / total_par_cours) * 100  

    # Création de la figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Création du barplot avec la palette pastelle
    barplot = sns.barplot(
        data=df,
        x='nom_cours',
        y='Value',
        hue='Category',
        palette=sns.color_palette("pastel")  # Palette de couleurs pastelle
    )
    
    ax.set_title(titre, fontsize=14)
    ax.set_xlabel('Cours')
    ax.set_ylabel('Pourcentage (%)')

    # Ajouter les étiquettes sur les barres
    for container in barplot.containers:
        for rect in container:
            height = rect.get_height()  # Récupérer la hauteur de la barre
            if height > 0:  # Éviter d'afficher les labels sur des barres vides
                ax.text(
                    rect.get_x() + rect.get_width() / 2,  # Position X (au centre de la barre)
                    height,  # Position Y (au-dessus de la barre)
                    f'{height:.0f}%',  # Format en pourcentage
                    ha='center',  # Alignement horizontal
                    va='bottom',  # Alignement vertical
                    fontsize=10, 
                    color='black'  # Couleur du texte
                )

    # Rotation des labels pour une meilleure lisibilité
    plt.xticks(rotation=45, ha='right')

    # Suppression des bordures du haut et de droite
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Suppression de la couleur de fond
    ax.set_facecolor("none")  # Fond de l'axe transparent
    fig.patch.set_alpha(0)  # Fond de la figure transparent

    # Ajustement automatique de la mise en page
    plt.tight_layout()

    return fig


def piechart_repart_presence():
    '''
    Extraction des données
    '''
    # Données
    titre = "Répartition des présences"
    df_appel = extractAppel()
    
    if isinstance(df_appel, pd.DataFrame):
        df_repart_general = repart_presence_general(df_appel)
        
        if isinstance(df_repart_general, pd.DataFrame):
            # Parametrage et Génération du graphique
            fig_piechart = piechart(df_repart_general, titre)
        else:
            return jsonify({"error": "Erreur lors du traitement des données"}), 500
    else:
        return jsonify({"error": "Erreur lors de l'extraction des données"}), 500

    # Convertir graph en image
    return graphToImg(fig_piechart)


def barChart_repart_presence():
    '''
    Extraction des données
    '''
    # Données
    titre = "Répartition des présences par cours"
    df_appel = extractAppel()
    
    if isinstance(df_appel, pd.DataFrame):
        df_repart_cours = repart_presence_cours(df_appel)
        
        if isinstance(df_repart_cours, pd.DataFrame):
            # Parametrage et Génération du graphique
            fig_barchart = barchart(df_repart_cours, titre)
        else:
            return jsonify({"error": "Erreur lors du traitement des données"}), 500
    else:
        return jsonify({"error": "Erreur lors de l'extraction des données"}), 500

    # Convertir graph en image
    return graphToImg(fig_barchart)


def heatmap_presence_mois_cours():
    '''
    Extraction des données
    '''
    # Données
    titre = "Taux de présence par cours et par mois"
    df_appel = extractAppel()
    
    if isinstance(df_appel, pd.DataFrame):
        df_repart_cours = presence_mois_cours(df_appel)
        
        if isinstance(df_repart_cours, pd.DataFrame):
            # Parametrage et Génération du graphique
            fig_heatmap = heatmap(df_repart_cours, titre)
        else:
            return jsonify({"error": "Erreur lors du traitement des données"}), 500
    else:
        return jsonify({"error": "Erreur lors de l'extraction des données"}), 500

    # Convertir graph en image
    return graphToImg(fig_heatmap)


def presence_mois_cours(df):
    # Vérification du type de df
    if not isinstance(df, pd.DataFrame):
        return {"error": "Erreur lors de la récupération des données"}, 500
        
    # Vérification et conversion de la colonne 'timestamp_appel' en datetime
    if 'timestamp_appel' in df.columns:
        df['timestamp_appel'] = pd.to_datetime(df['timestamp_appel'])
        df['mois'] = df['timestamp_appel'].dt.strftime('%Y-%m')  # Format Année-Mois
    else:
        return "Erreur : La colonne 'timestamp_appel' est manquante dans le DataFrame."

    # Déterminer la date actuelle
    today = datetime.now().date()

    # Trouver le dernier mois de septembre passé
    annee_courante = today.year
    if today.month < 9:  # Si on est avant septembre, on prend septembre de l'année précédente
        annee_septembre = annee_courante - 1
    else:
        annee_septembre = annee_courante

    # Générer les 12 mois de septembre -> août suivant
    mois_debut = datetime(annee_septembre, 9, 1)  # Septembre de l'année sélectionnée
    mois_liste = [(mois_debut + timedelta(days=30*i)).strftime('%Y-%m') for i in range(12)]

    # Filtrer uniquement les données des 12 mois sélectionnés
    df_filtered = df[df['mois'].isin(mois_liste)]

    # Calcul du taux de présence par id_cours et par mois
    presence_stats = df_filtered.groupby(['nom_cours', 'mois'])['present'].sum() / df_filtered.groupby(['nom_cours', 'mois'])['present'].count()
    presence_stats = presence_stats.unstack()  # Transformation en table pivot

    # Ajouter les mois manquants avec 0
    presence_stats = presence_stats.reindex(columns=mois_liste, fill_value=0)

    return presence_stats


def heatmap(presence_stats, titre):
    # Création de la figure
    plt.figure(figsize=(12, 6))
    fig, ax = plt.subplots(figsize=(12, 6))

    # Utilisation d'une palette pastel
    # Récupérer la palette pastel
    pastel_palette = sns.color_palette("pastel")
    first_color_hex = pastel_palette[0]

    cmap_pastel = sns.light_palette(first_color_hex, as_cmap=True)

    
    # Création de la heatmap
    sns.heatmap(
        presence_stats, 
        cmap=cmap_pastel,  # Couleur de la heatmap 
        annot=True,  # Affiche les valeurs sur la heatmap
        fmt=".0%",  # Format pourcentage
        linewidths=0.6,  # Séparation entre les cases
        linecolor='white',
        vmin=0.5,
        cbar_kws={'label': 'Taux de Présence (%)'}
    )

    # Configuration des labels
    ax.set_title(titre)
    ax.set_xlabel('')
    ax.set_ylabel('')

    plt.xticks(rotation=45, ha='right')  # Rotation des mois pour meilleure lisibilité
    plt.yticks(rotation=0)  # Garde les id_cours droits

    # Suppression de la couleur de fond
    ax.set_facecolor("none")  # Fond de l'axe transparent
    fig.patch.set_alpha(0)  # Fond de la figure transparent

    plt.tight_layout()
    
    return fig
