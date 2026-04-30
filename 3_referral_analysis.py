import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import os
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

# Create an output directory for graphs
os.makedirs("output_graphs", exist_ok=True)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mamionmiam"]

def fetch_data(collection_name):
    return pd.DataFrame(list(db[collection_name].find({}, {"_id": 0})))

parrainages_df = fetch_data("parrainages")
clients_df = fetch_data("clients")
entreprises_df = fetch_data("entreprises")
shops_df = fetch_data("shops")

# 1. Quelle personne a parrainé le plus de personnes ? Qui a été parrainé par cette personne ?

top_sponsor_id = parrainages_df['idParrain'].value_counts().idxmax()
top_sponsor_count = parrainages_df['idParrain'].value_counts().max()
top_sponsor_info = clients_df[clients_df['id'] == top_sponsor_id].iloc[0]
print(f"Top Parrain: {top_sponsor_info['prenom']} {top_sponsor_info['nom']} (ID: {top_sponsor_id}) avec {top_sponsor_count} filleuls.")

filleuls_ids = parrainages_df[parrainages_df['idParrain'] == top_sponsor_id]['idFilleul']
filleuls_info = clients_df[clients_df['id'].isin(filleuls_ids)][['id', 'prenom', 'nom']]
print("Filleuls :")
print(filleuls_info.to_string(index=False))

# 2. Combien de H/F ont parrainé quelqu'un ? Ont été parrainé par quelqu'un ?

parrains_uniques_ids = parrainages_df['idParrain'].unique()
parrains_df = clients_df[clients_df['id'].isin(parrains_uniques_ids)]
print("Parrains par genre :")
print(parrains_df['genre'].value_counts())

# Filleuls uniques
filleuls_uniques_ids = parrainages_df['idFilleul'].unique()
filleuls_df = clients_df[clients_df['id'].isin(filleuls_uniques_ids)]
print("\nFilleuls par genre :")
print(filleuls_df['genre'].value_counts())

# 3 & 4. Répartition H/F des parrains / filleuls (Graphique)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

parrains_df['genre'].value_counts().plot.pie(ax=ax1, autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=90)
ax1.set_title("Répartition H/F des parrains")
ax1.set_ylabel('')

filleuls_df['genre'].value_counts().plot.pie(ax=ax2, autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=90)
ax2.set_title("Répartition H/F des filleuls")
ax2.set_ylabel('')

plt.savefig("output_graphs/repartition_hf_parrains_filleuls.png")
plt.close()

# 5. Répartition des parrains par tranche d'âge

def calculate_age(birthdate_str):
    if pd.isna(birthdate_str):
        return None
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

parrains_df = parrains_df.copy()
parrains_df['age'] = parrains_df['naissance'].apply(calculate_age)
bins = [18, 28, 38, 48, 58, 68, 120]
labels = ['18-27', '28-37', '38-47', '48-57', '58-67', '68+']
parrains_df['tranche_age'] = pd.cut(parrains_df['age'], bins=bins, labels=labels, right=False)
tranche_age_counts = parrains_df['tranche_age'].value_counts().sort_index()
print(tranche_age_counts)

plt.figure(figsize=(8, 5))
tranche_age_counts.plot(kind='bar', color='orange')
plt.title("Répartition des parrains par tranche d'âge")
plt.xlabel("Tranche d'âge")
plt.ylabel("Nombre de parrains")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output_graphs/repartition_age_parrains.png")
plt.close()



# 7. Quelle entreprise a le plus d'employés qui ont la carte de fidélité ?
# Extract siret from the entreprise column (dict)
clients_df['siret'] = clients_df['entreprise'].apply(lambda x: x.get('siret') if isinstance(x, dict) else None)
siret_counts = clients_df['siret'].value_counts().head(10)

# Merge to get company names
top_employers_df = pd.DataFrame({'siret': siret_counts.index, 'nb_employes': siret_counts.values})
top_employers_df = top_employers_df.merge(entreprises_df[['siret', 'nom']], on='siret', how='left')

top_siret = top_employers_df.iloc[0]['siret']
top_entreprise_name = top_employers_df.iloc[0]['nom']
top_count = top_employers_df.iloc[0]['nb_employes']
print(f"Entreprise N°1 : {top_entreprise_name} (SIRET: {top_siret}) avec {top_count} employés.")

# Create graph
plt.figure(figsize=(10, 6))
plt.barh(top_employers_df['nom'][::-1], top_employers_df['nb_employes'][::-1], color='teal')
plt.title("Top 10 entreprises avec le plus d'employés ayant la carte de fidélité")
plt.xlabel("Nombre d'employés")
plt.ylabel("Entreprise")
plt.tight_layout()
plt.savefig("output_graphs/top_entreprises_carte.png")
plt.close()

# 8. Quels domaines d'activité concentrent le plus d'entreprises ?

domain_counts = entreprises_df['domain_label'].value_counts().head(10)
print(domain_counts)

# 9. Quelles sont les 10 entreprises qui génèrent le plus de parrains?

# parrains_df already has the unique sponsors
parrains_df['siret'] = parrains_df['entreprise'].apply(lambda x: x.get('siret') if isinstance(x, dict) else None)
sponsors_siret_counts = parrains_df['siret'].value_counts().head(10)
# Merge to get company names
top_sponsors_companies = pd.DataFrame({'siret': sponsors_siret_counts.index, 'nb_parrains': sponsors_siret_counts.values})
top_sponsors_companies = top_sponsors_companies.merge(entreprises_df[['siret', 'nom']], on='siret', how='left')
print(top_sponsors_companies[['nom', 'nb_parrains']])



print("\nAnalyses de parrainage terminées. Graphes sauvegardés dans le dossier 'output_graphs'.")
