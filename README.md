# JudoApp - Application de Présence pour les Clubs de Judo

## 🌟 Description du Projet
JudoApp est une application web permettant de suivre la présence des judokas lors des entraînements. L'application facilite la gestion des listes de présence, l'analyse statistique des présences et l'exportation des données pour une meilleure gestion des clubs de judo.

## 💡 Fonctionnalités
- Gestion des présences aux entraînements
- Authentification des utilisateurs (professeurs, administrateurs, judokas)
- Affichage et correction des présences
- Exportation des données de présence
- Analyse statistique des fréquentations
- Interface web avec pages HTML et CSS

## 💪 Technologies Utilisées
- **Back-end** : Python (Flask)
- **Front-end** : HTML, CSS
- **Base de données** : SQL (via des scripts SQL inclus)
- **Déploiement** : Docker, Heroku (via `Dockerfile`, `procfile`)
- **Scripts** : Manipulation de données, intégration BDD, scraping de licences

## 🛠 Installation et Exécution
### Prérequis
- Python 3.x
- Docker (optionnel, pour déploiement)
- Un gestionnaire de paquets comme `pip`

### Installation
Clonez le dépôt et installez les dépendances :
```bash
 git clone https://github.com/votre-repo/judoapp.git
 cd judoapp
 pip install -r requirements.txt
```

### Exécution
Démarrez l'application avec :
```bash
 python run.py
```
Ou avec Docker :
```bash
 docker build -t judoapp .
 docker run -p 5000:5000 judoapp
```

## 🔍 Utilisation
1. Accédez à l'application via `http://localhost:5000`
2. Connectez-vous avec vos identifiants
3. Gérez les présences et consultez les statistiques

## 🌐 Déploiement
L'application peut être déployée sur Heroku avec :
```bash
 heroku create judoapp
 git push heroku main
```

## 📚 Contribution
Les contributions sont les bienvenues ! Ouvrez une issue ou soumettez une pull request.

## 🏆 Licence
Ce projet est sous licence MIT.

---

📖 **Note** : Ce README est une version de base. N'hésitez pas à l'adapter selon vos besoins spécifiques !


