# Étape 1 : Utiliser une image Python 3.12 légère
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer les locales (optionnel, si nécessaire pour gérer les formats de date ou de langue)
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/*

# Configurer les locales (par exemple, pour le support des dates en français)
RUN echo "fr_FR.UTF-8 UTF-8" > /etc/locale.gen && locale-gen
ENV LC_ALL=fr_FR.UTF-8
ENV LANG=fr_FR.UTF-8
ENV LANGUAGE=fr_FR.UTF-8

# Copier l'ensemble du projet
COPY . .

# Rendre le script d'entrée exécutable (si nécessaire)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exposer le port sur lequel l'application s'exécutera
EXPOSE 80

# Spécifier la commande de démarrage de l'application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]


