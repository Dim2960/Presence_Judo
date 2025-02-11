# JudoApp - Application de Présence pour les Clubs de Judo

## 🌟 Description du Projet
JudoApp est une application web permettant de suivre la présence des judokas lors des entraînements. L'application facilite la gestion des listes de présence, l'analyse statistique des présences et l'exportation des données pour une meilleure gestion des clubs de judo.

## 💡 Fonctionnalités
- Gestion des présences aux entraînements
- Authentification des utilisateurs (professeurs, administrateurs, judokas)
- Affichage et correction des présences
- Exportation des données de présence
- Analyse statistique des fréquentations
- Interface web avec pages HTML, CSS et javascript
- Gestion des cours et des catégories d'âge
- Profils utilisateurs avec connexion à France Judo

## 💪 Technologies Utilisées
- **Back-end** : Python (Flask)
- **Front-end** : HTML, CSS, JavaScript (Swiper.js pour le carrousel)
- **Base de données** : MySQL (via SQLAlchemy)
- **Déploiement** : Docker, Heroku (via `Dockerfile`, `procfile`)
- **Scripts** : Manipulation de données, intégration BDD, scraping de licences

## 🛠 Installation et Exécution
### Prérequis
- Python >=3.12
- Docker
- Un gestionnaire de paquets comme `pip`
- Base de données MySQL configurée avec les variables d'environnement correctes

### Installation
Clonez le dépôt et installez les dépendances :
```bash
 git clone https://github.com/Dim2960/judoapp.git
 cd judoapp
 pip install -r requirements.txt
```

### Configuration de la Base de Données
Avant de lancer l'application, initialisez la base de données MySQL en exécutant le script SQL fourni :
```bash
 mysql -u root -p -h localhost < create-db-template.sql
```
Assurez-vous d'avoir configuré correctement les variables d'environnement pour la connexion à la base de données.

### Exemple de fichier `.env`
Créez un fichier `.env` dans le dossier judo_app avec le contenu suivant :
```ini
AZURE_MYSQL_USERNAME=root
AZURE_MYSQL_PASSWORD=[mySqlPassword]
AZURE_MYSQL_DATABASE=presenceJudo
AZURE_MYSQL_HOST=localhost
MYSQL_SSL_CA=certs/DigiCertGlobalRootCA.crt.pem
DEBUG=True

FLASK_SECRET_KEY=[yourFlaskSecretKey]
```
Remplacez `[mySqlPassword]` et `[yourFlaskSecretKey]` par vos valeurs réelles.

### Exécution
Démarrez l'application localement avec :
```bash
 python run.py
```
Ou avec Docker :
```bash
 docker build -t judoapp .
 docker run -p 5000:5000 --env-file .env judoapp
```
Pour un déploiement avec Docker Compose, utilisez :
```bash
 docker-compose up --build
```

## 🔍 Utilisation
1. Accédez à l'application via `http://localhost:5000`
2. Connectez-vous avec vos identifiants
3. Gérez les présences et consultez les statistiques
4. Ajoutez ou modifiez les cours et catégories
5. Consultez et mettez à jour votre profil utilisateur

## 🌐 Déploiement
L'application peut être déployée sur Heroku avec :
```bash
 heroku create judoapp
 git push heroku main
```
Ou sur un serveur Docker :
```bash
 docker build -t judoapp .
 docker run -d -p 5000:5000 --env-file .env judoapp
```

## 📚 Licence
Ce projet est un logiciel **propriétaire**. Tous droits réservés.

L'utilisation, la modification, la distribution et la reproduction du code source ou de toute partie de ce projet sont strictement interdites sans l'autorisation explicite du propriétaire. Pour toute demande d'utilisation, veuillez contacter l'auteur du projet.

## 📚 Contribution
Les contributions sont soumises à l'approbation du propriétaire du projet. Veuillez ouvrir une issue ou contacter l'équipe de développement pour toute suggestion ou amélioration.



