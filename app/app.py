from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from datetime import datetime
import locale
import os

# locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8') # confi langue Française pour les dates


try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error as e:
    print(f"Warning: Locale not supported. Defaulting to system settings. Error: {e}")

app = Flask(__name__)


# db_user = os.getenv("AZURE_MYSQL_USERNAME")
# db_password = os.getenv("AZURE_MYSQL_PASSWORD")
# db_host = os.getenv("AZURE_MYSQL_HOST")
# db_name = os.getenv("AZURE_MYSQL_DATABASE")
# ssl_cert = os.getenv("MYSQL_SSL_CA")
# db_DEBUG = os.getenv("DEBUG")


db_user="xidnkathdd"
db_password="JF0$AQTq0xQ9nAC4"
db_name="judoapp-database"
db_host="judoapp-server.mysql.database.azure.com:3306"
ssl_cert = "certs/DigiCertGlobalRootCA.crt.pem"
db_DEBUG=True



app.config.update(
    SQLALCHEMY_DATABASE_URI=(
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?'
        f'ssl_ca={ssl_cert}' 
    ),
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "default_secret_key")
    # DEBUG=os.environ.get("DEBUG", "False").lower() in ["true", "1"]
)

# Initialise SQLAlchemy pour gérer la base de données.
db = SQLAlchemy(app)
#db.init_app(app)
# Initialise Flask-Login pour gérer les sessions utilisateur.
login_manager = LoginManager(app)
# Configuration de login_manager
login_manager.init_app(app)
# Définit la route de redirection pour les utilisateurs non connectés.
login_manager.login_view = 'login' # type: ignore


"""
Extration des data eleves + tratiaement pour trie par cours

"""

## todo : ajouter la cte pour modifier les cours si la colonne modif cours ref est à 1 en fonction de la table de relation des modif cours



global id_cours_cache, data_cache
id_cours_cache = int()
data_cache = {}

"""
Fin extraction data eleves
"""


# Modèle User
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('connexion_user.id'), nullable=False)
    prenom = db.Column(db.String(150), nullable=False)
    nom = db.Column(db.String(150), nullable=False)
    francejudo_id = db.Column(db.String(150), nullable=False)
    francejudo_pwd = db.Column(db.String(150), nullable=False)

    def __init__(self, id_user, prenom, nom, francejudo_id, francejudo_pwd):
        self.id_user = id_user
        self.prenom = prenom
        self.nom = nom
        self.francejudo_id = francejudo_id
        self.francejudo_pwd = francejudo_pwd

    # Relation avec Connexion_user
    connexion_user = db.relationship(
        'Connexion_user', 
        backref='linked_user', 
        viewonly=True, 
        overlaps="connexion_user,linked_user")



# Modèle Connexion_user
class Connexion_user(UserMixin, db.Model):

    __tablename__ = 'connexion_user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    password = db.Column(db.String(150), nullable=False)    
    
    # Relation avec User
    users = db.relationship(
        'User',
        lazy=True,
        viewonly=True,  # Utilisé pour une relation en lecture seule
        overlaps="linked_user,linked_connexion"
    )

    # Propriété pour accéder au prénom depuis la relation
    @property
    def prenom(self):
        # Retourne le prénom associé au Connexion_user
        user = User.query.filter_by(id_user=self.id).first()
        return user.prenom if user else None
    
    @property
    def nom(self):
        # Retourne le prénom associé au Connexion_user
        user = User.query.filter_by(id_user=self.id).first()
        return user.nom if user else None
    
    @property
    def francejudo_id(self):
        # Retourne le prénom associé au Connexion_user
        user = User.query.filter_by(id_user=self.id).first()
        return user.francejudo_id if user else None
    
    @property
    def francejudo_pwd(self):
        # Retourne le prénom associé au Connexion_user
        user = User.query.filter_by(id_user=self.id).first()
        return user.francejudo_pwd if user else None


class Cours(db.Model):
    __tablename__ = 'cours'
    id = db.Column(db.Integer, primary_key=True)
    nom_cours = db.Column(db.String(255), nullable=False)


