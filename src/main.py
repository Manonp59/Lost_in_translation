import sqlite3
import requests
import pandas as pd
import sqlite3
import urllib.parse
from dotenv import load_dotenv
import os
import datetime
from dateparser import parse
from typing import Tuple
import streamlit as st


def create_db ():
    connexion = sqlite3.connect('base.db')
    curseur = connexion.cursor()

    # Création de la table Températures
    curseur.execute(""" CREATE TABLE IF NOT EXISTS Temperatures (
                        date TEXT PRIMARY KEY UNIQUE, 
                        temperature_moyenne INTEGER
                    )
                    """)

    # Création de la table Gares
    curseur.execute(""" CREATE TABLE IF NOT EXISTS Gares (
                        nom_gare TEXT PRIMARY KEY,
                        latitude REAL,
                        longitude REAL,
                        frequentation_2019 INTEGER,
                        frequentation_2020 INTEGER,
                        frequentation_2021 INTEGER
                    )
                    """)

    # Création de la table objets trouvés
    curseur.execute(""" CREATE TABLE IF NOT EXISTS Objets_trouves (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        date TEXT,
                        type TEXT,
                        nom_gare TEXT,
                        code_uic INTEGER,
                        FOREIGN KEY (nom_gare) REFERENCES Gares(nom_gare),
                        FOREIGN KEY (date) REFERENCES Temperatures(date)
                        )""")


    connexion.commit()
    connexion.close()
    


def years_between_dates(start_date, end_date):
    dates = []
    if end_date == "now":
        end_date = datetime.date.today()
    else:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    for year in range(start_date.year, end_date.year + 1):
        date = datetime.date(year, 1, 1)
        if start_date <= date <= end_date:
            dates.append(year)
    return dates

  


def import_data_objects ():
    url1 = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=objets-trouves-restitution&q=gc_obo_gare_origine_r_name+%3D+%22"
    url2 = "&sort=date&facet=date&facet=gc_obo_date_heure_restitution_c&facet=gc_obo_gare_origine_r_name&facet=gc_obo_nature_c&facet=gc_obo_type_c&facet=gc_obo_nom_recordtype_sc_c&timezone=Europe%2FParis&rows=-1"


    gares = ['Paris Gare de Lyon', 'Paris Montparnasse', 'Paris Gare du Nord', 'Paris Saint-Lazare', 'Paris Est', 'Paris Bercy', 'Paris Austerlitz']
    start_date = get_last_date("Objets_trouves")
    end_date = datetime.datetime.now()
    date = years_between_dates(start_date,end_date.strftime("%Y-%m-%d"))

    data_frames = []
    for g in gares:
        for d in date:
            api_url = f"{url1}{urllib.parse.quote(g)}%22+AND+date%3D{str(d)}{url2}"
            response = requests.get(api_url)
            data = response.json()
            records = data["records"]
            record_fields = [record["fields"] for record in records]
            data_frames.append(record_fields)
    
    connexion = sqlite3.connect("base.db")
    curseur = connexion.cursor()
    for n in range(len(data_frames)):
        for item in data_frames[n]:
        # Extract the variables and values
            date = item['date']
            type = item['gc_obo_type_c']
            gare = item['gc_obo_gare_origine_r_name']
            code_uic = item['gc_obo_gare_origine_r_code_uic_c']
            curseur.execute("INSERT INTO Objets_trouves (date,type,nom_gare,code_uic) VALUES (?,?, ?, ?)", (date, type,gare, code_uic))
    curseur.execute("""UPDATE Objets_trouves
    SET date = DATE(SUBSTR(date, 1, 10))""")
    connexion.commit()
    connexion.close()
    
def import_data_frequentation ():
    url_frequentation_gares = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=frequentation-gares&q=nom_gare%3D%27Paris%27&sort=nom_gare&rows=-1"

    response = requests.get(url_frequentation_gares)

    gare_frequentation_list = []

    if response.status_code == 200:
        data = response.json()
        for record in data['records']:
            gare = record['fields']['nom_gare']
            frequentation_2019 = record['fields']['total_voyageurs_non_voyageurs_2019']
            frequentation_2020 = record['fields']['total_voyageurs_non_voyageurs_2020']
            frequentation_2021 = record['fields']['total_voyageurs_non_voyageurs_2021']
            gare_frequentation_list.append([gare,frequentation_2019,frequentation_2020,frequentation_2021])
                        
    else:
        print("Une erreur s'est produite lors de la requête à l'API.")
        
    connexion = sqlite3.connect("base.db")
    curseur = connexion.cursor()
    for gare in gare_frequentation_list:
        nom_gare = gare[0]
        frequentation_2019 = gare[1]
        frequentation_2020 = gare[2]
        frequentation_2021 = gare[3]
        curseur.execute("INSERT INTO Gares (nom_gare, frequentation_2019, frequentation_2020,frequentation_2021) VALUES (?,?, ?, ?)",(nom_gare,frequentation_2019,frequentation_2020,frequentation_2021))
    curseur.execute("ALTER TABLE gares ADD COLUMN frequentation_2022 INTEGER;")
    curseur.execute('UPDATE gares SET frequentation_2022 = frequentation_2019')
    connexion.commit()
    connexion.close()
    
