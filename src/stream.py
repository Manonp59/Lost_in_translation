import sqlite3
import pandas as pd
import plotly.express as px 
import streamlit as st


# Se connecter à la base de données
connexion = sqlite3.connect("base.db")


# Définir les types d'objets à inclure
objets_inclus = ['Porte-monnaie / portefeuille, argent, titres', 'Appareils électroniques, informatiques, appareils photo', 'Articles médicaux']

# Récupérer les données entre 2019 et 2022
sql = "SELECT strftime('%Y-%W', date) AS semaine, type, COUNT(*) AS nb_objets FROM Objets_trouves WHERE type IN ({}) AND date BETWEEN '2019-01-01' AND '2022-12-31' GROUP BY semaine"
placeholders = ','.join(['?']*len(objets_inclus))
sql = sql.format(placeholders)
df = pd.read_sql_query(sql, connexion, params=objets_inclus)

# Calculer la somme du nombre d'objets trouvés par semaine
df_grouped = df.groupby(['semaine', 'type']).sum().reset_index()

# Afficher l'histogramme plotly
fig = px.histogram(df_grouped, x="semaine", y="nb_objets", barmode="stack", color=df['type'], title="Nombre d'objets trouvés par semaine",nbins=200)
fig.show()

# Afficher le graphique sur Streamlit
st.plotly_chart(fig)


