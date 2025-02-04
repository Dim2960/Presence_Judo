# Copyright (c) 2025 Dimitri Lefebvre
# Tous droits réservés. Ce fichier fait partie d'un logiciel propriétaire.
# Son utilisation est soumise aux conditions définies dans le fichier LICENSE.

from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user
from datetime import datetime
import pandas as pd

from ..extensions import db
from ..models import (
    Cours, 
    RelationCours, 
    RelationUserCours, 
    User, 
    Appel, 
    execute_query
)

api_bp = Blueprint('api', __name__)

@api_bp.route('/addCours', methods=['POST'])
@login_required
def add_cours():
    """
    Ajoute un cours et crée les relations cours-catégorie dans la table 'relation_cours_categorie_age'.
    """
    try:
        data = request.get_json()
        nom_cours = data.get('nom')
        categorie_age = data.get('categories')

        if not nom_cours:
            return jsonify({'error': 'Le nom du cours est requis'}), 400
        
        if categorie_age is None:
            return jsonify({'error': 'La catégorie d\'âge est requise'}), 400

        # Vérification de l'existence du cours
        existing_cours = Cours.query.filter_by(nom_cours=nom_cours).first()
        if existing_cours:
            return jsonify({'error': 'Ce cours existe déjà'}), 409

        # Ajouter le cours dans la table 'cours'
        new_cours = Cours(nom_cours=nom_cours, categorie_age=categorie_age[0])
        db.session.add(new_cours)
        db.session.commit()

        # Ajouter les relations cours -> catégories
        for row_categ in categorie_age:
            new_relation = RelationCours(id_cours=new_cours.id, id_categorie_age=row_categ)
            db.session.add(new_relation)
            db.session.commit()

        return jsonify({'message': 'Cours ajouté avec succès', 'nom_cours': nom_cours}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'ajout du cours : {str(e)}'}), 500
    finally:
        db.session.remove()


