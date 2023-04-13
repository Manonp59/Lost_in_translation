import sqlite3
import pandas as pd
import plotly.express as px
from code_streamlit import histogramme, line, scatterplot, boxplot
import unittest, pytest
from unittest.mock import patch
from io import StringIO

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



if __name__ == '__main__':
    unittest.main()