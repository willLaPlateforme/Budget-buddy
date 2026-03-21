-- ============================================================
-- Budget Buddy — Database.sql
-- Compatible avec database.py / transactions.py / Window.py
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

--  Suppression des tables dans le bon ordre 
DROP TABLE IF EXISTS `transactions`;
DROP TABLE IF EXISTS `comptes`;
DROP TABLE IF EXISTS `users`;

--  Table users 
CREATE TABLE `users` (
  `id`              INT           NOT NULL AUTO_INCREMENT,
  `nom`             VARCHAR(255)  NOT NULL,
  `prenom`          VARCHAR(255)  NOT NULL,
  `email`           VARCHAR(255)  NOT NULL,
  `password_hash`   VARCHAR(255)  NOT NULL,
  `profile_picture` VARCHAR(255)  DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Données de test (mots de passe hachés avec bcrypt)
INSERT INTO `users` VALUES
(4, 'Doe',    'Jane',     'janedoe@test.com',        '$2b$12$8OaqFmItoREd9sdLIZPgSuu8dq9UZ8w9PaWsfIOtaLzq8fy6cLO7e', NULL),
(5, 'Staline','Joseph',   'josephstaline@test.com',  '$2b$12$FD3fUgtmhNYm3F.D/ia0/e2B2/.4O8UwkcP4dBT/MuRMZr0o.EVGa', NULL),
(6, 'Macron', 'Emmanuel', 'for_sure@test.com',       '$2b$12$rzjU/Faj0s0.1Oqr956Aaefqdvix2Aobp./tdqV07YtA72smcntES', NULL);

-- ── Table comptes ─────────────────────────────────────────────
CREATE TABLE `comptes` (
  `id`      INT            NOT NULL AUTO_INCREMENT,
  `user_id` INT            NOT NULL,
  `libelle` VARCHAR(100)   NOT NULL DEFAULT 'Compte principal',
  `solde`   DECIMAL(15,2)  NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_comptes_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Un compte principal par utilisateur de test
INSERT INTO `comptes` VALUES
(1, 4, 'Compte principal', 1490.00),
(2, 5, 'Compte principal',  -25.00),
(3, 6, 'Compte principal',  -50.35);

-- ── Table transactions ────────────────────────────────────────
CREATE TABLE `transactions` (
  `id`             INT            NOT NULL AUTO_INCREMENT,
  `reference`      VARCHAR(30)    NOT NULL,
  `description`    VARCHAR(255)   NOT NULL,
  `montant`        DECIMAL(15,2)  NOT NULL,
  `date`           DATE           NOT NULL,
  `type_op`        ENUM('dépôt','retrait','transfert') NOT NULL,
  `categorie`      VARCHAR(50)    NOT NULL DEFAULT 'autre',
  `compte_id`      INT            NOT NULL,
  `compte_dest_id` INT            DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_tx_compte`      FOREIGN KEY (`compte_id`)      REFERENCES `comptes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tx_compte_dest` FOREIGN KEY (`compte_dest_id`) REFERENCES `comptes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Données de test
INSERT INTO `transactions` VALUES
(4, 'REF001', 'Fromages',  -10.00,   '2024-01-01', 'retrait', 'repas',   1, NULL),
(5, 'REF002', 'Vodka',     -25.00,   '2024-01-01', 'retrait', 'loisir',  2, NULL),
(6, 'REF003', 'Restaurant',-50.35,   '2024-01-01', 'retrait', 'repas',   3, NULL),
(7, 'REF010', 'Salaire',  1500.00,   '2024-02-01', 'dépôt',   'salaire', 1, NULL);

SET FOREIGN_KEY_CHECKS = 1;
