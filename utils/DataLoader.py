import json
import pandas as pd
import datetime
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')


class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_json_data(self):
        """Carrega os dados do arquivo JSON."""
        with open(self.file_path, 'r') as f:
            self.data = json.load(f)
        return self.data

    def extract_data(self):
        """Extrai calorias, duração, data e dia da semana dos dados carregados."""
        if self.data is None:
            raise ValueError("Os dados não foram carregados. Use load_json_data primeiro.")

        # Extraindo calorias, duração e combinando data e dia da semana
        extracted_data = [{
            "calories": entry["calories"],
            "duration": str(entry["duration"][2:-1]),
            "start_time": datetime.datetime.strptime(entry["start_time"][:10], '%Y-%m-%d').strftime('%d/%m (%A)')
        } for entry in self.data]
        df = pd.DataFrame(extracted_data)
        return df
