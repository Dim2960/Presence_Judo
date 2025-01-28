from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session, g
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from datetime import datetime, timedelta
import locale
import os
from dotenv import load_dotenv



# Charger les variables d'environnement depuis le fichier .env à supp si deploiement azure 
# + supp commentaire ligne 58 (# f'ssl_ca={ssl_cert}')
# + inversioin dans la main de la ligne commentée et non commentée
load_dotenv()


try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error as e:
    print(f"Warning: Locale not supported. Defaulting to system settings. Error: {e}")



db_user = os.getenv("AZURE_MYSQL_USERNAME")
db_password = os.getenv("AZURE_MYSQL_PASSWORD")
db_host = os.getenv("AZURE_MYSQL_HOST")
db_name = os.getenv("AZURE_MYSQL_DATABASE")
ssl_cert = os.getenv("MYSQL_SSL_CA")
db_DEBUG = os.getenv("DEBUG")
secret_key = os.getenv("FLASK_SECRET_KEY")


app = Flask(__name__)
app.secret_key = secret_key # Nécessaire pour utiliser la session

# Configurations pour optimiser les sessions

app.config['SESSION_TYPE'] = 'filesystem'  # Stockage des sessions sur le serveur
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'  # Chemin de stockage des sessions (Linux/macOS)
app.config['SESSION_USE_SIGNER'] = True  # Sécurise les sessions avec une signature cryptographique
app.config['SESSION_KEY_PREFIX'] = 'judoapp_'  # Préfixe pour éviter les conflits

app.config['SESSION_COOKIE_SECURE'] = True  # Nécessite HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Empêche l'accès JavaScript
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protection contre les attaques CSRF


Session(app)  # Initialise la gestion des sessions


app.config.update(
    SQLALCHEMY_DATABASE_URI=(
        # f"mysql+pymysql://root:Dimarion1708&@localhost/presenceJudo"
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?'
        # f'ssl_ca={ssl_cert}' 
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

    

    def get_id(self):
        return str(self.id)
    

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
    categorie_age = db.Column(db.String(255), nullable=False)
    ordre_cours = db.Column(db.Integer, nullable=False)

    def __init__(self, nom_cours, categorie_age):
        self.nom_cours = nom_cours
        self.categorie_age = categorie_age


class RelationCours(db.Model):
    __tablename__ = 'relation_cours_categorie_age'
    id = db.Column(db.Integer, primary_key=True)
    id_cours = db.Column(db.Integer, nullable=False)
    id_categorie_age = db.Column(db.Integer, nullable=False)

    def __init__(self, id_cours, id_categorie_age):
        self.id_cours = id_cours
        self.id_categorie_age = id_categorie_age


class RelationUserCours(db.Model):
    __tablename__ = 'relation_user_cours'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, nullable=False)
    id_cours = db.Column(db.Integer, nullable=False)

    def __init__(self, id_user, id_cours):
        self.id_user = id_user
        self.id_cours = id_cours



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
    id_appel = db.Column(db.Numeric(10, 6), nullable=False)

    def __init__(self, id_judoka, id_cours, timestamp_appel, present, absent, retard, absence_excuse, id_appel):
        self.id_judoka = id_judoka
        self.id_cours = id_cours
        self.timestamp_appel = timestamp_appel
        self.present = present
        self.absent = absent
        self.retard = retard
        self.absence_excuse = absence_excuse
        self.id_appel = id_appel


def execute_query(query, params=None):
    try:
        with db.engine.connect() as connection:
            return pd.read_sql(query, connection, params=params)
    except Exception as e:
        print(f"Erreur SQL : {e}")
        return None
    

@app.teardown_appcontext
def shutdown_session(exception=None):
    try:
        db.session.remove()
    except Exception as e:
        print(f"Erreur lors de la fermeture de la session : {e}")


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(Connexion_user, int(user_id)) 
    except Exception as e :
        print(f"Erreur lors de la connexion : {e}")
        return None 
        

@app.route('/')
@login_required
def index():

    return render_template('index.html')  


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Veuillez renseigner tous les champs.', 'warning')
            return redirect(url_for('login'))

        user = Connexion_user.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            session.permanent = True  # Garde la session ouverte plus longtemps
            app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7) # Durée de la session

            # initialisation des variables sessions
            session['id_cours'] = 0
            session['id_appel'] = 0
            session['timestamp_cours'] = float()
            session['data_cache'] = {}
            session['data_cache_correction'] = {}

            flash('Connexion réussie.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Email ou mot de passe incorrect.', 'danger')
    
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
            db.session.remove()
            flash('Une erreur est survenue lors de la création du compte.')
            print(f"Erreur lors de la création du compte : {e.__class__.__name__} - {e}")


    return render_template('register.html')


