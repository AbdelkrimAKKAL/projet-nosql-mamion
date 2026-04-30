import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import os

# Create an output directory for graphs
os.makedirs("output_graphs", exist_ok=True)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mamionmiam"]

def fetch_data(collection_name):
    return pd.DataFrame(list(db[collection_name].find({}, {"_id": 0})))

produits_df = fetch_data("produits")
achats_df = fetch_data("achats")
clients_df = fetch_data("clients")

# 1. 10 catégories avec le plus de produit

cat_prod_counts = produits_df['Categorie'].value_counts().head(10)
print(cat_prod_counts)

# Graph for 1
plt.figure(figsize=(10, 6))
cat_prod_counts.plot(kind='barh', color='skyblue')
plt.title('Top 10 catégories avec le plus de produits')
plt.xlabel('Nombre de produits')
plt.ylabel('Catégorie')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("output_graphs/top_10_categories.png")
plt.close()

# 2. 10 rayons avec le plus de catégories

rayon_cat_counts = produits_df.groupby('Rayon')['Categorie'].nunique().sort_values(ascending=False).head(10)
print(rayon_cat_counts)

# 3. 10 rayons avec le plus de produits

rayon_prod_counts = produits_df['Rayon'].value_counts().head(10)
print(rayon_prod_counts)


# 5. Catégories avec le plus de ligne de vente
cat_lines = sales_merged['Categorie'].value_counts().head(10)
print(cat_lines)

# Graph for 5
plt.figure(figsize=(10, 6))
cat_lines.plot(kind='bar', color='lightcoral')
plt.title('Top 10 catégories par nombre de lignes de vente')
plt.xlabel('Catégorie')
plt.ylabel('Nombre de lignes de vente')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("output_graphs/top_10_cat_lignes_vente.png")
plt.close()

# 6. Catégories avec le plus de quantité vendue

cat_qty = sales_merged.groupby('Categorie')['qte'].sum().sort_values(ascending=False).head(10)
print(cat_qty)

# 7. Nombre d'achat et dépense totale par genre (H/F)

achats_clients = achats_df.merge(clients_df, left_on='acheteur', right_on='id', how='inner')
gender_stats = achats_clients.groupby('genre').agg(
    nombre_achats=('ticket', 'count'),
    depense_totale=('total', 'sum')
)
print(gender_stats)

# 8. Nombre d'achat et dépense totale par genre et par rayon

sales_full = sales_merged.merge(clients_df, left_on='acheteur', right_on='id', how='inner')
gender_rayon_stats = sales_full.groupby(['genre', 'Rayon']).agg(
    nombre_achats=('ticket', 'nunique'), # count unique tickets to avoid duplicating per line
    depense_totale=('total_line', 'sum')
).reset_index()

# Sort to show some meaningful top results
print(gender_rayon_stats.sort_values(by='depense_totale', ascending=False).head(10))

# 9. Nombre d'achat et dépense totale par commune

commune_stats = achats_clients.groupby('commune').agg(
    nombre_achats=('ticket', 'count'),
    depense_totale=('total', 'sum')
).sort_values(by='depense_totale', ascending=False).head(10)
print(commune_stats)

# Graph for 9
plt.figure(figsize=(10, 6))
commune_stats['depense_totale'].plot(kind='bar', color='mediumseagreen')
plt.title('Dépense totale par commune (Top 10)')
plt.xlabel('Commune')
plt.ylabel('Dépense totale (€)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("output_graphs/depense_par_commune.png")
plt.close()

# 10. Dépense totale par commune et par genre

commune_gender_stats = achats_clients.groupby(['commune', 'genre'])['total'].sum().unstack().fillna(0)
commune_gender_stats['Total'] = commune_gender_stats.sum(axis=1)
commune_gender_stats = commune_gender_stats.sort_values(by='Total', ascending=False).head(10)
print(commune_gender_stats[['F', 'H']])

print("\nAnalyses des ventes terminées. Graphes sauvegardés dans le dossier 'output_graphs'.")
