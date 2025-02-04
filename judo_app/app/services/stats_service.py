# Copyright (c) 2025 Dimitri Lefebvre
# Tous droits réservés. Ce fichier fait partie d'un logiciel propriétaire.
# Son utilisation est soumise aux conditions définies dans le fichier LICENSE.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime, timedelta
from flask import jsonify
from ..models import execute_query

def extractAppel():
    """
    Extrait les données de présence des élèves judokas en effectuant une requête SQL sur la base de données.
    
    Retourne un DataFrame contenant les présences avec le nom du cours correspondant.
    
    Returns:
        DataFrame: Un tableau contenant les présences des élèves avec les détails des cours.
        Response (json): En cas d'erreur, retourne une réponse JSON avec un message d'erreur et un code HTTP 500.
    """
    try:
        # Définition de la requête SQL pour récupérer les présences avec le nom du cours associé
        query = """
            SELECT 
                a.*,  
                c.nom_cours  
            FROM 
                appel a 
            JOIN 
                cours c ON a.id_cours = c.id; 
        """
        
        # Exécute la requête et récupère les résultats sous forme de DataFrame
        df = execute_query(query)

        # Vérifie si la requête a retourné des données valides
        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données. Vérifiez id_cours et date."}), 500
        
        return df  # Retourne le DataFrame contenant les données de présence
    except Exception as e:
        # Gestion des erreurs et retour d'une réponse JSON en cas d'échec
        return jsonify({"error": f"Erreur lors de la récupération des données : {str(e)}"}), 500


def repart_presence_general(df):
    """
    Calcule la répartition des présences, absences, absences excusées et retards
    à partir d'un DataFrame contenant ces informations.

    Paramètres:
    df (pd.DataFrame): DataFrame contenant les colonnes suivantes avec des valeurs binaires (1 ou 0) :
        - 'present' : 1 si le judoka est présent, 0 sinon.
        - 'absent' : 1 si le judoka est absent, 0 sinon.
        - 'retard' : 1 si le judoka est en retard, 0 sinon.
        - 'absence_excuse' : 1 si le judoka a une absence excusée, 0 sinon.

    Retourne:
    pd.DataFrame: Un DataFrame contenant les catégories de présence et leurs effectifs respectifs.
    """
    # Vérifie si l'entrée est bien un DataFrame
    if isinstance(df, pd.DataFrame):
        
        # Comptabilise le nombre de présences (nombre de 1 dans la colonne 'present')
        presence_counts = df['present'].value_counts(normalize=False).get(1, 0)
        
        # Comptabilise le nombre d'absences (nombre de 1 dans la colonne 'absent')
        absence_counts = df['absent'].value_counts(normalize=False).get(1, 0)
        
        # Comptabilise le nombre de retards (nombre de 1 dans la colonne 'retard')
        retard_counts = df['retard'].value_counts(normalize=False).get(1, 0)
        
        # Comptabilise le nombre d'absences excusées (nombre de 1 dans la colonne 'absence_excuse')
        absence_excuse_counts = df['absence_excuse'].value_counts(normalize=False).get(1, 0)
        
        # Création d'un DataFrame contenant le résumé des différentes catégories de présence
        df_result = pd.DataFrame({
            'Category': ['Présent', 'Absent', 'Excusé', 'Retard'],
            'Value': [presence_counts, absence_counts, absence_excuse_counts, retard_counts]
        })
        
        return df_result
    else:
        # Retourne une erreur si l'entrée n'est pas un DataFrame valide
        return {"error": "Erreur lors de la récupération des données. df doit être un DataFrame valide."}, 500