def import_data_localisation():
    url_gares = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=referentiel-gares-voyageurs&q=gare_alias_libelle_noncontraint='Paris'&sort=gare_alias_libelle_noncontraint&rows=-1"

    response = requests.get(url_gares)

    gares_coord_list = []

    if response.status_code == 200:
        data = response.json()
        for record in data['records']:
            gare_alias_libelle_noncontraint = record['fields']['gare_alias_libelle_noncontraint']
            if 'wgs_84' in record['fields']:
                latitude = record['fields']['wgs_84'][0]
                longitude = record['fields']['wgs_84'][1]
                gares_coord_list.append([gare_alias_libelle_noncontraint, latitude, longitude])
          
    else:
        print("Une erreur s'est produite lors de la requête à l'API.")
        
    connexion = sqlite3.connect("base.db")
    curseur = connexion.cursor()
    for gare in gares_coord_list:
        nom_gare = gare[1]
        latitude = gare[2]
        longitude = gare[3]
        curseur.execute("UPDATE Gares SET latitude = ?, longitude= ? WHERE nom_gare = ?", (latitude, longitude, nom_gare))
    curseur.execute("UPDATE Objets_trouves SET nom_gare = 'Paris Bercy' WHERE nom_gare LIKE 'Paris Bercy%'")
    curseur.execute("UPDATE Gares SET nom_gare = 'Paris Bercy' WHERE nom_gare LIKE 'Paris Bercy%'")
    connexion.commit()
    connexion.close()

def import_data_temperature():

    load_dotenv()
    API_KEY_TEMP = os.getenv("API_KEY_TEMP")

    # Coordonnées de Paris
    COORDS = "48.8566,2.3522"

    # Définition de la période de temps
    delta = datetime.timedelta(days=35)
    start_date = get_last_date("Temperatures")
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.now()
   

    # Liste pour stocker les données de température
    temperature_dates_list = []

    # Boucle pour récupérer les données de température par période de 35 jours
    while start_date <= end_date:
        end_period = start_date + delta
        if end_period > end_date:
            end_period = end_date
        url = f"https://api.worldweatheronline.com/premium/v1/past-weather.ashx?q={COORDS}&date={start_date}&enddate={end_period}&tp=24&format=json&key={API_KEY_TEMP}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for weather in data['data']['weather']:
                date = weather['date']
                temperature_moyenne = weather['avgtempC']
                temperature_dates_list.append([date,temperature_moyenne])
        else:
            print("Une erreur s'est produite lors de la requête à l'API.")
        start_date += delta

    connexion = sqlite3.connect("base.db")
    curseur = connexion.cursor()
    for entree in temperature_dates_list:
        date = entree[0]
        temperature = entree[1]

        curseur.execute("INSERT INTO Temperatures (date,temperature_moyenne) VALUES (?,?)", (date, temperature))

    # Fermeture de la connexion à la base de données
    connexion.commit()
    connexion.close()
    
def clean(table) -> None:
        connexion = sqlite3.connect("base.db")
        curseur = connexion.cursor()
        curseur.execute(f"""DROP TABLE {table}""")
        connexion.commit()
        connexion.close()
        
def get_last_date(table) -> str:
    connexion = sqlite3.connect("base.db")
    curseur = connexion.cursor()
    curseur.execute(f"""SELECT MAX(date) FROM {table}""")
    date_string = str(curseur.fetchone()[0])
    connexion.commit()
    connexion.close()
    
    # Convertir la date en objet datetime
    last_date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    
    # Ajouter un jour à la date
    next_day = last_date + datetime.timedelta(days=1)
    
    # Convertir la date en chaîne de caractères
    next_day_string = next_day.strftime("%Y-%m-%d")
    
    return next_day_string
 
    
        
# def get_last_date(table) -> str:
#     connexion = sqlite3.connect("base.db")
#     curseur = connexion.cursor()
#     curseur.execute(f"""SELECT MAX(date) FROM {table}""")
#     date_string = str(curseur.fetchone()[0])
#     connexion.commit()
#     connexion.close()
#     return date_string

# def parse_date(start_date: str, end_date: str) -> Tuple[datetime, datetime]:
#         start_parse = parse(str(start_date))
#         end_parse = parse(str(end_date))
#         return start_parse, end_parse

# create_db()

# clean("Temperatures")
# create_db()
# import_data_temperature("2023-01-01","now")


def maj_db():
    with st.empty():
        st.write("Mise à jour en cours...")
        import_data_temperature()
        import_data_objects()
        st.write("Mise à jour terminée !")