@app.route('/mon_profil')
@login_required
def mon_profil() :
    return render_template('profil_perso.html')


@app.route('/configuration_cours', methods=['GET', 'POST'])
@login_required
def configuration_cours() :
    return render_template('config_cours.html')


@app.route('/appel_menu')
@login_required
def appel_menu() :
    
    # Récupérer les données de la table `cours`
    cours_list = db.session.query(Cours).order_by(Cours.ordre_cours.asc()).all()
    session['id_appel'] = 0


    return render_template('appel_menu.html', cours=cours_list)


@app.route('/correction_appel', methods=['POST'])
@login_required
def correction_appel():
    id_cours = request.form.get('id_cours')
    id_appel = request.form.get('id_appel')

    session['id_appel'] = id_appel
    session['id_cours'] = id_cours

    return render_template('correction_appel.html', id_cours=id_cours, id_appel=id_appel)


@app.route('/correction_cours', methods=['POST', 'GET'])
@login_required
def correction_cours():
    id_cours = request.form.get('id_cours')
    session['id_cours'] = id_cours
    nom_cours = request.form.get('nom_cours', '')

    return render_template('correction_cours.html', id_cours=id_cours, nom_cours=nom_cours)


@app.route('/api/addCours', methods=['GET', 'POST'])
@login_required
def add_cours():
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

        # Ajouter le cours à la base de données cours
        new_cours = Cours(nom_cours=nom_cours, categorie_age=categorie_age[0])
        db.session.add(new_cours)
        db.session.commit()

        # Ajouter à la base de données relation_cours_categorie_age
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


@app.route('/api/updateCours/<int:id_cours>', methods=['PUT'])
@login_required
def update_cours(id_cours):
    try:
        data = request.get_json()
        nom_cours = data.get('nom')
        categorie_age = data.get('categories')
        print("categ : ",categorie_age)

        # Vérifier si le cours existe
        cours = Cours.query.get(id_cours)
        if not cours:
            return jsonify({'error': 'Cours non trouvé'}), 404

        # Validation des données
        if not nom_cours:
            return jsonify({'error': 'Le nom du cours est requis'}), 400

        if not categorie_age or not isinstance(categorie_age, list):
            return jsonify({'error': 'Au moins une catégorie d\'âge est requise'}), 400

        # Mise à jour des informations du cours
        cours.nom_cours = nom_cours
        db.session.commit()

        # Mise à jour des relations cours-catégorie
        # Supprimer les relations existantes pour ce cours
        RelationCours.query.filter_by(id_cours=id_cours).delete()

        # Ajouter les nouvelles relations
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


