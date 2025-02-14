# Copyright (c) 2025 Dimitri Lefebvre
# Tous droits réservés. Ce fichier fait partie d'un logiciel propriétaire.
# Son utilisation est soumise aux conditions définies dans le fichier LICENSE.

from .extensions import db
from flask_login import UserMixin
import pandas as pd

class User(db.Model):
    """
    Modèle représentant un utilisateur.
    """
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

class Connexion_user(UserMixin, db.Model):
    """
    Modèle représentant un utilisateur pour la connexion.
    """
    __tablename__ = 'connexion_user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password
    
    def get_id(self):
        return str(self.id)
    
    # Relation avec User
    users = db.relationship(
        'User',
        lazy=True,
        viewonly=True,
        overlaps="linked_user,linked_connexion"
    )

    @property
    def prenom(self):
        """Retourne le prénom associé à l'utilisateur."""
        user = User.query.filter_by(id_user=self.id).first()
        return user.prenom if user else None
    
    @property
    def nom(self):
        """Retourne le nom associé à l'utilisateur."""
        user = User.query.filter_by(id_user=self.id).first()
        return user.nom if user else None
    
    @property
    def francejudo_id(self):
        """Retourne l'ID France Judo associé à l'utilisateur."""
        user = User.query.filter_by(id_user=self.id).first()
        return user.francejudo_id if user else None
    
    @property
    def francejudo_pwd(self):
        """Retourne le mot de passe France Judo associé à l'utilisateur."""
        user = User.query.filter_by(id_user=self.id).first()
        return user.francejudo_pwd if user else None

class Cours(db.Model):
    """
    Modèle représentant un cours.
    """
    __tablename__ = 'cours'
    id = db.Column(db.Integer, primary_key=True)
    nom_cours = db.Column(db.String(255), nullable=False)
    categorie_age = db.Column(db.String(255), nullable=False)
    ordre_cours = db.Column(db.Integer, nullable=False)

    def __init__(self, nom_cours: str, categorie_age):
        self.nom_cours = nom_cours
        self.categorie_age = categorie_age

class RelationCours(db.Model):
    """
    Modèle représentant la relation entre un cours et une catégorie d'âge.
    """
    __tablename__ = 'relation_cours_categorie_age'
    id = db.Column(db.Integer, primary_key=True)
    id_cours = db.Column(db.Integer, nullable=False)
    id_categorie_age = db.Column(db.Integer, nullable=False)

    def __init__(self, id_cours, id_categorie_age):
        self.id_cours = id_cours
        self.id_categorie_age = id_categorie_age

class RelationUserCours(db.Model):
    """
    Modèle représentant la relation entre un utilisateur et un cours.
    """
    __tablename__ = 'relation_user_cours'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, nullable=False)
    id_cours = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id: int, cours_id: int):
        self.id_user = user_id
        self.id_cours = cours_id

class Appel(db.Model):
    """
    Modèle représentant un appel de présence.
    """
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
    """
    Exécute une requête SQL et retourne les résultats sous forme de DataFrame.
    """
    try:
        with db.engine.connect() as connection:
            return pd.read_sql(query, connection, params=params)
    except Exception as e:
        print(f"Erreur SQL : {e}")
        return None