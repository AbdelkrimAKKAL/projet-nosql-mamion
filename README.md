# Mamion Miam - Projet NoSQL

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


2. **Analyse des ventes** :
   ```bash
   python 2_sales_analysis.py
   ```


3. **Analyse du parrainage** :
   ```bash
   python 3_referral_analysis.py
   ```
   

4. **Chargement de la base Neo4J** :
   ```bash
   python 4_load_neo4j.py
   ```
  