@app.route('/api/updateCoursUser/<int:id_user>', methods=['PUT'])
@login_required
def update_coursUser(id_user):
    try:
        data = request.get_json()
        cours = data.get('coursUser')
        print("data : ", data)

        # Vérifier si le cours existe
        user_record = User.query.get(id_user)
        if not user_record:
            return jsonify({'error': 'id_user non trouvé'}), 404

        # Validation des données
        if not cours or not isinstance(cours, list):
            return jsonify({'error': 'Au moins un cours est requis'}), 400

        print('ixi')
        # Mise à jour des relations cours-catégorie
        # Supprimer les relations existantes pour ce cours
        RelationUserCours.query.filter_by(id_user=id_user).delete()

        print('la')
        # Ajouter les nouvelles relations
        for row_cours in cours:
            print("row_cours : ", row_cours)
            new_relation = RelationUserCours(id_user=id_user, id_cours=row_cours)
            db.session.add(new_relation)

        db.session.commit()

        return jsonify({'message': 'Cours mis à jour avec succès', 'id_user': id_user}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour du cours : {str(e)}'}), 500
    finally:
        db.session.remove()



@app.route('/delete-cours/<int:cours_id>', methods=['DELETE'])
def delete_cours(cours_id):
    try:
        cours = Cours.query.get(cours_id)
        if not cours:
            return jsonify({"message": "Cours non trouvé."}), 404

        db.session.delete(cours)
        db.session.commit()
        return jsonify({"message": "Cours supprimé avec succès."}), 200

    except Exception as e:
        return jsonify({"message": "Erreur serveur.", "error": str(e)}), 500


@app.route('/appel_encours', methods=['POST'])
@login_required
def appel_encours():
    nom_cours = request.form.get('nom_cours')
    id_cours = request.form.get('id_cours')


    # Stocker dans la session
    if session['id_cours'] != id_cours:
        session['data_cache'] = dict()

    session['id_cours'] = id_cours

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
    try:

        id_cours = session.get('id_cours')

        if id_cours is None:
            return jsonify({"error": "id_cours est requis."}), 400

        try:
            id_cours = int(id_cours)
        except ValueError:
            return jsonify({"error": "id_cours doit être un entier valide."}), 400

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
        WHERE rcca.id_cours = %s;
        """


        # df = pd.read_sql(query_with_filter, connection, params={"id_cours": int(id_cours)})
        df = execute_query(query_with_filter, (id_cours,))

        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données. df est None"}), 500
        
        df['status'] = 'non_defini'
        df = df.reset_index()

        
        # retravail des infos pour affichage
        df['SEXE'] = df['SEXE'].apply(lambda x: 'Féminin' if x == 'F' else 'Masculin')
        df['NAISSANCE'] = pd.to_datetime(df['NAISSANCE'])
        df['NAISSANCE'] = df['NAISSANCE'].dt.strftime('%d/%m/%Y')
        df['LICENCE'] = df['LICENCE'].apply(lambda x: 'Oui' if x != "" else 'Non')
        

        session['data_cache'] = df.to_dict(orient='records')  

        return jsonify(
                df.to_dict(orient='records')
                )
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données : {str(e)}"}), 500




@app.route('/api/checkAppelStatus')
@login_required
def checkappelDateCours():
    try:
        # Charger les données 
        query_with_filter = f"""
            WITH LatestAppel AS (
                SELECT 
                    id_cours, 
                    id_appel,
                    MAX(timestamp_appel) AS last_appel
                FROM 
                    appel
                GROUP BY 
                    id_cours, id_appel
            )
            SELECT 
                c.id, 
                la.last_appel,
                la.id_appel
            FROM 
                cours c
            LEFT JOIN 
                LatestAppel la ON c.id = la.id_cours;
        """
        

        df = execute_query(query_with_filter)

        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données Checkcouple idcours et date"}), 500
        else:
            df['cours_today'] = df['last_appel'].apply(lambda x: x == datetime.now().date() if x is not None else False)
            df['id_appel'] = df['id_appel'].apply(lambda x: str(x) if x is not None else None)
            
        return jsonify(
                df.to_dict(orient='records')
                )
    
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données Checkcouple idcours et date : {str(e)}"}), 500


@app.route('/api/getListAppel')
@login_required
def getListAppel():

    try:
        # Charger les données 
        query_with_filter = f"""
            WITH dernier_appel AS (
                SELECT 
                    a.id_appel,
                    a.timestamp_appel,
                    c.nom_cours,
                    c.id AS id_cours,
                    a.id,
                    ROW_NUMBER() OVER (PARTITION BY a.id_appel ORDER BY a.timestamp_appel DESC) AS rn
                FROM 
                    appel a
                JOIN 
                    cours c ON c.id = a.id_cours
            )
            SELECT 
                timestamp_appel,
                nom_cours,
                id_cours,
                id_appel,
                id
            FROM 
                dernier_appel
            WHERE 
                rn = 1
            ORDER BY 
                timestamp_appel DESC
            LIMIT 20;
        """

        df = execute_query(query_with_filter)

        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données. df est None"}), 500

        
        return jsonify(
                df.to_dict(orient='records')
                )
    
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données de liste des appels : {str(e)}"}), 500


@app.route('/api/getListCours')
@login_required
def getListCours():

    try:
        # Charger les données 
        query_with_filter = f"""
            SELECT 
                c.id,
                c.nom_cours,
                c.categorie_age
            FROM 
                cours c
            ORDER BY 
                c.nom_cours ASC;
        """

        df = execute_query(query_with_filter)

        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données. df est None"}), 500

        
        return jsonify(
                df.to_dict(orient='records')
                )
    
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données de liste des appels : {str(e)}"}), 500


@app.route('/api/getCategFromCours')
@login_required
def getCours():
    try:
        id_cours= session['id_cours']

        # Charger les données 
        query_with_filter = f"""
            SELECT 
                rcca.id_categorie_age
            FROM 
                relation_cours_categorie_age rcca 
            WHERE
                rcca.id_cours = %s;
        """

        df = execute_query(query_with_filter, (id_cours,))

        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données. df est None"}), 500
        
        return jsonify(
                df.to_dict(orient='records')
                )
    
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données de liste des appels : {str(e)}"}), 500


@app.route('/api/getCoursFromUser')
@login_required
def getCoursUser():
    try:
        id_user= current_user.id

        print(id_user)
        # Charger les données 
        query_with_filter = f"""
            SELECT 
                ruc.id_user,
                id_cours
            FROM 
                relation_user_cours ruc 
            WHERE
                ruc.id_user = %s;
        """

        df = execute_query(query_with_filter, (id_user,))

        print(df)

        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données. df est None"}), 500

        
        return jsonify(
                df.to_dict(orient='records')
                )
    
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données de liste des appels : {str(e)}"}), 500
    

@app.route('/api/getListCategories')
@login_required
def getListCateg():

    try:
        # Charger les données 
        query_with_filter = f"""
            SELECT 
                ca.id,
                ca.nom_categorie_age,
                ca.age_mini,
                ca.age_maxi
            FROM 
                categorie_age ca
            ORDER BY 
                ca.nom_categorie_age ASC;
        """

        df = execute_query(query_with_filter)

        if df is None:
            return jsonify({"error": "Erreur lors de la récupération des données. df est None"}), 500

        
        return jsonify(
                df.to_dict(orient='records')
                )
    
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données de liste des appels : {str(e)}"}), 500
    

@app.route('/api/getAppelToCorrect')
@login_required
def getAppelToCorrect():

    try:
    
        id_appel = session.get('id_appel')

        if id_appel is None:
            return jsonify({"error": "id_appel est requis."}), 400

        try:
            id_appel = float(id_appel)
        except ValueError:
            return jsonify({"error": "id_appel doit être un entier valide."}), 400
        
        

        # Charger les données 
        query_with_filter = """
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

        df = execute_query(query_with_filter, (id_appel,))

        if df is None or df.empty:
            return jsonify({"error": "Aucune donnée trouvée pour l'id_appel fourni."}), 404

        # Définition du statut en fonction des colonnes booléennes
        def map_status(row):
            if row['present']:
                return 'present'
            elif row['absent']:
                return 'absent'
            elif row['retard']:
                return 'retard'
            elif row['absence_excuse']:
                return 'absence_excuse'
            return 'non_defini'

        df['status'] = df.apply(map_status, axis=1)

        # Mise en cache des données dans la session
        session['data_cache_correction'] = df.to_dict(orient='records')

        return jsonify(df.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des données de liste des appels : {str(e)}"}), 500




@app.route('/api/updateStatusCorrection', methods=['POST'])
@login_required
def update_status_correction():

    try:
        data = request.get_json()
        # Récupérer depuis la session
        id_cours = session.get('id_cours')
        data_cache = pd.DataFrame(session.get('data_cache_correction'))
        id_appel = session.get('id_appel')


        def map_status(row):
            if row['present']:
                return 'present'
            elif row['absent']:
                return 'absent'
            elif row['retard']:
                return 'retard'
            elif row['absence_excuse']:
                return 'absence_excuse'
            else:
                return 'non_defini'

        data_cache['status'] = data_cache.apply(map_status, axis=1)

        person_id = data.get('id')
        status = data.get('status')


        if person_id is None or status is None:
            return jsonify({"error": "Données invalides : id et status requis."}), 400

        if data_cache[data_cache['id_cours']==id_cours] is None or 'id' not in data_cache[data_cache['id_cours']==id_cours].columns:
            return jsonify({"error": "Données introuvables ou structure invalide."}), 500
        

        # Trouver l'index correspondant
        index = data_cache.index[data_cache['id'] == person_id].tolist()


        if not index or index is None:
            return jsonify({"error": f"ID {person_id} introuvable."}), 404

        # Mettre à jour le statut
        data_cache.loc[index[0], 'status'] = status
        # mise à jour des pd.series --> present, absent, absece_justifie, retard
        if status == 'present':
            data_cache.loc[index[0], 'present'] = 1
            data_cache.loc[index[0], 'absent'] = 0
            data_cache.loc[index[0], 'retard'] = 0
            data_cache.loc[index[0], 'absence_excuse'] = 0
            
        elif status == 'absent':
            data_cache.loc[index[0], 'present'] = 0
            data_cache.loc[index[0], 'absent'] = 1
            data_cache.loc[index[0], 'retard'] = 0
            data_cache.loc[index[0], 'absence_excuse'] = 0

        elif status == 'retard':
            data_cache.loc[index[0], 'present'] = 0
            data_cache.loc[index[0], 'absent'] = 0
            data_cache.loc[index[0], 'retard'] = 1
            data_cache.loc[index[0], 'absence_excuse'] = 0

        elif status == 'absent_justifie':
            data_cache.loc[index[0], 'present'] = 0
            data_cache.loc[index[0], 'absent'] = 0
            data_cache.loc[index[0], 'retard'] = 0
            data_cache.loc[index[0], 'absence_excuse'] = 1

        # Calculer les compteurs de chaque statut
        status_counts = data_cache['status'].value_counts().to_dict()

        # Compléter les statuts manquants avec zéro
        all_statuses = ['present', 'absent', 'retard', 'absent_justifie', 'non_defini']
        status_counts = {status: status_counts.get(status, 0) for status in all_statuses}

        # Comptage du nombre de personne total du groupe
        status_counts['total'] = int(data_cache['id'].count())


        session['data_cache_correction'] = data_cache.to_dict(orient='records') 


        return jsonify({
            "message": f"Statut mis à jour pour ID {person_id}.",
            "status_counts": status_counts
            }), 200


    except Exception as e:
        print("Erreur serveur :", str(e))
        return jsonify({"error": "Erreur interne du serveur."}), 500


@app.route('/api/updateStatus', methods=['POST'])
@login_required
def update_status():

    try:
        data = request.get_json()
        # Récupérer depuis la session
        id_cours = session.get('id_cours')
        data_cache = pd.DataFrame(session.get('data_cache'))



        person_id = data.get('id')
        status = data.get('status')


        if person_id is None or status is None:
            return jsonify({"error": "Données invalides : id et status requis."}), 400

        if data_cache[data_cache['id_cours']==id_cours] is None or 'id' not in data_cache[data_cache['id_cours']==id_cours].columns:
            return jsonify({"error": "Données introuvables ou structure invalide."}), 500
        

        # Trouver l'index correspondant
        index = data_cache.index[data_cache['id'] == person_id].tolist()

        if not index:
            return jsonify({"error": f"ID {person_id} introuvable."}), 404


        # Mettre à jour le statut
        data_cache.loc[index[0], 'status'] = status

        # Calculer les compteurs de chaque statut
        status_counts = data_cache['status'].value_counts().to_dict()

        # Compléter les statuts manquants avec zéro
        all_statuses = ['present', 'absent', 'retard', 'absent_justifie', 'non_defini']
        status_counts = {status: status_counts.get(status, 0) for status in all_statuses}

        # Comptage du nombre de personne total du groupe
        status_counts['total'] = int(data_cache['id'].count())

        session['data_cache'] = data_cache.to_dict(orient='records') 

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
        
        id_appel = datetime.now().timestamp()

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
                absence_excuse=bool(absence_excuse),
                id_appel=str(id_appel)
            )
            
            # Ajouter à la session
            db.session.add(appel)

        # Valider les modifications
        db.session.commit()

        return jsonify({"message": "Les données ont été insérées avec succès"}), 201

    except Exception as e:
        db.session.rollback()
        db.session.remove()
        return jsonify({"error": str(e)}), 400

    finally:
        db.session.remove()


@app.route('/api/submitAttendanceUpdate', methods=['POST'])
def submit_attendance_update():
    data = request.json

    try:
        if data is None:
            return jsonify({"error": "No data provided"}), 400

        for id_enregistrement, details in data.items():
            # Extract necessary fields

            status = details.get('status')
            id_appel = details.get('timestamp')


            # Map status to boolean columns
            present = status == 'present'
            absent = status == 'absent'
            retard = status == 'retard'
            absence_excuse = status == 'absent_justifie'

            # Find existing record
            existing_record = Appel.query.filter_by(
                id=int(id_enregistrement),
                id_appel=float(id_appel)
            ).first()

            if existing_record:
                # Update existing record
                existing_record.present = bool(present)
                existing_record.absent = bool(absent)
                existing_record.retard = bool(retard) 
                existing_record.absence_excuse = bool(absence_excuse)
            else:
                # If record doesn't exist, return error
                return jsonify({"error": f"Record not found for judoka {id_enregistrement}"}), 404

        # Commit all updates
        db.session.commit()
        return jsonify({"message": "Les données ont été mises à jour avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        db.session.remove()
        return jsonify({"yo error": str(e)}), 400

    finally:
        db.session.remove()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True, host='0.0.0.0', port=80)

