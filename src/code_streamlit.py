import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns



# Calculez entre 2019 et 2022 la somme du nombre d’objets trouvés par semaine. Afficher sur un histogramme plotly la répartition de ces valeurs. (un point correspond à une semaine dont la valeur est la somme). (On peut choisir d’afficher ou non certains types d’objet).
def histogrammes ():
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
import sqlite3
import pandas as pd
import numpy as np
import json
import branca
from streamlit_folium import folium_static
from folium.plugins import PolyLineTextPath



# Connexion à la base de données
connexion = sqlite3.connect("base.db")

def requete(selected_year, selected_object):
    if selected_object == "Tous":
        df = pd.read_sql_query(f"""SELECT Gares.nom_gare, Gares.latitude, Gares.longitude, 
                                        COUNT (*) AS nb_total_objets,
                                        SUM(Gares.frequentation_2019 + Gares.frequentation_2020 + Gares.frequentation_2021) AS frequentation_gare
                                FROM Objets_trouves 
                                JOIN Gares ON Objets_trouves.nom_gare = Gares.nom_gare
                                GROUP BY Gares.nom_gare
                            """,connexion)
    else : 
        df = pd.read_sql_query(f"""SELECT Gares.nom_gare, Gares.latitude, Gares.longitude, 
                                        COUNT (*) AS nb_total_objets,
                                        Gares.frequentation_{selected_year} AS frequentation_gare  
                                FROM Objets_trouves 
                                JOIN Gares ON Objets_trouves.nom_gare = Gares.nom_gare
                                WHERE type = "{selected_object}"
                                GROUP BY Gares.nom_gare
                            """,connexion)
    return df



def get_color(frequentation):
    df = requete(selected_year,selected_object)
    if frequentation < np.percentile(df['frequentation_gare'],25):
        return "green"
    elif frequentation < np.percentile(df['frequentation_gare'],50):
        return "yellow"
    elif frequentation < np.percentile(df['frequentation_gare'],75):
        return "orange"
    else :
        return "red"

def show_map(df):
    carte = folium.Map(location=[48.864716, 2.349014], zoom_start=12)
    scale = np.log(df['nb_total_objets'].astype(float))
    scale_min, scale_max = scale.min(), scale.max()
    for index, row in df.iterrows():
        normalized_size = (np.log(row['nb_total_objets']) - scale_min) / (scale_max - scale_min)
        taille_marqueur = 5 + normalized_size * 50
        folium.CircleMarker(location=(row['latitude'], row['longitude']),
                    tooltip=row['nom_gare']+ " - " + str(row['nb_total_objets']) + " objets trouvés",
                    icon=folium.Icon(icon='train', prefix='fa'),
                    radius=taille_marqueur,
                    color = get_color(row['frequentation_gare'])
                    ).add_to(carte)
    
    colormap = branca.colormap.StepColormap(
    colors = ['green','yellow','orange','red'],
    vmin=df['frequentation_gare'].min(),
    vmax=df['frequentation_gare'].max(),
    index=[0,np.percentile(df['frequentation_gare'],25),np.percentile(df['frequentation_gare'],50),np.percentile(df['frequentation_gare'],75)],
    caption = 'Fréquentation de la gare')

    carte.add_child(colormap)  
    
    return folium_static(carte)


def scatterplot():
    connexion = sqlite3.connect("base.db")
    curseur = connexion.cursor()
    df = pd.DataFrame(curseur.execute("""SELECT Temperatures.date AS date , Temperatures.temperature_moyenne AS temperature, COUNT(Objets_trouves.id) AS nb_objets
    FROM Temperatures
    LEFT JOIN Objets_trouves ON Temperatures.date = Objets_trouves.date
    GROUP BY Temperatures.date;

                                    """))
    connexion.commit()
    connexion.close()
    g = px.scatter(data_frame=df,x=1,y=2)
    g.update_xaxes(title_text='Température')
    g.update_yaxes(title_text="Nombre d'objets trouvés")
    g.update_layout(title="Nombre d'objets trouvés en fonction de la température")
    st.plotly_chart(g,use_container_width=True)

if __name__ == "__main__":
    histogrammes()
    
    options_year = ["2019","2020","2021","2022"]

    selected_year = st.selectbox("Sélectionnez une année", options_year)

    options_objects = ["Porte-monnaie / portefeuille, argent, titres","Livres, articles de papéterie","Vêtements, chaussures","Bagagerie: sacs, valises, cartables","Pièces d'identités et papiers personnels","Appareils électroniques, informatiques, appareils photo","Articles d'enfants, de puériculture","Optique","Instruments de musique","Articles médicaux","Articles de sport, loisirs, camping","Bijoux, montres","Clés, porte-clés, badge magnétique","Vélos, trottinettes, accessoires 2 roues","Parapluies","Tous"]

    selected_object = st.selectbox("Sélectionnez un type d'objet", options_objects)
    
    show_map(requete(selected_year,selected_object))
    
    scatterplot()
    st.write("Il n'y a pas de corrélation entre la température et le nombre d'objets trouvés.")
    
