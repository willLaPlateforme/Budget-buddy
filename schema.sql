-- ============================================================
-- Budget Buddy — schema.sql
-- Schéma MySQL complet : users, comptes, transactions
-- Exécuter une seule fois pour initialiser la base de données
-- ============================================================

CREATE DATABASE IF NOT EXISTS budget_buddy
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE budget_buddy;

-- Table des utilisateurs (gérée par database.py / register.py)
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nom             VARCHAR(100)  NOT NULL,
    prenom          VARCHAR(100)  NOT NULL,
    email           VARCHAR(255)  UNIQUE NOT NULL,
    password_hash   VARCHAR(255)  NOT NULL,
    profile_picture VARCHAR(255)  DEFAULT NULL,
    created_at      DATETIME      DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table des comptes bancaires
CREATE TABLE IF NOT EXISTS comptes (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT          NOT NULL,
    libelle VARCHAR(100) NOT NULL DEFAULT 'Compte principal',
    solde   DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_comptes_user FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table des transactions
CREATE TABLE IF NOT EXISTS transactions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    reference       VARCHAR(30)   NOT NULL,
    description     VARCHAR(255)  NOT NULL,
    montant         DECIMAL(15,2) NOT NULL,
    date            DATE          NOT NULL,
    type_op         ENUM('dépôt','retrait','transfert') NOT NULL,
    categorie       VARCHAR(50)   NOT NULL DEFAULT 'autre',
    compte_id       INT           NOT NULL,
    compte_dest_id  INT           DEFAULT NULL,
    CONSTRAINT fk_tx_compte      FOREIGN KEY (compte_id)      REFERENCES comptes(id) ON DELETE CASCADE,
    CONSTRAINT fk_tx_compte_dest FOREIGN KEY (compte_dest_id) REFERENCES comptes(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
