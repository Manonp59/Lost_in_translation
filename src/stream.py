import sqlite3
import pandas as pd
import plotly.express as px 
import streamlit as st


# Se connecter à la base de données
connexion = sqlite3.connect("base.db")

# Définir la fonction qui génère le graphique Plotly
def generer_graphique(objets_inclus):
    # Récupérer les données entre 2019 et 2022
    sql = "SELECT strftime('%Y-%W', date) AS semaine, type, COUNT(*) AS nb_objets FROM Objets_trouves WHERE type IN ({})  AND date BETWEEN '2019-01-01' AND '2022-12-31' GROUP BY semaine".format(', '.join(['?']*len(objets_inclus)))
    df = pd.read_sql_query(sql, connexion, params=objets_inclus)

    # Générer le graphique Plotly
    fig = px.histogram(df, x="semaine", y="nb_objets", color = 'type', color_discrete_sequence=px.colors.qualitative.Alphabet, nbins=1000000)
    fig.update_layout(xaxis=dict(type='category'))
    fig.update_layout(width=2000, height=600)
    
    return fig

# Utiliser la barre latérale pour créer une liste déroulante permettant de sélectionner les types d'objets à inclure
objets_inclus = st.sidebar.multiselect('Sélectionnez les types d\'objets à inclure :', ['Porte-monnaie / portefeuille, argent, titres', 'Livres, articles de papéterie' , 'Vêtements, chaussures', 'Bagagerie: sacs, valises, cartables', "Pièces d'identités et papiers personnels" , 'Appareils électroniques, informatiques, appareils photo', "Articles d'enfants, de puériculture", "Optique", "Divers", "Instruments de musique", "Articles médicaux","Articles de sport, loisirs, camping","Bijoux, montres", "Clés, porte-clés, badge magnétique", "Vélos, trottinettes, accessoires 2 roues", "Parapluies" ])

# Appeler la fonction pour générer le graphique Plotly en fonction des types d'objets sélectionnés
fig = generer_graphique(objets_inclus)

# Afficher le graphique Plotly dans un conteneur
with st.container():
    st.plotly_chart(fig)
