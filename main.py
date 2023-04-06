import requests
import pandas as pd



url = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=objets-trouves-restitution&q=gc_obo_gare_origine_r_name+%3D+%22Paris%22+AND+(date%3D'2019'+OR+date%3D'2020'+OR+date+%3D'2021'+OR+date%3D'2022')&sort=date&facet=date&facet=gc_obo_date_heure_restitution_c&facet=gc_obo_gare_origine_r_name&facet=gc_obo_nature_c&facet=gc_obo_type_c&facet=gc_obo_nom_recordtype_sc_c&timezone=Europe%2FParis"



response = requests.get(url)

if response.ok:
    data = response.json()
    print(data)
else:
    print('Erreur lors de la requête :', response.status_code)
    
df_data = pd.DataFrame(data, columns=[
    "date",
    "gc_obo_date_heure_restitution_c",
    "gc_obo_gare_origine_r_name",
    "gc_obo_nature_c",
    "gc_obo_type_c",
    "gc_obo_nom_recordtype_sc_c"
])

df_data.to_csv('df_data.csv')



url_gares = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=referentiel-gares-voyageurs&q=&sort=gare_alias_libelle_noncontraint&facet=latitude_entreeprincipale_wgs84&facet=longitude_entreeprincipale_wgs84"
response = requests.get(url)

if response.ok:
    data = response.json()
    print(data)
else:
    print('Erreur lors de la requête :', response.status_code)
    




