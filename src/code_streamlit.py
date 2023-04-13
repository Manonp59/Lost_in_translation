import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px 
import streamlit as st
import folium
import numpy as np
import branca
from streamlit_folium import folium_static
from main import maj_db
import statsmodels.api as sm
import plotly.io as pio
import sqlalchemy as db


def histogramme():
    # Se connecter à la base de données
    connexion = sqlite3.connect("base.db")

    # Définir la fonction qui génère le graphique Plotly
    def generer_graphique(objets_inclus):
        # Récupérer les données entre 2019 et 2022
        sql = "SELECT strftime('%Y-%W', date) AS semaine, type, COUNT(*) AS nb_objets FROM Objets_trouves WHERE type IN ({}) GROUP BY semaine".format(', '.join(['?']*len(objets_inclus)))
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
def line (selected_object):
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


    line = px.line(df_semaine, x='semaine', y='nb_objets_trouves')
    line.update_xaxes(title_text='Date')
    line.update_yaxes(title_text="Nombre d'objets trouvés")
    line.update_layout(title="Nombre d'objets trouvés par semaine",width=1500)

    st.plotly_chart(line, witdh=-1)
    

    connexion.close()


# Afficher une carte de Paris avec le nombre d’objets trouvés en fonction de la fréquentation de voyageur de chaque gare. Possibilité de faire varier par année et par type d’objets

# Création de la requête qui récupère les données dans la base de données
def requete(selected_year, selected_object):
    # Connexion à la base de données
    connexion = sqlite3.connect("base.db")
    # Pour tous les types d'objets confondus
    if selected_object == "Tous":
        df = pd.read_sql_query(f"""SELECT Gares.nom_gare, Gares.latitude, Gares.longitude, 
                                        COUNT (*) AS nb_total_objets,
                                        Gares.frequentation_{selected_year} AS frequentation_gare
                                FROM Objets_trouves 
                                JOIN Gares ON Objets_trouves.nom_gare = Gares.nom_gare
                                WHERE Objets_trouves.date LIKE "{selected_year}%"
                                GROUP BY Gares.nom_gare
                            """,connexion)
    # Pour pouvoir sélectionner un type d'objet particulier
    else : 
        df = pd.read_sql_query(f"""SELECT Gares.nom_gare, Gares.latitude, Gares.longitude, 
                                        COUNT (*) AS nb_total_objets,
                                        Gares.frequentation_{selected_year} AS frequentation_gare  
                                FROM Objets_trouves 
                                JOIN Gares ON Objets_trouves.nom_gare = Gares.nom_gare
                                WHERE type = "{selected_object}" AND Objets_trouves.date LIKE "{selected_year}%"
                                GROUP BY Gares.nom_gare
                            """,connexion)
    return df


# Détermination de la couleur des markers en fonction de la fréquentation de la gare
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

# Affichage de la carte 
def show_map(df):
    # Création de la carte 
    carte = folium.Map(location=[48.864716, 2.349014], zoom_start=12)
    
    # Création de l'échelle pour que les tailles des markers soient proportionnelles au nombre d'objets perdus
    scale = np.log(df['nb_total_objets'].astype(float))
    scale_min, scale_max = scale.min(), scale.max()
    
    # Ajout des markers
    for index, row in df.iterrows():
        normalized_size = (np.log(row['nb_total_objets']) - scale_min) / (scale_max - scale_min)
        taille_marqueur = 5 + normalized_size * 50
        folium.CircleMarker(location=(row['latitude'], row['longitude']),
                    tooltip=row['nom_gare']+ " - " + str(row['nb_total_objets']) + " objets trouvés",
                    radius=taille_marqueur,
                    color = get_color(row['frequentation_gare'])
                    ).add_to(carte)
    
    # Ajout de la légende
    colormap = branca.colormap.StepColormap(
    colors = ['green','yellow','orange','red'],
    vmin=df['frequentation_gare'].min(),
    vmax=df['frequentation_gare'].max(),
    index=[0,np.percentile(df['frequentation_gare'],25),np.percentile(df['frequentation_gare'],50),np.percentile(df['frequentation_gare'],75)],
    caption = 'Fréquentation de la gare')

    carte.add_child(colormap)  
    
    return folium_static(carte)

#### Afficher le nombre d’objets trouvés en fonction de la température sur un scatterplot. Est ce que le nombre d’objets perdus est corrélé à la temperature d'après ce graphique?


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
    
### Quelle est la médiane du nombre d’objets trouvés en fonction de la saison? Il y a t il une correlation entre ces deux variables d'après le graphique?
    
