-- Active: 1737731483941@@judoapp-server.mysql.database.azure.com@3306@judoapp-database


USE `presenceJudo`;



CREATE TABLE connexion_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(150) NOT NULL
    CONSTRAINT fk_user FOREIGN KEY (id_user)
        REFERENCES connexion_user(id) 
        ON DELETE CASCADE
);

CREATE TABLE `user` (
    id INT AUTO_INCREMENT PRIMARY KEY,                      -- Clé primaire unique pour la table
    id_user INT NOT NULL,                                   -- Colonne pour la clé étrangère (non nulle)
    prenom VARCHAR(150) NOT NULL,                          -- Prénom obligatoire
    nom VARCHAR(150) NOT NULL,                             -- Nom obligatoire
    francejudo_id VARCHAR(150) NOT NULL,                   -- ID FranceJudo obligatoire
    francejudo_pwd VARCHAR(150) NOT NULL,                  -- Mot de passe FranceJudo obligatoire
    CONSTRAINT fk_user FOREIGN KEY (id_user)               -- Déclaration de la clé étrangère
        REFERENCES connexion_user(id)                      -- Référence à la table et colonne cible
        ON DELETE CASCADE                                   -- Supprime l'utilisateur associé si l'id_user est supprimé
        ON UPDATE CASCADE                                  -- Met à jour l'id_user en cas de modification
);


CREATE TABLE cours (
    id INT AUTO_INCREMENT PRIMARY KEY,                      -- Clé primaire unique pour la table
    nom_cours VARCHAR(150) NOT NULL,                        -- Nom du cours obligatoire
    categorie_age INT NOT NULL,                             -- Catégorie d'âge obligatoire
    ordre_cours INT NOT NULL,                               -- Ordre du cours à l'affichage
)


CREATE TABLE categorie_age (
    id INT AUTO_INCREMENT PRIMARY KEY,                      -- Clé primaire unique pour la table
    nom_categorie_age VARCHAR(150) NOT NULL,                -- Nom de la catégorie d'âge obligatoire,
    age_mini INT NOT NULL,                                  -- Age minimum obligatoire
    age_maxi INT NOT NULL                                   -- Age maximum obligatoire
)

CREATE TABLE relation_cours_categorie_age (
    id INT AUTO_INCREMENT PRIMARY KEY,                      -- Clé primaire unique pour la table
    id_cours INT NOT NULL,                                  -- Colonne pour la clé étrangère (non nulle)
    id_categorie_age INT NOT NULL,                          -- Colonne pour la clé étrangère (non nulle)
    CONSTRAINT fk_cours FOREIGN KEY (id_cours)               -- Déclaration de la clé étrangère
        REFERENCES cours(id)                                -- Référence à la table et colonne cible
        ON DELETE CASCADE                                   -- Supprime le cours associé si l'id_cours est supprimé
        ON UPDATE CASCADE,                                  -- Met à jour l'id_cours en cas de modification
    CONSTRAINT fk_categorie_age FOREIGN KEY (id_categorie_age) -- Déclaration de la clé étrangère
        REFERENCES categorie_age(id)                        -- Référence à la table et colonne cible
        ON DELETE CASCADE                                   -- Supprime la catégorie d'âge associée si l'id_categorie_age est supprimé
        ON UPDATE CASCADE -- Met à jour la référence si la catégorie d'âge est modifiée
        );


CREATE TABLE relation_user_cours (
    id INT AUTO_INCREMENT PRIMARY KEY,          -- Clé primaire
    id_user INT NOT NULL,                       -- Colonne avec clé étrangère vers user
    id_cours INT NOT NULL,                      -- Colonne avec clé étrangère vers cours
    CONSTRAINT fk_user_relation FOREIGN KEY (id_user)    -- Clé étrangère vers user
        REFERENCES user(id)
        ON DELETE CASCADE                       -- Supprime la relation si l'utilisateur est supprimé
        ON UPDATE CASCADE,                      -- Met à jour la référence si l'utilisateur est modifié
    CONSTRAINT fk_cours_relation FOREIGN KEY (id_cours)  -- Clé étrangère vers cours
        REFERENCES cours(id)
        ON DELETE CASCADE                       -- Supprime la relation si le cours est supprimé
        ON UPDATE CASCADE                       -- Met à jour la référence si le cours est modifié
);



CREATE TABLE judoka (
    id INT AUTO_INCREMENT PRIMARY KEY,                      -- Clé primaire unique pour la table
    LICENCE VARCHAR(50),
    NOM VARCHAR(100) NOT NULL,
    PRENOM VARCHAR(100) NOT NULL,
    SEXE CHAR(1) NOT NULL,
    NAISSANCE DATE,
    PORTABLE VARCHAR(15),
    modif_cours_ref BOOLEAN DEFAULT FALSE
);


CREATE TABLE appel (
    id INT AUTO_INCREMENT PRIMARY KEY,                      -- Clé primaire unique pour la table
    id_judoka INT NOT NULL,                                 -- Colonne pour la clé étrangère (non nulle)
    id_cours INT NOT NULL,                                  -- Colonne pour la clé étrangère (non nulle)
    timestamp_appel DATE NOT NULL,                               -- Date de l'appel obligatoire
    present BOOLEAN NOT NULL,                              -- Présence obligatoire
    absent BOOLEAN NOT NULL,                               -- Absence obligatoire
    retard BOOLEAN NOT NULL,        
    absence_excuse BOOLEAN NOT NULL,
    id_appel DECIMAL(16,6) NOT NULL,
    CONSTRAINT fk_judoka_appel FOREIGN KEY (id_judoka)             -- Déclaration de la clé étrangère
        REFERENCES judoka(id)                               -- Référence à la table et colonne cible
        ON DELETE CASCADE,
    CONSTRAINT fk_cours_appel FOREIGN KEY (id_cours)
        REFERENCES cours(id)
        ON DELETE CASCADE
);