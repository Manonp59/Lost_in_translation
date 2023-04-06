import requests
import pandas as pd

api_key = 'YOUR_API_KEY_HERE' # Remplacez YOUR_API_KEY_HERE par votre clé d'API SNCF

url = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=objets-trouves-restitution&q=gc_obo_gare_origine_r_name+%3D+%22Paris%22+AND+(date%3D'2019'+OR+date%3D'2020'+OR+date+%3D'2021'+OR+date%3D'2022')&sort=date&facet=date&facet=gc_obo_date_heure_restitution_c&facet=gc_obo_gare_origine_r_name&facet=gc_obo_nature_c&facet=gc_obo_type_c&facet=gc_obo_nom_recordtype_sc_c&timezone=Europe%2FParis&rows=-1"


response = requests.get(url)
data = response.json()
facet = data["parameters"]["facet"]


#---------------------------------------------------------------------------------------------------------------
# Extraire les valeurs de facet
facets = facet
date = facets[0]
gc_obo_date_heure_restitution_c = facets[1]
gc_obo_gare_origine_r_name = facets[2]
gc_obo_nature_c = facets[3]
gc_obo_type_c = facets[4]
gc_obo_nom_recordtype_sc_c = facets[5]

# Extraire les champs des enregistrements
records = data["records"]
record_fields = []
for record in records:
    record_fields.append(record["fields"])

#print(record_fields)

# Créer un DataFrame à partir des champs des enregistrements
df = pd.DataFrame(record_fields)
print(df)


# Écrire le DataFrame dans un fichier CSV
df.to_csv("objets-trouves.csv", index=False)

#-------------------------------------------------------------------------------------------------------------------------------
    