def saison():

    # Connexion à la base de données
    connexion = sqlite3.connect("base.db")
    curseur = connexion.cursor()
    
    # Création d'une colonne saison dans la table Objets_trouves
    curseur.execute("""
    UPDATE objets_trouves
    SET saison =
    CASE
        WHEN strftime('%m', date) BETWEEN '03' AND '05' THEN 'Printemps'
        WHEN strftime('%m', date) BETWEEN '06' AND '08' THEN 'Été'
        WHEN strftime('%m', date) BETWEEN '09' AND '11' THEN 'Automne'
        ELSE 'Hiver'
    END;
                                    
                    """)
    connexion.commit()
    connexion.close()
    
    # Récupération des données nécessaires dans la base de données, stockage dans un dictionnaire des médianes pour chaque saison
    saisons = ["Printemps","Été","Automne","Hiver"]
    dico = {}
    for saison in saisons:

        connexion = sqlite3.connect("base.db")
        curseur = connexion.cursor()
        df = pd.DataFrame(curseur.execute(f"""
        SELECT date AS date, COUNT(id) AS nb_objets FROM Objets_trouves WHERE saison = "{saison}" GROUP BY date
                                        
                        """),columns=['date','nb_objets'])
        connexion.commit()
        connexion.close()

        dico[saison]=df['nb_objets'].median()
    
    # Création d'un barplot à partir des données   
    saisons = list(dico.keys())
    temperatures = list(dico.values())

    barplot = px.bar(x=saisons,y=temperatures)
    barplot.update_xaxes(title_text="Saisons")
    barplot.update_yaxes(title_text="Médiane journalière du nombre d'objets trouvés")
    barplot.update_layout(title="Médiane journalière du nombre d'objets trouvés en fonction de la saison")
    st.plotly_chart(barplot,use_container_width=False)


### Affichez le nombre d'objets trouvés en fonction du type de d'objet et de la saison sur un graphique. Il y a t il une correlation entre ces deux variables d'après le graphique?
def groupbar():
    # Connexion à la base de données
    connexion = sqlite3.connect("base.db")

    # Récupération des données à partir de la base de données
    df = pd.read_sql_query("""SELECT Objets_trouves.type, Objets_trouves.saison, COUNT(id) AS nb_objets
                            FROM Objets_trouves
                            GROUP BY type, saison;""", connexion)

    # Création d'une table pivot
    pivot_data = df.pivot(index='type', columns='saison', values='nb_objets')

    # Création du graphique à barres
    fig = go.Figure(data=[
        go.Bar(name='Printemps', y=pivot_data.index, x=pivot_data['Printemps'],orientation='h'),
        go.Bar(name='Été', y=pivot_data.index, x=pivot_data['Été'],orientation='h'),
        go.Bar(name='Automne', y=pivot_data.index, x=pivot_data['Automne'],orientation='h'),
        go.Bar(name='Hiver', y=pivot_data.index, x=pivot_data['Hiver'],orientation='h')
    ])
    fig.update_layout(barmode='group',height=800,width=1500,title="Nombre d'objets trouvés selon le type et la saison")

    # Fermeture de la connexion à la base de données
    connexion.close()
    st.plotly_chart(fig,use_container_width=True)
    
def scatterplot_2():
    # Connexion à la base de données
    connexion = sqlite3.connect("base.db")

    # Récupération des données à partir de la base de données
    df = pd.read_sql_query("""SELECT Objets_trouves.type, Objets_trouves.saison, COUNT(id) AS nb_objets
                            FROM Objets_trouves
                            GROUP BY type, saison;""", connexion)
    
    s = px.scatter(data_frame=df, x=df['type'], y=df['nb_objets'],color=df['saison'])
    connexion.close()
    st.plotly_chart(s, use_container_width=True)
    
    

def boxplot():
    import sqlite3
import pandas as pd
import plotly.express as px

def boxplot():
    # Connexion à la base de données
    connexion = sqlite3.connect("base.db")

    # Récupération des données à partir de la base de données
    df = pd.read_sql_query("""SELECT Objets_trouves.type, Objets_trouves.saison, COUNT(id) AS nb_objets
                            FROM Objets_trouves
                            GROUP BY saison, type""", connexion)

    # Création d'une liste des types d'objets
    types_objets = df["type"].unique()

    # Pour chaque type d'objet, créer un graphique boîte à moustaches avec une boîte pour chaque saison
    for objet in types_objets:
        df_objet = df[df["type"] == objet]
        fig = px.box(df_objet, x="saison", y="nb_objets", height=400, width=700, points="all")
        fig.update_layout(title=f"Nombre d'objets perdus par saison pour l'objet {objet}")
        st.plotly_chart(fig, use_container_width=True)

    # Fermer la connexion à la base de données
    connexion.close()
    
