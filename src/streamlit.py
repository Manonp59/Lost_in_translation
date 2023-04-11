import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

options_year = ["2019","2020","2021","2022"]

selected_year = st.selecto

# Calculez entre 2019 et 2022 la somme du nombre d’objets trouvés par semaine. Afficher sur un histogramme plotly la répartition de ces valeurs. (un point correspond à une semaine dont la valeur est la somme). (On peut choisir d’afficher ou non certains types d’objet).

connexion = sqlite3.connect("base.db")
df_semaine = pd.read_sql_query("""SELECT strftime('%Y-%W', date) AS semaine, COUNT(*) AS nb_objets_trouves 
                          FROM Objets_trouves 
                          GROUP BY semaine""", connexion)

hist = px.histogram(df_semaine, x='semaine', y='nb_objets_trouves', nbins=300)
hist.update_xaxes(title_text='Date')
hist.update_yaxes(title_text="Nombre d'objets trouvés")
hist.update_layout(title="Nombre d'objets trouvés par semaine")

line = px.line(df_semaine, x='semaine', y='nb_objets_trouves')
line.update_xaxes(title_text='Date')
line.update_yaxes(title_text="Nombre d'objets trouvés")
line.update_layout(title="Nombre d'objets trouvés par semaine")
st.title('Mes graphiques')

st.plotly_chart(hist,use_container_width=True)
st.plotly_chart(line, use_container_witdh=True)

connexion.close()

# Afficher une carte de Paris avec le nombre d’objets trouvés en fonction de la fréquentation de voyageur de chaque gare. Possibilité de faire varier par année et par type d’objets

import folium
from folium.plugins import HeatMap

# Chargement des données depuis la base de données
connexion = sqlite3.connect("base.db")

df_gares = pd.read_sql_query("SELECT * FROM Gares", connexion)
df_objets_trouves = pd.read_sql_query("SELECT * FROM Objets_trouves", connexion)

connexion.close()

# Agrégation des données par gare et par année
df_gares_agg = df_gares.groupby(['nom_gare']).sum().reset_index()
df_objets_trouves_agg = df_objets_trouves.groupby(['nom_gare']).count().reset_index()

# Jointure des données
df_join = pd.merge(df_gares_agg, df_objets_trouves_agg, on='nom_gare')

# Création de la carte
paris_coord = [48.8566, 2.3522]
m = folium.Map(location=paris_coord, zoom_start=12)

# Ajout des marqueurs de gare
for i, row in df_join.iterrows():
    popup_text = f"Gare : {row['nom_gare']}<br>Fréquentation 2019 : {row['frequentation_2019']}<br>Fréquentation 2020 : {row['frequentation_2020']}<br>Fréquentation 2021 : {row['frequentation_2021']}<br>Nombre d'objets trouvés : {row['id']}"
    folium.Marker(location=[row['latitude'], row['longitude']], popup=popup_text).add_to(m)

# Ajout de la heatmap
heatmap_data = [[row['latitude'], row['longitude'], row['id']] for i, row in df_join.iterrows()]
HeatMap(heatmap_data, radius=15, blur=10).add_to(m)

# Affichage de la carte
st.folium_chart(m)