class Appel(db.Model):
    __tablename__ = 'appel'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_judoka = db.Column(db.Integer, nullable=False)
    id_cours = db.Column(db.Integer, nullable=False)
    timestamp_appel = db.Column(db.DateTime, nullable=False)
    present = db.Column(db.Boolean, nullable=False, default=False)
    absent = db.Column(db.Boolean, nullable=False, default=False)
    retard = db.Column(db.Boolean, nullable=False, default=False)
    absence_excuse = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, id_judoka, id_cours, timestamp_appel, present, absent, retard, absence_excuse):
        self.id_judoka = id_judoka
        self.id_cours = id_cours
        self.timestamp_appel = timestamp_appel
        self.present = present
        self.absent = absent
        self.retard = retard
        self.absence_excuse = absence_excuse



@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(Connexion_user, int(user_id)) 
    except Exception as e :
        print(f"Erreur lors de la connexion : {e}")
        

@app.route('/')
@login_required
def index():
    return render_template('index.html')  


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Récupération des données du formulaire
        email = request.form.get('email')
        password = request.form.get('password')

        # Vérification que les champs sont remplis
        if not email or not password:
            flash('Veuillez renseigner tous les champs.')
            return redirect(url_for('login'))

        try:
            # Recherche de l'utilisateur dans la base de données
            user = Connexion_user.query.filter_by(email=email).first()

            # Vérification de l'utilisateur et du mot de passe
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Connexion réussie.')
                return redirect(url_for('index'))
            else:
                flash('Email ou mot de passe incorrect.')

        except Exception as e:
            # Gestion des erreurs liées à la base de données
            db.session.rollback()
            flash('Une erreur est survenue. Veuillez réessayer.')
            print(f"Erreur lors de la connexion : {e}")  # Log pour débogage

    # Si GET ou échec de connexion
    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Récupération des données du formulaire
        prenom = request.form.get('prenom')
        nom = request.form.get('nom')
        email = request.form.get('email')
        first_password = request.form.get('firstpassword')
        second_password = request.form.get('secondpassword')
        id_francejudo = request.form.get('idFranceJudo')
        pwd_francejudo = request.form.get('passwordFranceJudo')

        flash('prenom')

        # Vérification des mots de passe
        if first_password != second_password:
            flash('Les mots de passe ne correspondent pas.')
            return redirect(url_for('register'))

        # Hachage des mots de passe
        if not first_password:
            flash('Le mot de passe ne peut pas être vide.')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(first_password, method='pbkdf2:sha256')

        if not pwd_francejudo:
            flash('Le mot de passe France Judo ne peut pas être vide.')
            return redirect(url_for('register'))
        
        hashed_pwd_francejudo = generate_password_hash(pwd_francejudo, method='pbkdf2:sha256')

        try:
            # Insérer dans connexion_user
            new_connexion_user = Connexion_user(email=email, password=hashed_password)
            db.session.add(new_connexion_user)
            db.session.flush()  # Génére l'ID utilisateur sans valider la transaction

            # Utiliser l'ID généré pour l'insertion dans user
            new_user = User(
                id_user=new_connexion_user.id,  # L'ID généré automatiquement
                prenom=prenom,
                nom=nom,
                francejudo_id=id_francejudo,
                francejudo_pwd=hashed_pwd_francejudo
            )
            db.session.add(new_user)
            db.session.commit()  # Valider les deux insertions
            flash('Création du compte avec succès.')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()  # Annuler les changements en cas d'erreur
            flash('Une erreur est survenue lors de la création du compte.')
            print(f"Erreur lors de la création du compte : {e.__class__.__name__} - {e}")


    return render_template('register.html')


@app.route('/mon_profil')
@login_required
def mon_profil() :
    return render_template('profil_perso.html')


@app.route('/configuration_cours')
@login_required
def configuration_cours() :
    return render_template('config_cours.html')


@app.route('/appel_menu')
@login_required
def appel_menu() :
    # Récupérer les données de la table `cours`
    cours = Cours.query.order_by(Cours.nom_cours.asc()).all()
    
    return render_template('appel_menu.html', cours=cours)



@app.route('/appel_encours', methods=['POST'])
@login_required
def appel_encours():
    nom_cours = request.form.get('nom_cours')
    id_cours = request.form.get('id_cours')
    global id_cours_cache
    id_cours_cache = id_cours
    today = datetime.now().strftime("%A %d %B %Y")

    return render_template('appel_encours.html', nom_cours=nom_cours, id_cours=id_cours, today=today)


@app.route('/Statistique_generale')
@login_required
def Statistique_generale() :
    return render_template('visu_generale.html')


@app.route('/Statistique_groupe')
@login_required
def Statistique_groupe() :
    return render_template('visu_grp.html')


