import json
import locale
import os
from datetime import datetime

import pandas as pd
import streamlit as st

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')


class DashboardUtils:


    def load_treino_data(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        treino_data_path = os.path.join(script_dir, "../../data/set.json")
        with open(treino_data_path, "r") as file:
            data = json.load(file)
            treino_list = []
            for date, details in data["schedule"].items():
                treino_list.append({
                    "Data": date,
                    "Tipo": details.get("type", ""),
                    "Exercícios": [
                        {"Categoria": ex["category"], "Sets": ex["sets"]}
                        for ex in details.get("exercises", [])
                    ]
                })
            rows = []
            for treino in treino_list:
                for ex in treino["Exercícios"]:
                    for set_item in ex["Sets"]:
                        rows.append({
                            "Data": treino["Data"],
                            "Tipo": treino["Tipo"],
                            "Categoria": ex["Categoria"],
                            "Exercício": set_item
                        })
            treino_data = pd.DataFrame(rows)
        return treino_data

    # BUSCAR AS CALORIAS POR DATA
    def get_calories_by_date(self, bio_data, selected_date):
        for entry in bio_data:
            if isinstance(entry, dict) and "start_time" in entry:
                entry_date = datetime.strptime(entry["start_time"][:10], "%Y-%m-%d").date()
                if entry_date == selected_date:
                    duration = entry.get("duration", "")
                    if duration.startswith("PT") and duration.endswith("S"):
                        try:
                            duration_seconds = float(duration[2:-1])
                            duration_minutes = int(duration_seconds // 60)
                        except ValueError:
                            duration_minutes = 0
                    else:
                        duration_minutes = 0
                    return (
                        entry["calories"], entry["heart_rate"]["average"], entry["heart_rate"]["maximum"],
                        duration_minutes)
        return 0, 0, 0, 0
