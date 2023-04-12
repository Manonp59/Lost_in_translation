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


def histogramme():
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
    objets_inclus = st.multiselect('Sélectionnez les types d\'objets à inclure :', ['Porte-monnaie / portefeuille, argent, titres', 'Livres, articles de papéterie' , 'Vêtements, chaussures', 'Bagagerie: sacs, valises, cartables', "Pièces d'identités et papiers personnels" , 'Appareils électroniques, informatiques, appareils photo', "Articles d'enfants, de puériculture", "Optique", "Divers", "Instruments de musique", "Articles médicaux","Articles de sport, loisirs, camping","Bijoux, montres", "Clés, porte-clés, badge magnétique", "Vélos, trottinettes, accessoires 2 roues", "Parapluies" ])

    # Appeler la fonction pour générer le graphique Plotly en fonction des types d'objets sélectionnés
    fig = generer_graphique(objets_inclus)

    # Afficher le graphique Plotly dans un conteneur
    with st.container():
        st.plotly_chart(fig)



# Calculez entre 2019 et 2022 la somme du nombre d’objets trouvés par semaine. Afficher sur un histogramme plotly la répartition de ces valeurs. (un point correspond à une semaine dont la valeur est la somme). (On peut choisir d’afficher ou non certains types d’objet).
def line(selected_object):
    connexion = sqlite3.connect("base.db")
    if selected_object == "Tous":
        df_semaine = pd.read_sql_query("""SELECT strftime('%Y-%W', date) AS semaine, COUNT(*) AS nb_objets_trouves 
                                FROM Objets_trouves 
                                GROUP BY semaine""", connexion)
    else :
        df_semaine = pd.read_sql_query(f"""SELECT strftime('%Y-%W', date) AS semaine, COUNT(*) AS nb_objets_trouves 
                                FROM Objets_trouves 
                                WHERE type = "{selected_object}"
                                GROUP BY semaine""", connexion)


    fig = px.line(df_semaine, x='semaine', y='nb_objets_trouves')
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text="Nombre d'objets trouvés")
    fig.update_layout(title="Nombre d'objets trouvés par semaine")

    st.plotly_chart(fig, use_container_width=True)
    connexion.close()







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

















if __name__ == "__main__":
    st.set_page_config(page_title="Titre de la page", page_icon="icone.png", layout="wide", initial_sidebar_state="expanded")

    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-attachment: fixed;
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    



    st.write("<h1 style='text-align: center; font-weight: bold;'>Titre du graphique</h1>", unsafe_allow_html=True)
    add_bg_from_url()

    st.title("Brief Lost in Translation")

    st.markdown("<span style='color:blue;text-decoration:underline;'>Mon texte coloré et souligné</span>", unsafe_allow_html=True)

    
    st.write("<h2> Calculez entre 2019 et 2022 la somme du nombre d’objets trouvés par semaine. Afficher sur un histogramme plotly la répartition de ces valeurs. (un point correspond à une semaine dont la valeur est la somme). (On peut choisir d’afficher ou non certains types d’objet).</h2>",unsafe_allow_html = True)

    histogramme()
    
    options_objects = ["Porte-monnaie / portefeuille, argent, titres","Livres, articles de papéterie","Vêtements, chaussures","Bagagerie: sacs, valises, cartables","Pièces d'identités et papiers personnels","Appareils électroniques, informatiques, appareils photo","Articles d'enfants, de puériculture","Optique","Instruments de musique","Articles médicaux","Articles de sport, loisirs, camping","Bijoux, montres","Clés, porte-clés, badge magnétique","Vélos, trottinettes, accessoires 2 roues","Parapluies","Tous"]
    selected_object = st.selectbox("Sélectionnez un type d'objet", options_objects,key="object1")
    line(selected_object)
    st.write("<h2>Nuage de points.</h2>",unsafe_allow_html = True)

    scatterplot()