@api_bp.route('/updateCours/<int:id_cours>', methods=['PUT'])
@login_required
def update_cours(id_cours):
    """
    Met à jour un cours existant et réinitialise les relations de catégories associées.
    """
    try:
        data = request.get_json()
        nom_cours = data.get('nom')
        categorie_age = data.get('categories')

        # Vérifier si le cours existe
        cours = Cours.query.get(id_cours)
        if not cours:
            return jsonify({'error': 'Cours non trouvé'}), 404

        # Validation des données
        if not nom_cours:
            return jsonify({'error': 'Le nom du cours est requis'}), 400

        if not categorie_age or not isinstance(categorie_age, list):
            return jsonify({'error': 'Au moins une catégorie d\'âge est requise'}), 400

        # Mise à jour du nom du cours
        cours.nom_cours = nom_cours
        db.session.commit()

        # Mise à jour des relations cours-catégorie
        RelationCours.query.filter_by(id_cours=id_cours).delete()
        for row_categ in categorie_age:
            new_relation = RelationCours(id_cours=id_cours, id_categorie_age=row_categ)
            db.session.add(new_relation)

        db.session.commit()

        return jsonify({'message': 'Cours mis à jour avec succès', 'nom_cours': nom_cours}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour du cours : {str(e)}'}), 500
    finally:
        db.session.remove()


@api_bp.route('/updateCoursUser/<int:id_user>', methods=['PUT'])
@login_required
def update_cours_user(id_user):
    """
    Assigne ou réassigne un ensemble de cours à un utilisateur.
    """
    try:
        data = request.get_json()
        cours = data.get('coursUser')

        # Vérifier l'existence de l'utilisateur
        user_record = User.query.get(id_user)
        if not user_record:
            return jsonify({'error': 'id_user non trouvé'}), 404

        # Validation des données
        if not cours or not isinstance(cours, list):
            return jsonify({'error': 'Au moins un cours est requis'}), 400

        # Supprimer les relations existantes
        RelationUserCours.query.filter_by(id_user=id_user).delete()

        # Ajouter les nouvelles relations
        for row_cours in cours:
            new_relation = RelationUserCours(user_id=id_user, cours_id=row_cours)
            db.session.add(new_relation)

        db.session.commit()
        return jsonify({'message': 'Cours mis à jour avec succès', 'id_user': id_user}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour du cours : {str(e)}'}), 500
    finally:
        db.session.remove()


@api_bp.route('/delete-cours/<int:cours_id>', methods=['DELETE'])
@login_required
def delete_cours(cours_id):
    """
    Supprime un cours existant.
    """
    try:
        cours = Cours.query.get(cours_id)
        if not cours:
            return jsonify({"message": "Cours non trouvé."}), 404

        db.session.delete(cours)
        db.session.commit()
        return jsonify({"message": "Cours supprimé avec succès."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erreur serveur.", "error": str(e)}), 500
    finally:
        db.session.remove()


@api_bp.route('/people')
@login_required
def get_people():
    """
    Renvoie la liste des élèves/judokas pour un cours donné (stocké dans la session).
    """
    try:
        id_cours = session.get('id_cours')
        if id_cours is None:
            return jsonify({"error": "id_cours est requis."}), 400

        # Validation id_cours
        try:
            id_cours = int(id_cours)
        except ValueError:
            return jsonify({"error": "id_cours doit être un entier valide."}), 400

        # Requête SQL pour récupérer les judokas et catégories correspondantes
        query_with_filter = """
        WITH AgeCalculation AS (
            SELECT 
                j.*, 
                CASE 
                    WHEN MONTH(CURRENT_DATE) < 9 THEN YEAR(CURRENT_DATE) - 1
                    ELSE YEAR(CURRENT_DATE)
                END - YEAR(j.NAISSANCE) AS age_reference
            FROM judoka j
        ),
        CategorieAgeJoin AS (
            SELECT 
                ac.*, 
                c.id AS id_categorie_age
            FROM AgeCalculation ac
            JOIN categorie_age c
                ON ac.age_reference BETWEEN c.age_mini AND c.age_maxi
        )
        SELECT 
            caj.*, 
            rcca.id_cours
        FROM CategorieAgeJoin caj
        JOIN relation_cours_categorie_age rcca
            ON caj.id_categorie_age = rcca.id_categorie_age
        WHERE rcca.id_cours = %s;
        """

        df = execute_query(query_with_filter, (id_cours,))
        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données (df is None)"}), 500
        
        # Ajout d'un champ 'status' par défaut
        df['status'] = 'non_defini'
        df = df.reset_index(drop=True)

        # Retraitement des champs pour l'affichage
        df['SEXE'] = df['SEXE'].apply(lambda x: 'Féminin' if x == 'F' else 'Masculin')
        df['NAISSANCE'] = pd.to_datetime(df['NAISSANCE']).dt.strftime('%d/%m/%Y')
        df['LICENCE'] = df['LICENCE'].apply(lambda x: 'Oui' if x != "" else 'Non')

        # Mise en cache dans la session
        session['data_cache'] = df.to_dict(orient='records')

        return jsonify(df.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données : {str(e)}"}), 500


@api_bp.route('/checkAppelStatus')
@login_required
def check_appel_status():
    """
    Renvoie la dernière date d'appel par cours, ainsi que l'id_appel correspondant.
    """
    try:
        query_with_filter = """
            WITH LatestAppel AS (
                SELECT 
                    a.id_cours, 
                    a.id_appel,
                    MAX(a.timestamp_appel) AS last_appel
                FROM appel a
                GROUP BY a.id_cours, a.id_appel
            )
            SELECT 
                c.id, 
                la.last_appel,
                la.id_appel
            FROM cours c
            LEFT JOIN LatestAppel la ON c.id = la.id_cours;
        """

        df = execute_query(query_with_filter)
        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données"}), 500

        # Marqueur si l'appel a eu lieu 'aujourd'hui'
        df['cours_today'] = df['last_appel'].apply(
            lambda x: x == datetime.now().date() if x is not None else False
        )
        # Convertir id_appel en str pour le JSON
        df['id_appel'] = df['id_appel'].apply(lambda x: str(x) if x is not None else None)

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500


@api_bp.route('/getListAppel')
@login_required
def get_list_appel():
    """
    Renvoie la liste des 20 derniers appels effectués (dernier timestamp par id_appel).
    """
    try:
        query_with_filter = """
            WITH dernier_appel AS (
                SELECT 
                    a.id_appel,
                    a.timestamp_appel,
                    c.nom_cours,
                    c.id AS id_cours,
                    a.id,
                    ROW_NUMBER() OVER (PARTITION BY a.id_appel ORDER BY a.timestamp_appel DESC) AS rn
                FROM appel a
                JOIN cours c ON c.id = a.id_cours
            )
            SELECT 
                timestamp_appel,
                nom_cours,
                id_cours,
                id_appel,
                id
            FROM dernier_appel
            WHERE rn = 1
            ORDER BY timestamp_appel DESC
            LIMIT 20;
        """
        df = execute_query(query_with_filter)
        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données"}), 500

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/getListCours')
@login_required
def get_list_cours():
    """
    Renvoie la liste de tous les cours enregistrés.
    """
    try:
        query = """
            SELECT 
                c.id,
                c.nom_cours,
                c.categorie_age
            FROM cours c
            ORDER BY c.nom_cours ASC;
        """
        df = execute_query(query)
        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données"}), 500

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/getCategFromCours')
@login_required
def get_categ_from_cours():
    """
    Renvoie la liste des id_categorie_age associées à un cours (lecture via session['id_cours']).
    """
    try:
        id_cours = session.get('id_cours')
        if not id_cours:
            return jsonify({"error": "id_cours manquant dans la session"}), 400

        query = """
            SELECT 
                rcca.id_categorie_age
            FROM relation_cours_categorie_age rcca 
            WHERE rcca.id_cours = %s;
        """
        df = execute_query(query, (id_cours,))
        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données"}), 500

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/getCoursFromUser')
@login_required
def get_cours_user():
    """
    Renvoie la liste des id_cours associés à l'utilisateur courant.
    """
    try:
        id_user = current_user.id
        query = """
            SELECT 
                ruc.id_user,
                ruc.id_cours
            FROM relation_user_cours ruc 
            WHERE ruc.id_user = %s;
        """
        df = execute_query(query, (id_user,))
        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données"}), 500

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/getListCategories')
@login_required
def get_list_categories():
    """
    Renvoie la liste des catégories d'âge existantes.
    """
    try:
        query = """
            SELECT 
                ca.id,
                ca.nom_categorie_age,
                ca.age_mini,
                ca.age_maxi
            FROM categorie_age ca
            ORDER BY ca.nom_categorie_age ASC;
        """
        df = execute_query(query)
        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données"}), 500

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/getAppelToCorrect')
@login_required
def get_appel_to_correct():
    """
    Renvoie la liste des enregistrements d'appel (Appel) pour un id_appel stocké en session, 
    avec un champ 'status' déterminé par les booléens (present, absent, retard, etc.).
    """
    try:
        id_appel = session.get('id_appel')
        if id_appel is None:
            return jsonify({"error": "id_appel est requis."}), 400

        try:
            id_appel = float(id_appel)
        except ValueError:
            return jsonify({"error": "id_appel doit être un nombre valide."}), 400

        query = """
            SELECT
                a.id,
                j.id AS id_judoka,
                j.PRENOM,
                j.NOM,
                c.id AS id_cours,
                c.nom_cours,
                a.timestamp_appel,
                a.present,
                a.absent,
                a.retard,
                a.absence_excuse,
                a.id_appel
            FROM appel a 
            JOIN cours c ON c.id = a.id_cours
            JOIN judoka j ON j.id = a.id_judoka
            WHERE a.id_appel = %s;
        """
        df = execute_query(query, (id_appel,))
        if df is None or df.empty:
            return jsonify({"error": "Aucune donnée trouvée pour l'id_appel fourni."}), 404

        def map_status(row):
            if row['present']:
                return 'present'
            if row['absent']:
                return 'absent'
            if row['retard']:
                return 'retard'
            if row['absence_excuse']:
                return 'absence_excuse'
            return 'non_defini'

        df['status'] = df.apply(map_status, axis=1)
        session['data_cache_correction'] = df.to_dict(orient='records')

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/updateStatusCorrection', methods=['POST'])
@login_required
def update_status_correction():
    """
    Met à jour, dans la variable de session, le statut (present/absent/retard/justifié) 
    d’un judoka sur un appel existant (mode correction).
    """
    try:
        data = request.get_json()
        id_cours = session.get('id_cours')
        data_cache = pd.DataFrame(session.get('data_cache_correction', []))
        id_appel = session.get('id_appel')

        if data_cache.empty:
            return jsonify({"error": "Aucune donnée en cache pour la correction"}), 400

        person_id = data.get('id')
        status = data.get('status')
        if person_id is None or status is None:
            return jsonify({"error": "Données invalides : 'id' et 'status' sont requis"}), 400

        # Filtrer la ligne correspondant à person_id
        index_list = data_cache.index[data_cache['id'] == person_id].tolist()
        if not index_list:
            return jsonify({"error": f"ID {person_id} introuvable dans la session"}), 404

        row_idx = index_list[0]

        # Mettre à jour
        data_cache.at[row_idx, 'status'] = status
        data_cache.at[row_idx, 'present'] = 1 if status == 'present' else 0
        data_cache.at[row_idx, 'absent'] = 1 if status == 'absent' else 0
        data_cache.at[row_idx, 'retard'] = 1 if status == 'retard' else 0
        data_cache.at[row_idx, 'absence_excuse'] = 1 if status == 'absent_justifie' else 0

        # Recompter les statuts
        status_counts = data_cache['status'].value_counts().to_dict()
        all_statuses = ['present', 'absent', 'retard', 'absent_justifie', 'non_defini']
        status_counts = {s: status_counts.get(s, 0) for s in all_statuses}
        status_counts['total'] = int(data_cache.shape[0])

        session['data_cache_correction'] = data_cache.to_dict(orient='records')

        return jsonify({
            "message": f"Statut mis à jour pour ID {person_id}.",
            "status_counts": status_counts
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erreur interne du serveur: {str(e)}"}), 500


@api_bp.route('/updateStatus', methods=['POST'])
@login_required
def update_status():
    """
    Met à jour le 'status' (présent, absent, retard, absent_justifie) 
    pour un élève dans la session 'data_cache' pendant l'appel en cours.
    """
    try:
        data = request.get_json()
        id_cours = session.get('id_cours')
        data_cache = pd.DataFrame(session.get('data_cache', []))

        person_id = data.get('id')
        status = data.get('status')
        if person_id is None or status is None:
            return jsonify({"error": "Données invalides : 'id' et 'status' sont requis."}), 400

        # Trouver l'enregistrement dans data_cache
        index_list = data_cache.index[data_cache['id'] == person_id].tolist()
        if not index_list:
            return jsonify({"error": f"ID {person_id} introuvable dans data_cache"}), 404

        row_idx = index_list[0]
        data_cache.at[row_idx, 'status'] = status

        # Recalculer les compteurs
        status_counts = data_cache['status'].value_counts().to_dict()
        all_statuses = ['present', 'absent', 'retard', 'absent_justifie', 'non_defini']
        status_counts = {s: status_counts.get(s, 0) for s in all_statuses}
        status_counts['total'] = int(data_cache.shape[0])

        # Mettre à jour la session
        session['data_cache'] = data_cache.to_dict(orient='records')

        return jsonify({
            "message": f"Statut mis à jour pour ID {person_id}.",
            "status_counts": status_counts
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erreur interne du serveur: {str(e)}"}), 500


@api_bp.route('/submitAttendance', methods=['POST'])
@login_required
def submit_attendance():
    """
    Insère en base les enregistrements d'un appel (présences, absences, etc.) 
    depuis la session d'appel en cours.
    """
    data = request.json
    try:
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        
        id_appel = datetime.now().timestamp()
        for id_judoka, details in data.items():
            id_cours = details.get('id_cours')
            timestamp_str = details.get('timestamp')
            status = details.get('status')

            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')

            present = (status == 'present')
            absent = (status == 'absent')
            retard = (status == 'retard')
            absence_excuse = (status == 'absent_justifie')

            appel = Appel(
                id_judoka=int(id_judoka),
                id_cours=int(id_cours),
                timestamp_appel=timestamp,
                present=present,
                absent=absent,
                retard=retard,
                absence_excuse=absence_excuse,
                id_appel=str(id_appel)
            )
            db.session.add(appel)

        db.session.commit()
        return jsonify({"message": "Les données ont été insérées avec succès"}), 201

    except Exception as e:
        db.session.rollback()
        db.session.remove()
        return jsonify({"error": str(e)}), 400
    finally:
        db.session.remove()


@api_bp.route('/submitAttendanceUpdate', methods=['POST'])
@login_required
def submit_attendance_update():
    """
    Met à jour l'historique d'appel existant (Appel), en changeant le statut et la date si besoin.
    """
    data = request.json
    try:
        if data is None:
            return jsonify({"error": "No data provided"}), 400

        # Ex : "appelDate" : "2025-01-01"
        date_appel = data.get('appelDate')
        if not date_appel:
            return jsonify({"error": "appelDate is missing"}), 400

        date_appel_dt = datetime.strptime(date_appel, '%Y-%m-%d')

        for key, details in data.items():
            # On skip la clé 'appelDate' elle-même
            if key == 'appelDate':
                continue

            status = details.get('status')
            id_appel = details.get('timestamp')
            if status is None or id_appel is None:
                return jsonify({"error": f"Missing fields in record {key}"}), 400

            present = (status == 'present')
            absent = (status == 'absent')
            retard = (status == 'retard')
            absence_excuse = (status == 'absent_justifie')

            existing_record = Appel.query.filter_by(id=int(key)).first()
            if existing_record:
                existing_record.present = present
                existing_record.absent = absent
                existing_record.retard = retard
                existing_record.absence_excuse = absence_excuse
                existing_record.timestamp_appel = date_appel_dt
            else:
                return jsonify({"error": f"Record not found for judoka {key}"}), 404

        db.session.commit()
        return jsonify({"message": "Les données ont été mises à jour avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        db.session.remove()
        return jsonify({"yo error": str(e)}), 400
    finally:
        db.session.remove()
