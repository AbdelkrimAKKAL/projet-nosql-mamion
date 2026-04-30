# Mamion Miam - Projet NoSQL

Ce projet répond aux exigences de l'analyse des données de la chaîne de magasins Mamion Miam.

## Mise en place

1. Assurez-vous que Docker et Docker Compose sont installés.
2. Lancez les bases de données (MongoDB et Neo4J) :
   ```bash
   docker-compose up -d
   ```
   L'interface de Neo4J sera disponible sur `http://localhost:7474` (Identifiant: `neo4j`, Mot de passe: `mamionmiam`).
3. Créez et activez l'environnement virtuel, puis installez les dépendances :
   ```bash
   python -m venv venv
   # Sur Windows:
   .\venv\Scripts\activate
   # Sur Linux/Mac:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

## Ordre d'exécution des scripts

1. **Chargement de la base MongoDB** (Source de vérité) :
   ```bash
   python 1_load_mongodb.py
   ```
   Ce script lit les fichiers JSON du dossier `mamionmiam/mamionmiam` et crée une collection pour chaque type de données dans la base `mamionmiam`.

2. **Analyse des ventes** :
   ```bash
   python 2_sales_analysis.py
   ```
   Répond aux questions sur les ventes en utilisant MongoDB et Pandas. Génère des graphiques Matplotlib dans le dossier `output_graphs/`.

3. **Analyse du parrainage** :
   ```bash
   python 3_referral_analysis.py
   ```
   Répond aux questions sur les parrainages. Utilise MongoDB, Pandas et NetworkX pour les parcours de graphes. Génère également des graphiques.

4. **Chargement de la base Neo4J** :
   ```bash
   python 4_load_neo4j.py
   ```
   Si vous souhaitez faire des requêtes Cypher directement sur Neo4J, ce script vide la base et recrée les graphes de ventes et de parrainages selon les schémas définis dans le sujet.

## Contenu généré

- Les scripts d'analyses impriment les réponses aux questions dans la console.
- Les graphes Matplotlib exportés (PNG) se trouvent dans le répertoire `output_graphs/`.
- `requirements.txt` et `.gitignore` sont correctement configurés.