def repart_presence_cours(df):
    """
    Agrège et transforme les données de présence des élèves judoka par cours.
    
    Parameters:
    df (pd.DataFrame): Un DataFrame contenant les présences avec les colonnes suivantes :
        - 'nom_cours' : Nom du cours
        - 'present' : Booléen indiquant la présence (1 si présent, sinon 0)
        - 'absent' : Booléen indiquant l'absence (1 si absent, sinon 0)
        - 'retard' : Booléen indiquant un retard (1 si en retard, sinon 0)
        - 'absence_excuse' : Booléen indiquant une absence excusée (1 si excusé, sinon 0)
    
    Returns:
    pd.DataFrame: Un DataFrame contenant la répartition des présences sous forme d'un tableau transformé avec les catégories et les valeurs associées.
    """
    if not isinstance(df, pd.DataFrame):
        return jsonify({"error": "Erreur lors de la récupération des données. df est None"}), 500
    
    # Agrégation des présences par cours en comptant le nombre d'occurrences de chaque catégorie
    result = df.groupby('nom_cours').agg({
        'present': lambda x: x.eq(1).sum(),
        'absent': lambda x: x.eq(1).sum(), 
        'retard': lambda x: x.eq(1).sum(),
        'absence_excuse': lambda x: x.eq(1).sum()
    }).reset_index()

    # Transformation des données pour obtenir une colonne 'Category' contenant les types de présence
    df_melted = pd.melt(
        result,
        id_vars=['nom_cours'],  # Conservation du nom du cours
        value_vars=['present', 'absent', 'retard', 'absence_excuse'],  # Catégories à transformer
        var_name='Category',  # Nouvelle colonne pour les catégories
        value_name='Value'  # Valeur associée à chaque catégorie
    )

    # Mapping des catégories 
    category_map = {
        'present': 'Présent',
        'absent': 'Absent',
        'retard': 'Retard',
        'absence_excuse': 'Excusé'
    }
    df_melted['Category'] = df_melted['Category'].map(category_map)

    return df_melted



def graphToImg(fig):
    """
    Convertit un objet Matplotlib figure en une image encodée en base64.
    
    Paramètres:
    fig (matplotlib.figure.Figure) : La figure Matplotlib à convertir.
    
    Retourne:
    str : Une chaîne de caractères représentant l'image en base64, directement affichable dans une balise HTML.
    """
    
    # Création d'un buffer mémoire pour stocker l'image
    pngImage = io.BytesIO()
    
    # Sauvegarde de la figure dans le buffer au format PNG
    fig.savefig(pngImage, format='png')
    
    # Repositionnement du pointeur au début du buffer pour la lecture
    pngImage.seek(0)
    
    # Encodage de l'image en base64 pour l'intégration dans une page web
    pngImageB64String = "data:image/png;base64," + base64.b64encode(pngImage.read()).decode('utf8')
    
    return pngImageB64String


def piechart(df: pd.DataFrame, titre: str):
    """
    Génère un diagramme en camembert à partir d'un DataFrame.
    
    Paramètres:
        df (pd.DataFrame): Un DataFrame contenant deux colonnes :
            - 'Category' : noms des catégories.
            - 'Value' : valeurs associées à chaque catégorie.
        titre (str): Le titre du graphique.
    
    Retourne:
        fig (matplotlib.figure.Figure): La figure du graphique généré.
    """
    
    # Sélection de couleurs pastel pour chaque catégorie
    colors = sns.color_palette('pastel')[0:len(df)]
    
    # Création de la figure et des axes
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Génération du camembert
    ax.pie(
        df['Value'],
        labels=df['Category'].tolist(),  # Affichage des labels des catégories
        colors=colors,  # Application des couleurs définies
        autopct='%.0f%%',  # Affichage des pourcentages
        startangle=90,  # Rotation pour commencer à 12h
        textprops={'fontsize': 12}  # Taille du texte des labels et pourcentages
    )
    
    ax.set_title(titre, fontsize=14)  # Ajout du titre
    ax.set_aspect('equal')  # Assure que le camembert reste circulaire
    
    # Suppression du fond pour une meilleure intégration visuelle
    ax.set_facecolor("none")
    fig.patch.set_alpha(0)
    
    # Ajustement des marges pour éviter les bordures blanches
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.tight_layout()
    
    return fig


