from neo4j import GraphDatabase
import pymongo
import json

uri = "bolt://localhost:7687"
user = "neo4j"
password = "mamionmiam"
driver = GraphDatabase.driver(uri, auth=(user, password))

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mamionmiam"]

def clear_db(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def load_sales_graph(tx):
    print("Loading Sales Graph into Neo4J...")
    
    # 1. Charger les categories et les rayons
    produits = list(db["produits"].find({}, {"_id": 0}))
    for p in produits:
        tx.run("""
            MERGE (r:Rayon {name: $rayon})
            MERGE (c:Categorie {name: $categorie})
            MERGE (c)-[:IN_RAYON]->(r)
            MERGE (prod:Produit {sku: $sku, label: $label})
            MERGE (prod)-[:IN_CAT]->(c)
        """, rayon=p.get('Rayon', 'Inconnu'), categorie=p.get('Categorie', 'Inconnu'), sku=p['SKU'], label=p.get('Label', 'Inconnu'))
        
    # 2. Charger les utilisateurs et les tickets
    achats = list(db["achats"].find({}, {"_id": 0}))
    for a in achats:
        acheteur_id = str(a['acheteur'])
        ticket_id = a['ticket']
        
        tx.run("""
            MERGE (u:User {id: $acheteur_id})
            MERGE (t:Ticket {id: $ticket_id})
            MERGE (u)-[:HAS_BOUGHT]->(t)
        """, acheteur_id=acheteur_id, ticket_id=ticket_id)
        
        details = a.get('detail', [])
        if isinstance(details, list):
            for d in details:
                if 'SKU' in d:
                    tx.run("""
                        MATCH (t:Ticket {id: $ticket_id})
                        MATCH (p:Produit {sku: $sku})
                        MERGE (t)-[:CONTAINS {qte: $qte, total: $total}]->(p)
                    """, ticket_id=ticket_id, sku=d['SKU'], qte=d.get('qte', 1), total=d.get('total', 0))
    print("Sales Graph loaded.")

def load_referral_graph(tx):
    print("Loading Referral Graph into Neo4J...")
    
    # 1. charger les magasins
    shops = list(db["shops"].find({}, {"_id": 0}))
    for s in shops:
        tx.run("MERGE (sh:Shop {id: $id, name: $name})", id=str(s['id']), name=s['name'])
        
    # 2. charger les entreprises
    entreprises = list(db["entreprises"].find({}, {"_id": 0}))
    for e in entreprises:
        tx.run("""
            MERGE (naf:NAF {code: $naf_code, label: $naf_label})
            MERGE (dom:Domain {code: $dom_code, label: $dom_label})
            MERGE (ent:Entreprise {siret: $siret, name: $name})
            MERGE (ent)-[:IN_NAF]->(naf)
            MERGE (ent)-[:IN_DOMAIN]->(dom)
        """, siret=str(e['siret']), name=e['nom'], 
             naf_code=e.get('naf_code', 'Unk'), naf_label=e.get('naf_label', 'Unk'),
             dom_code=e.get('domain_code', 'Unk'), dom_label=e.get('domain_label', 'Unk'))
             
    # 3. charger les clients et leurs entreprises
    clients = list(db["clients"].find({}, {"_id": 0}))
    for c in clients:
        tx.run("MERGE (u:Usr {id: $id, prenom: $prenom, nom: $nom})", 
               id=str(c['id']), prenom=c.get('prenom', ''), nom=c.get('nom', ''))
               
        if isinstance(c.get('entreprise'), dict) and 'siret' in c['entreprise']:
            tx.run("""
                MATCH (u:Usr {id: $id})
                MATCH (ent:Entreprise {siret: $siret})
                MERGE (u)-[:WORKS_AT]->(ent)
            """, id=str(c['id']), siret=str(c['entreprise']['siret']))
            
    # 4. charger les parrainages
    parrainages = list(db["parrainages"].find({}, {"_id": 0}))
    for p in parrainages:
        tx.run("""
            MATCH (parrain:Usr {id: $idParrain})
            MATCH (filleul:Usr {id: $idFilleul})
            MERGE (parrain)-[:SPONSOR {date: $dateParrainage}]->(filleul)
        """, idParrain=str(p['idParrain']), idFilleul=str(p['idFilleul']), dateParrainage=p.get('dateParrainage', ''))
        
    print("Referral Graph loaded.")

if __name__ == "__main__":
    with driver.session() as session:
        print("Clearing Neo4J DB...")
        session.execute_write(clear_db)
        
        session.execute_write(load_sales_graph)
        session.execute_write(load_referral_graph)
    
    driver.close()
    print("Neo4J Data loaded successfully.")
