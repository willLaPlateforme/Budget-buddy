
# 💰 Budget Buddy
> Votre allié financier pour des dépenses malines et un budget équilibré

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2%2B-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Présentation

**Budget Buddy** est un outil de gestion financière personnelle développé en Python avec une interface graphique moderne (CustomTkinter) et une base de données MySQL. Il permet de suivre ses comptes bancaires, gérer ses transactions et visualiser ses finances en un coup d'œil.

### Fonctionnalités principales

- **Authentification sécurisée** — inscription, connexion, mot de passe haché avec bcrypt
- **Gestion des transactions** — dépôt, retrait, transfert entre comptes
- **Historique complet** — toutes les transactions avec filtres avancés multi-critères
- **Vue Globale** — KPIs, alertes de découvert, graphique revenus/dépenses
- **Budgets** — camemberts de répartition des dépenses et dépôts par catégorie
- **Épargne** — analyse du taux d'épargne et conseils personnalisés
- **Multi-comptes** — ajout de plusieurs comptes par utilisateur

---

## 🗂️ Structure du projet

```
budget_buddy/
│
├── main.py              # Point d'entrée — lancer l'application
├── database.py          # Connexion MySQL, authentification, gestion comptes
├── register.py          # Écrans de connexion et d'inscription (CustomTkinter)
├── transactions.py      # Logique métier : dépôt, retrait, transfert, filtres
├── ui_transactions.py   # Interface Transactions & Filtres
├── Window.py            # Dashboard principal (Vue Globale, Budgets, Épargne)
├── Menu_General.py      # Widgets partagés et graphique barres
│
├── Database.sql         # Script SQL complet (tables + données de test)
├── schema.sql           # Script SQL structure seule (sans données)
├── requirements.txt     # Dépendances Python
└── README.md
```

---

## ⚙️ Prérequis

Avant d'installer le projet, assurez-vous d'avoir :

| Logiciel | Version minimale | Lien |
|---|---|---|
| Python | 3.10+ | https://www.python.org/downloads/ |
| MySQL | 8.0+ | https://dev.mysql.com/downloads/ |
| MySQL Shell | 8.0+ | https://dev.mysql.com/downloads/shell/ |
| pip | inclus avec Python | — |

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/budget_buddy.git
cd budget_buddy
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

Ou manuellement :

```bash
pip install customtkinter mysql-connector-python bcrypt
```

> ⚠️ Si `pip` n'est pas reconnu, utilisez `python -m pip install ...`

### 3. Configurer MySQL

#### 3a. Créer la base de données

Ouvrez un terminal et connectez-vous à MySQL :

```bash
mysql -u root -p
```

Créez la base :

```sql
CREATE DATABASE IF NOT EXISTS budget_buddy CHARACTER SET utf8mb4;
EXIT;
```

#### 3b. Importer les tables et données de test

```bash
mysql -u root -p budget_buddy < Database.sql
```

> Remplacez `Database.sql` par le chemin complet si nécessaire :
> ```bash
> mysql -u root -p budget_buddy < "C:\Users\VotreNom\Desktop\budget_buddy\Database.sql"
> ```

#### 3c. Vérifier l'import

```bash
mysql -u root -p
```

```sql
USE budget_buddy;
SHOW TABLES;
```

Vous devez voir :
```
+------------------------+
| Tables_in_budget_buddy |
+------------------------+
| comptes                |
| transactions           |
| users                  |
+------------------------+
```

### 4. Configurer les identifiants MySQL

Ouvrez `database.py` et modifiez la fonction `get_connection()` :

```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",              # ← votre utilisateur MySQL
        password="votre_mdp",    # ← votre mot de passe MySQL
        database="budget_buddy"
    )
```

### 5. Lancer l'application

```bash
python main.py
```

---

## 👤 Comptes de test

Après import de `Database.sql`, trois comptes de démonstration sont disponibles.

> ⚠️ Les mots de passe originaux de ces comptes ne sont pas connus car ils ont été générés externement. **Créez votre propre compte** via l'interface pour commencer.

---

## 📝 Créer un compte

Au lancement, cliquez sur **"Créer un compte"** et remplissez :

| Champ | Règle |
|---|---|
| Nom | Obligatoire |
| Prénom | Obligatoire |
| Email | Format valide requis |
| Mot de passe | **10 caractères min.**, une majuscule, une minuscule, un chiffre, un caractère spécial |

Exemple de mot de passe valide : `Budget@2024!`

---

## 🖥️ Utilisation

### Vue Globale
- Solde total, dépenses du mois, épargne, nombre de comptes actifs
- Alertes automatiques (découvert, solde faible)
- Graphique revenus vs dépenses par mois

### Transactions
- **Dépôt** — créditer un compte
- **Retrait** — débiter un compte (vérifie le solde disponible)
- **Transfert** — entre deux comptes de l'application
- **Filtres avancés** — par date, type, catégorie, plage de dates, tri par montant

### Budgets
- Camemberts de répartition des dépenses et dépôts par catégorie
- Détail par catégorie avec solde net
- Totaux globaux

### Épargne
- Taux d'épargne calculé automatiquement
- Conseil personnalisé selon votre situation financière

---

## 🗄️ Schéma de la base de données

```sql
users
  id, nom, prenom, email, password_hash, profile_picture

comptes
  id, user_id (FK → users), libelle, solde

transactions
  id, reference, description, montant, date,
  type_op (dépôt|retrait|transfert), categorie,
  compte_id (FK → comptes), compte_dest_id (FK → comptes)
```

---

## 🔒 Sécurité

- Les mots de passe sont **hachés avec bcrypt** avant stockage
- Validation stricte du format email et de la force du mot de passe
- Les clés étrangères MySQL garantissent l'intégrité des données

---

## 🐛 Problèmes fréquents

### `Access denied for user`
→ Les identifiants MySQL dans `database.py` sont incorrects. Vérifiez `user` et `password`.

### `Table 'budget_buddy.comptes' doesn't exist`
→ La base n'a pas été initialisée. Relancez `mysql -u root -p budget_buddy < Database.sql`

### `No module named 'customtkinter'`
→ Lancez `pip install customtkinter` avec le bon Python (vérifiez `python --version`)

### `ModuleNotFoundError: No module named 'bcrypt'`
→ Lancez `pip install bcrypt`

---

## 👥 Équipe

Projet réalisé dans le cadre de la certification professionnelle — Développement Python & SQL.

| Membre | Rôle |
|---|---|
| Guillaume Ciampa | Authentification & Base de données |
| Melvin Vincent | Transactions & Filtres |
| Ilies Chapuis | Dashboard & Visualisation |

---

## 📦 Dépendances

```
customtkinter>=5.2.0
mysql-connector-python>=8.0.0
bcrypt>=4.0.0
```

---

## 📄 Licence

Ce projet est développé à des fins pédagogiques.