def barchart(df: pd.DataFrame, titre: str):
    """
    Génère un graphique en barres représentant la répartition des valeurs par cours en pourcentage.
    
    Paramètres:
    df (pd.DataFrame): Un DataFrame contenant les colonnes 'nom_cours', 'Value' et 'Category'.
    titre (str): Le titre du graphique.
    
    Retourne:
    fig (matplotlib.figure.Figure): La figure matplotlib du graphique généré.
    """
    
    # Calcul du pourcentage de chaque valeur par rapport au total de son cours
    total_par_cours = df.groupby('nom_cours')['Value'].transform('sum')
    df['Value'] = (df['Value'] / total_par_cours) * 100  
    
    # Création de la figure et des axes
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Création du graphique en barres avec une palette de couleurs pastel
    barplot = sns.barplot(
        data=df,
        x='nom_cours',
        y='Value',
        hue='Category',  # Différenciation par catégorie
        palette=sns.color_palette("pastel")
    )
    
    # Configuration des titres et des labels
    ax.set_title(titre, fontsize=14)
    ax.set_xlabel('Cours')
    ax.set_ylabel('Pourcentage (%)')
    
    # Ajout des étiquettes de pourcentage sur chaque barre
    for container in barplot.containers:
        for rect in container:
            height = rect.get_height()
            if height > 0:  # Évite d'afficher des labels sur des barres vides
                ax.text(
                    rect.get_x() + rect.get_width() / 2,  # Position centrée
                    height,  # Juste au-dessus de la barre
                    f'{height:.0f}%',  # Format sans décimales
                    ha='center',
                    va='bottom',
                    fontsize=10, 
                    color='black'
                )
    
    # Amélioration de la lisibilité des labels sur l'axe X
    plt.xticks(rotation=45, ha='right')
    
    # Suppression des bordures supérieures et droites pour un design plus épuré
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
    Génère un graphique en camembert représentant la répartition des présences des élèves judokas.
    
    Extraction des données de présence, transformation en données exploitables, génération du graphique,
    puis conversion du graphique en image pour affichage.
    
    Retourne :
        Une image du graphique si tout fonctionne correctement.
        Une réponse JSON d'erreur en cas de problème.
    '''
    
    # Extraction des données de présence
    df_appel = extractAppel()
    
    if isinstance(df_appel, pd.DataFrame):  # Vérifie que l'extraction a réussi
        df_repart_general = repart_presence_general(df_appel)
        
        if isinstance(df_repart_general, pd.DataFrame):  # Vérifie que le traitement a réussi
            # Génération du graphique en camembert
            fig_piechart = piechart(df_repart_general, "Répartition des présences")
        else:
            return jsonify({"error": "Erreur lors du traitement des données"}), 500
    else:
        return jsonify({"error": "Erreur lors de l'extraction des données"}), 500

    # Conversion du graphique en image pour affichage
    return graphToImg(fig_piechart)


def barChart_repart_presence():
    """
    Génère un graphique en barres représentant la répartition des présences par cours.
    
    Cette fonction extrait les données d'appel, les traite pour obtenir la répartition
    des présences par cours, puis génère un graphique en barres à partir de ces données.
    Enfin, elle convertit le graphique en image et le retourne.
    
    Retour :
        Image du graphique représentant la répartition des présences.
    """
    # Extraction des données d'appel
    titre = "Répartition des présences par cours"
    df_appel = extractAppel()
    
    if isinstance(df_appel, pd.DataFrame):  # Vérifie que les données ont bien été extraites
        df_repart_cours = repart_presence_cours(df_appel)
        
        if isinstance(df_repart_cours, pd.DataFrame):  # Vérifie que les données sont correctement traitées
            # Génération du graphique en barres
            fig_barchart = barchart(df_repart_cours, titre)
        else:
            return jsonify({"error": "Erreur lors du traitement des données"}), 500
    else:
        return jsonify({"error": "Erreur lors de l'extraction des données"}), 500

    # Conversion du graphique en image avant de le retourner
    return graphToImg(fig_barchart)


def heatmap_presence_mois_cours():
    """
    Génère une heatmap représentant le taux de présence des élèves par cours et par mois.
    
    Extraction des données, transformation et affichage sous forme de heatmap.
    Retourne une image du graphique généré.
    
    Sortie : 
        - Image de la heatmap représentant le taux de présence
    """
    
    # Définition du titre du graphique
    titre = "Taux de présence par cours et par mois"
    
    # Extraction des données de présence
    df_appel = extractAppel()
    
    if isinstance(df_appel, pd.DataFrame):  # Vérifie que les données ont bien été extraites
        df_repart_cours = presence_mois_cours(df_appel)  # Transformation des données pour la heatmap
        
        if isinstance(df_repart_cours, pd.DataFrame):  # Vérifie que le traitement a réussi
            # Génération de la heatmap à partir des données traitées
            fig_heatmap = heatmap(df_repart_cours, titre)
        else:
            return jsonify({"error": "Erreur lors du traitement des données"}), 500
    else:
        return jsonify({"error": "Erreur lors de l'extraction des données"}), 500
    
    # Conversion du graphique en image pour affichage ou enregistrement
    return graphToImg(fig_heatmap)


def presence_mois_cours(df):
    """
    Calcule le taux de présence des élèves judokas par cours et par mois sur une période de 12 mois (septembre à août).
    
    Paramètres :
        df (pd.DataFrame) : DataFrame contenant les colonnes 'timestamp_appel', 'nom_cours' et 'present'.
    
    Retour :
        pd.DataFrame : Tableau de taux de présence par cours et par mois sur la période sélectionnée.
    """
    # Vérification que df est bien un DataFrame
    if not isinstance(df, pd.DataFrame):
        return {"error": "Erreur lors de la récupération des données"}, 500
        
    # Vérification et conversion de 'timestamp_appel' en datetime si elle existe
    if 'timestamp_appel' in df.columns:
        df['timestamp_appel'] = pd.to_datetime(df['timestamp_appel'])
        df['mois'] = df['timestamp_appel'].dt.strftime('%Y-%m')  # Extraction du mois sous format 'YYYY-MM'
    else:
        return "Erreur : La colonne 'timestamp_appel' est manquante dans le DataFrame."

    # Détermination de la date actuelle
    today = datetime.now().date()

    # Identification du dernier mois de septembre écoulé
    annee_courante = today.year
    if today.month < 9:
        annee_septembre = annee_courante - 1  # Si avant septembre, prendre l'année précédente
    else:
        annee_septembre = annee_courante

    # Génération des 12 mois de septembre à août suivant
    mois_debut = datetime(annee_septembre, 9, 1)
    mois_liste = [(mois_debut + timedelta(days=30*i)).strftime('%Y-%m') for i in range(12)]

    # Filtrage des données correspondant à la période définie
    df_filtered = df[df['mois'].isin(mois_liste)]

    # Calcul du taux de présence par cours et par mois
    presence_stats = df_filtered.groupby(['nom_cours', 'mois'])['present'].sum() / df_filtered.groupby(['nom_cours', 'mois'])['present'].count()
    presence_stats = presence_stats.unstack()  # Transformation en table pivot (cours en lignes, mois en colonnes)

    # Compléter avec des valeurs 0 pour les mois manquants
    presence_stats = presence_stats.reindex(columns=mois_liste, fill_value=0)

    return presence_stats


def heatmap(presence_stats, titre):
    """
    Génère une heatmap représentant le taux de présence des élèves judokas.
    
    Paramètres :
    presence_stats (DataFrame) : Tableau des taux de présence (index = id_cours, colonnes = mois).
    titre (str) : Titre de la heatmap.
    
    Retourne :
    Figure matplotlib contenant la heatmap.
    """
    # Création de la figure et de l'axe principal
    fig, ax = plt.subplots(figsize=(12, 6))

    # Récupération de la première couleur de la palette pastel pour un rendu doux
    pastel_palette = sns.color_palette("pastel")
    first_color_hex = pastel_palette[0]
    cmap_pastel = sns.light_palette(first_color_hex, as_cmap=True)
    
    # Génération de la heatmap
    sns.heatmap(
        presence_stats, 
        cmap=cmap_pastel,  # Palette de couleurs pastelles pour un rendu agréable
        annot=True,  # Affiche les valeurs de présence directement sur la heatmap
        fmt=".0%",  # Affichage en pourcentage sans décimale
        linewidths=0.6,  # Espacement entre les cases
        linecolor='white',  # Couleur des séparations
        vmin=0.5,  # Plancher des valeurs pour éviter une trop grande variation des couleurs
        cbar_kws={'label': 'Taux de Présence (%)'}  # Label de la barre de couleur
    )

    # Configuration des titres et labels
    ax.set_title(titre)
    ax.set_xlabel('')  # Suppression du label des colonnes
    ax.set_ylabel('')  # Suppression du label des lignes
    
    # Amélioration de la lisibilité des axes
    plt.xticks(rotation=45, ha='right')  # Inclinaison des labels de colonnes
    plt.yticks(rotation=0)  # Conservation des labels de lignes droits

    # Suppression de la couleur de fond pour une meilleure intégration visuelle
    ax.set_facecolor("none")  # Fond du graphe transparent
    fig.patch.set_alpha(0)  # Fond de la figure transparent

    plt.tight_layout()  # Ajustement automatique des marges
    
    return fig