@app.route('/menu_correction_appel')
@login_required
def menu_correction_appel() :
    return render_template('menu_correction_appel.html')


@app.route('/api/people')
@login_required
def get_people():
    """Send list of people."""
    global data_cache, id_cours_cache  # Accéder au cache
    data_cache = {}
    try:
        id_cours = id_cours_cache
        if id_cours is None:
            return jsonify({"error": "id_cours est requis."}), 400

        # Vérifier si les données sont en cache
        if id_cours in data_cache:
            filtered_df = data_cache[id_cours]
        else:
            # Charger les données depuis la base si non en cache
            query_with_filter = f"""
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
            WHERE rcca.id_cours = {int(id_cours)};
            """
            filtered_df = pd.read_sql(query_with_filter, db.engine, params={"id_cours": int(id_cours)})
            data_cache[id_cours] = filtered_df  # Stocker en cache

        return jsonify(
                filtered_df.to_dict(orient='records')
                )
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données : {str(e)}"}), 500


@app.route('/api/statusCounts', methods=['GET'])
@login_required
def get_status_counts():
    try:
        # Calculer les compteurs
        status_counts = {}

        # Compléter les statuts avec zéro
        all_statuses = ['present', 'absent', 'retard', 'absent_justifie', 'non_defini']
        status_counts = {status: status_counts.get(status, 0) for status in all_statuses}

        # Comptage du nombre de personne total du groupe
        status_counts['non_defini'] = int(data_cache[id_cours_cache]['id'].count())

        return jsonify({"status_counts": status_counts}), 200

    except Exception as e:
        print("Erreur serveur get_statusCounts:", str(e))
        return jsonify({"error": "Erreur interne du serveur."}), 500



@app.route('/api/updateStatus', methods=['POST'])
@login_required
def update_status():
    try:
        data = request.get_json()

        person_id = data.get('id')
        status = data.get('status')

        if person_id is None or status is None:
            return jsonify({"error": "Données invalides : id et status requis."}), 400

        if data_cache[id_cours_cache] is None or 'id' not in data_cache[id_cours_cache].columns:
            return jsonify({"error": "Données introuvables ou structure invalide."}), 500

        # Trouver l'index correspondant
        index = data_cache[id_cours_cache].index[data_cache[id_cours_cache]['id'] == person_id].tolist()
        if not index:
            return jsonify({"error": f"ID {person_id} introuvable."}), 404

        # Mettre à jour le statut
        data_cache[id_cours_cache].loc[index[0], 'status'] = status
    
        # Calculer les compteurs de chaque statut
        status_counts = data_cache[id_cours_cache]['status'].value_counts().to_dict()

        # Compléter les statuts manquants avec zéro
        all_statuses = ['present', 'absent', 'retard', 'absent_justifie', 'non_defini']
        status_counts = {status: status_counts.get(status, 0) for status in all_statuses}

        # Comptage du nombre de personne total du groupe
        status_counts['non_defini'] = int(data_cache[id_cours_cache]['id'].count())

        return jsonify({
            "message": f"Statut mis à jour pour ID {person_id}.",
            "status_counts": status_counts
            }), 200


    except Exception as e:
        print("Erreur serveur :", str(e))
        return jsonify({"error": "Erreur interne du serveur."}), 500


# Endpoint pour soumettre les données d'appel
@app.route('/api/submitAttendance', methods=['POST'])
def submit_attendance():
    data = request.json
    # Traitement des données
    # enregistrement dans une base de données ou fichier
    print("Attendance data received:", data)
    try:
        if data is None:
            return jsonify({"error": "No data provided"}), 400

        for id_judoka, details in data.items():
            # Extraire les champs nécessaires
            id_cours = details.get('id_cours')
            timestamp = datetime.strptime(details.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%fZ')
            status = details.get('status')

            # Mapper le statut aux colonnes boolean
            present = status == 'present'
            absent = status == 'absent'
            retard = status == 'retard'
            absence_excuse = status == 'absent_justifie'

            # Créer un nouvel enregistrement
            appel = Appel(
                id_judoka=int(id_judoka),
                id_cours=int(id_cours),
                timestamp_appel=timestamp,
                present=bool(present),
                absent= bool(absent),
                retard= bool(retard),
                absence_excuse=bool(absence_excuse)
            )
            
            # Ajouter à la session
            db.session.add(appel)

        # Valider les modifications
        db.session.commit()

        return jsonify({"message": "Les données ont été insérées avec succès"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port=80)

