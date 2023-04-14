import unittest 
from unittest.mock import MagicMock
import sqlite3
from main import years_between_dates,get_last_date
from code_streamlit import histogramme,scatterplot,boxplot
from unittest.mock import patch
from io import StringIO

class TestWithUnittest(unittest.TestCase):
    
    def setUp(self):
        self.connexion = sqlite3.connect(":memory:")
        self.curseur = self.connexion.cursor()


    def test_years_between_dates(self):
        """
        Teste la fonction years_between_dates() en vérifiant que la liste de dates
        renvoyée est bien égale à celle attendue pour une plage de dates donnée.
        """
        start_date = "2019-01-01"
        end_date = "2022-12-31"
        expected_dates = years_between_dates(start_date,end_date)
        
        self.assertEqual(expected_dates, [2019,2020,2021,2022])
    
         
    def test_get_last_date(self):
        """
        Teste la fonction get_last_date() en vérifiant que la date de la dernière entrée
        dans une table donnée est bien récupérée.
        """
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
        

class TestHistogramme(unittest.TestCase):

    def test_histogramme(self):
        # Test avec une sélection d'objets vide
        objets_inclus = []
        fig = histogramme(objets_inclus)
        self.assertIsNotNone(fig, "Le graphique ne doit pas être None")

        # Test avec une sélection d'objets non vide
        objets_inclus = ['Porte-monnaie / portefeuille, argent, titres']
        fig = histogramme(objets_inclus)
        self.assertIsNotNone(fig, "Le graphique ne doit pas être None")

        # Test avec une sélection d'objets inexistante
        objets_inclus = ['Objet inexistant']
        fig = histogramme(objets_inclus)
        self.assertIsNotNone(fig, "Le graphique ne doit pas être None")

        # Test avec une base de données incorrecte
        connexion = sqlite3.connect("mauvaise_base.db")
        objets_inclus = ['Porte-monnaie / portefeuille, argent, titres']
        with self.assertRaises(Exception):
            histogramme(connexion,objets_inclus)



    #Vérifiez que la fonction fonctionne correctement lorsque l'argument 'Tous' est passé:
class TestLine(unittest.TestCase):
    
    def setUp(self):
        self.selected_object = "Tous"
    
    def test_line(self):
        chart = line(self.selected_object)
        self.assertIsNotNone(chart)
        self.assertEqual(chart.__class__.__name__, 'PlotlyChart')
        self.assertEqual(chart['data'][0]['type'], 'scatter')
        self.assertEqual(chart['layout']['title']['text'], "Nombre d'objets trouvés par semaine")
        self.assertEqual(chart['layout']['xaxis']['title']['text'], 'Date')
        self.assertEqual(chart['layout']['yaxis']['title']['text'], "Nombre d'objets trouvés")
        self.assertEqual(chart['layout']['width'], 1500)
        


class TestScatterPlot(unittest.TestCase):
    
    def test_scatterplot(self):
        try:
            scatterplot()
        except Exception as e:
            self.fail(f"scatterplot() raised an exception: {e}")


class TestBoxPlot(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def test_boxplot(self, mock_stdout):
        boxplot()
        self.assertIn("Nombre d'objets perdus par saison pour l'objet", mock_stdout.getvalue())

