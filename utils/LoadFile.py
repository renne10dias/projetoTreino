import json
import locale
import os

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')


class LoadFile:

    def load_bio_data(self):
        bio_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/bioData.json")
        with open(bio_data_path, "r") as file:
            return json.load(file)

        # Função para carregar dados do set.json
    def load_set_data(self):
        treino_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/set.json")
        with open(treino_data_path, "r", encoding='utf-8') as file:
            return json.load(file)



