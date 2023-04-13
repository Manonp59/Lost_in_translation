import unittest 
from unittest.mock import MagicMock
import sqlite3
from main import years_between_dates,get_last_date, import_data_objects

class TestWithUnittest(unittest.TestCase):
    
    def setUp(self):
        self.connexion = sqlite3.connect(":memory:")
        self.curseur = self.connexion.cursor()


    def test_years_between_dates(self):
        start_date = "2019-01-01"
        end_date = "2022-12-31"
        expected_dates = years_between_dates(start_date,end_date)
        
        self.assertEqual(expected_dates, [2019,2020,2021,2022])
    
         
    def test_get_last_date(self):
        self.curseur.execute("""
            CREATE TABLE objets (
                id INTEGER PRIMARY KEY,
                type_objet TEXT,
                date TEXT
            )
        """)
        # Insertion de données de test dans la table objets_trouves
        self.curseur.execute("""
            INSERT INTO objets (type_objet, date)
            VALUES ('clés', '2022-01-01'),
                ('portefeuille', '2022-01-02'),
                ('téléphone', '2022-01-03')
        """)
        self.connexion.commit()
        
        # Vérification de la date de la dernière entrée dans la table objets_trouves
        self.assertEqual(get_last_date("objets"), "2022-01-04")

        self.connexion.close()
        

