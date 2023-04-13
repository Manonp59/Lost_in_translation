import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px 
import streamlit as st
import folium
import numpy as np
import statsmodels.api as sm
from streamlit_folium import folium_static
import matplotlib.pyplot as plt








def scatterplot():
    
    # Connexion à la base de données
    connexion = sqlite3.connect("base.db")
    curseur = connexion.cursor()
    
    # Récupération des données à partir de la base de données dans un dataframe
    df = pd.DataFrame(curseur.execute("""SELECT Temperatures.date AS date , Temperatures.temperature_moyenne AS temperature, COUNT(Objets_trouves.id) AS nb_objets
    FROM Temperatures
    LEFT JOIN Objets_trouves ON Temperatures.date = Objets_trouves.date
    GROUP BY Temperatures.date;

                                    """))
    connexion.commit()
    connexion.close()

    # Création du scatterplot avec une droite de régression linéaire
    x = df.iloc[:, 1] # sélection de la colonne "temperature" comme variable indépendante
    y = df.iloc[:, 2] # sélection de la colonne "nb_objets" comme variable dépendante
    model = sm.OLS(y, sm.add_constant(x)).fit() # ajustement d'un modèle de régression linéaire
        
    # Création du scatterplot avec une droite de régression linéaire
    g = px.scatter(data_frame=df,x=1,y=2,trendline="ols")
    g.update_xaxes(title_text='Température')
    g.update_yaxes(title_text="Nombre d'objets trouvés")
    g.update_layout(title="Nombre d'objets trouvés en fonction de la température")
    
    # Affichage du scatterplot dans Streamlit
    st.plotly_chart(g,use_container_width=True)

        # Vérification si la droite de régression existe avant de récupérer le coefficient de détermination R²
    if len(g['data']) > 1:
        coeff_determination = model.rsquared
        st.write(f"Le coefficient de détermination R² est : {coeff_determination:.2f}")
        if coeff_determination < 0.1:
            st.write("D'après le graphique et le coefficient de détermination R², On constate que la corrélation entre la température et les objets trouvés est très faible.")
        elif 0.1 <= coeff_determination < 0.3:
            st.write("D'après le graphique et le coefficient de détermination R², On constate que la corrélation est faible.")
        elif 0.3 <= coeff_determination < 0.5:
            st.write("D'après le graphique et le coefficient de détermination R², On constate que la corrélation est modérée.")
        elif 0.5 <= coeff_determination < 0.7:
            st.write("D'après le graphique et le coefficient de détermination R², On constate que la corrélation est forte.")
        elif 0.7 <= coeff_determination < 0.9:
            st.write("D'après le graphique et le coefficient de détermination R², On constate que la corrélation est très forte.")
        else:
            st.write("D'après le graphique et le coefficient de détermination R², On constate que la corrélation est excellente.")

    else:
        st.write("Attention : La droite de régression n'a pas pu être tracée.")




def groupbar():
    # Connexion à la base de données
    connexion = sqlite3.connect("base.db")

    # Récupération des données à partir de la base de données
    df = pd.read_sql_query("""SELECT Objets_trouves.type, Objets_trouves.saison, COUNT(id) AS nb_objets
                            FROM Objets_trouves
                            GROUP BY type, saison;""", connexion)

    # Création d'une table pivot
    pivot_data = df.pivot(index='type', columns='saison', values='nb_objets')

    # Calcul de la moyenne pour chaque saison
    moyenne = df.groupby('saison')['nb_objets'].mean()

    # Création du graphique à barres
    fig = go.Figure(data=[
        go.Bar(name='Printemps', y=pivot_data.index, x=pivot_data['Printemps'],orientation='h'),
        go.Bar(name='Été', y=pivot_data.index, x=pivot_data['Été'],orientation='h'),
        go.Bar(name='Automne', y=pivot_data.index, x=pivot_data['Automne'],orientation='h'),
        go.Bar(name='Hiver', y=pivot_data.index, x=pivot_data['Hiver'],orientation='h'),
        go.Scatter(y=moyenne.index, x=moyenne.values, mode='lines', name='Moyenne')
    ])
    fig.update_layout(barmode='group',height=800,width=1500,title="Nombre d'objets trouvés selon le type et la saison")

    # Fermeture de la connexion à la base de données
    connexion.close()
    st.plotly_chart(fig,use_container_width=True)




st.title("Brief Lost in Translation")

st.markdown("<span style='color:blue;text-decoration:underline;'>Mon texte coloré et souligné</span>", unsafe_allow_html=True)

    
st.write("<h2> Calculez entre 2019 et 2022 la somme du nombre d’objets trouvés par semaine. Afficher sur un histogramme plotly la répartition de ces valeurs. (un point correspond à une semaine dont la valeur est la somme). (On peut choisir d’afficher ou non certains types d’objet).</h2>",unsafe_allow_html = True)

 
    
options_objects = ["Porte-monnaie / portefeuille, argent, titres","Livres, articles de papéterie","Vêtements, chaussures","Bagagerie: sacs, valises, cartables","Pièces d'identités et papiers personnels","Appareils électroniques, informatiques, appareils photo","Articles d'enfants, de puériculture","Optique","Instruments de musique","Articles médicaux","Articles de sport, loisirs, camping","Bijoux, montres","Clés, porte-clés, badge magnétique","Vélos, trottinettes, accessoires 2 roues","Parapluies","Tous"]
  
st.write("<h2>Nuage de points.</h2>",unsafe_allow_html = True)

scatterplot()

st.write("<h2>Affichez le nombre d'objets trouvés en fonction du type de d'objet et de la saison sur un graphique. Il y a t il une correlation entre ces deux variables d'après le graphique?</h2>",unsafe_allow_html=True)

groupbar()
st.write("<h2>Boite à moustache </h2>",unsafe_allow_html=True)


boite_moustache()