def barres_empilées():
    
    # Connexion à la base de données
    conn = sqlite3.connect("base.db")

    # Requête SQL pour récupérer les données
    query = """
    SELECT saison, type, count(*) as nb_objets
    FROM objets_trouves
    GROUP BY saison, type
    """

    # Récupération des données
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    # Création de la liste des saisons et des types d'objet uniques
    saisons = list(set([row[0] for row in data]))
    types_objet = list(set([row[1] for row in data]))

    # Initialisation des listes de données pour chaque type d'objet
    donnees = {type_objet: [] for type_objet in types_objet}

    # Remplissage des listes de données pour chaque type d'objet
    for saison in saisons:
        nb_objets_total = sum([row[2] for row in data if row[0] == saison])
        for type_objet in types_objet:
            nb_objets_type = sum([row[2] for row in data if row[0] == saison and row[1] == type_objet])
            proportion = nb_objets_type / nb_objets_total
            donnees[type_objet].append(proportion)

    # Création du graphique à barres empilées
    fig = go.Figure()
    for i, type_objet in enumerate(types_objet):
        fig.add_trace(go.Bar(
            x=saisons,
            y=donnees[type_objet],
            name=type_objet,
        ))

    # Configuration du layout du graphique
    fig.update_layout(
        title="Proportion d'objets trouvés par saison et par type d'objet",
        xaxis_title="Saison",
        yaxis_title="Proportion d'objets trouvés",
        barmode="stack",
        height=800
    )

    # Affichage du graphique
    st.plotly_chart(fig,use_container_width=True)

def line_saison():
    # Connexion à la base de données
    connexion = sqlite3.connect('base.db')
    
    # Requête SQL pour récupérer les données
    query = '''
            SELECT saison, type, COUNT(*) as nb_objets
            FROM objets_trouves
            GROUP BY saison, type
            ORDER BY saison, type
            '''
    cursor = connexion.cursor()
    df = pd.DataFrame(cursor.execute(query), columns=['saison','type','nb_objets'])

    # Création du graphique en courbes
    fig = px.line(df, x='saison', y='nb_objets', color='type',
                title='Évolution du nombre d\'objets trouvés en fonction de la saison',
                labels={'saison': 'Saison', 'nb_objets': 'Nombre d\'objets trouvés'},
                height=800)

    st.plotly_chart(fig, use_container_width=True)



    




st.set_page_config(layout="wide")
st.title("Brief Lost in Translation")

st.write("<h2> Calculez entre 2019 et 2022 la somme du nombre d’objets trouvés par semaine. Afficher sur un histogramme plotly la répartition de ces valeurs. (un point correspond à une semaine dont la valeur est la somme). (On peut choisir d’afficher ou non certains types d’objet).</h2>",unsafe_allow_html = True)

histogramme()

options_objects = ["Porte-monnaie / portefeuille, argent, titres","Livres, articles de papéterie","Vêtements, chaussures","Bagagerie: sacs, valises, cartables","Pièces d'identités et papiers personnels","Appareils électroniques, informatiques, appareils photo","Articles d'enfants, de puériculture","Optique","Instruments de musique","Articles médicaux","Articles de sport, loisirs, camping","Bijoux, montres","Clés, porte-clés, badge magnétique","Vélos, trottinettes, accessoires 2 roues","Parapluies","Tous"]
selected_object = st.selectbox("Sélectionnez un type d'objet", options_objects,key="object1")
line(selected_object)

st.write("<h2>Afficher une carte de Paris avec le nombre d’objets trouvés en fonction de la fréquentation de voyageur de chaque gare. Possibilité de faire varier par année et par type d’objets</h2>", unsafe_allow_html=True)
options_year = ["2019","2020","2021","2022"]
selected_year = st.selectbox("Sélectionnez une année", options_year)
options_objects2 = ["Porte-monnaie / portefeuille, argent, titres","Livres, articles de papéterie","Vêtements, chaussures","Bagagerie: sacs, valises, cartables","Pièces d'identités et papiers personnels","Appareils électroniques, informatiques, appareils photo","Articles d'enfants, de puériculture","Optique","Instruments de musique","Articles médicaux","Articles de sport, loisirs, camping","Bijoux, montres","Clés, porte-clés, badge magnétique","Vélos, trottinettes, accessoires 2 roues","Parapluies","Tous"]
selected_object2 = st.selectbox("Sélectionnez un type d'objet", options_objects2,key="object2")
show_map(requete(selected_year,selected_object2))

st.write("<h2>Afficher le nombre d’objets trouvés en fonction de la température sur un scatterplot. Est ce que le nombre d’objets perdus est corrélé à la temperature d'après ce graphique?</h2>",unsafe_allow_html=True)
scatterplot()
st.write("Il n'y a pas de corrélation entre la température et le nombre d'objets trouvés.")

st.write("<h2>Quelle est la médiane du nombre d’objets trouvés en fonction de la saison? Il y a t il une correlation entre ces deux variables d'après le graphique?</h2>",unsafe_allow_html=True)
saison()
st.write("Il n'y a pas de corrélation entre la saison et le nombre d'objets trouvés.")

st.write("<h2>Affichez le nombre d'objets trouvés en fonction du type de d'objet et de la saison sur un graphique. Il y a t il une correlation entre ces deux variables d'après le graphique?</h2>",unsafe_allow_html=True)
groupbar()
st.write("Il n'y a pas de corrélation entre la saison et le type d'objets trouvés.")

line_saison()
barres_empilées()

st.write("<h2>Conclusion : Il ne semble pas y avoir de corrélations entre la saison et le type d'objets perdus. Les variations sont très faibles.</h2>",unsafe_allow_html=True)




if st.button("Cliquez ici pour mettre à jour les données"):
    maj_db()

