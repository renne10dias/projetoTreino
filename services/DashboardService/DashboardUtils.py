import json
import locale
import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.DataLoader import DataLoader

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
    '''def get_calories_by_date(self, bio_data, selected_date):
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
        return 0, 0, 0, 0'''

    # BUSCAR AS CALORIAS POR DATA
    def get_calories_by_date(self, bio_data, selected_date):
        calories_list = []
        heart_rate_avg_list = []
        heart_rate_max_list = []
        duration_list = []

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

                    calories_list.append(entry["calories"])
                    heart_rate_avg_list.append(entry["heart_rate"]["average"])
                    heart_rate_max_list.append(entry["heart_rate"]["maximum"])
                    duration_list.append(duration_minutes)

        # Considerando apenas os últimos 5 treinos
        calories_list = calories_list[-5:]
        heart_rate_avg_list = heart_rate_avg_list[-5:]
        heart_rate_max_list = heart_rate_max_list[-5:]
        duration_list = duration_list[-5:]

        if calories_list:
            avg_calories = sum(calories_list) / len(calories_list)
            avg_heart_rate_avg = sum(heart_rate_avg_list) / len(heart_rate_avg_list)
            avg_heart_rate_max = sum(heart_rate_max_list) / len(heart_rate_max_list)
            avg_duration = sum(duration_list) / len(duration_list)
            return avg_calories, avg_heart_rate_avg, avg_heart_rate_max, avg_duration

        return 0, 0, 0, 0

    def load_dataset_formated(self):

        data_loader = DataLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/bioData.json"))
        json_data = data_loader.load_json_data()
        df = data_loader.extract_data()

        # Remove o dia da semana do campo 'start_time' e converte para datetime
        df['start_time'] = df['start_time'].apply(
            lambda x: re.match(r'\d{2}/\d{2}', x).group(0) + '/2024')
        df['start_time'] = pd.to_datetime(df['start_time'], format='%d/%m/%Y')

        # Formata as datas no hover
        df['Data'] = df['start_time'].dt.strftime('%d/%m/%Y')

        anos_unicos_Intensity = df["start_time"].dt.year.unique()
        meses_unicos_en_Intensity = df["start_time"].dt.month.unique()

        return [json_data, df, anos_unicos_Intensity, meses_unicos_en_Intensity]



    def selected_month_year_Intensity(self, key_suffix=""):

        # Criando uma instância da classe que contém os métodos
        dashboard_utils = DashboardUtils()

        # Chamando o método e armazenando os retornos
        json_data, df, anos_unicos_Intensity, meses_unicos_en_Intensity = dashboard_utils.load_dataset_formated()

        meses_pt = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio",
            6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro",
            11: "Novembro", 12: "Dezembro"
        }

        # Criar os widgets para seleção de ano e mês
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            selected_month_Intensity = st.selectbox(
                "Selecione o mês",
                [meses_pt[mes] for mes in meses_unicos_en_Intensity],
                key=f"mes_intensidade_{key_suffix}"  # Gera um key único"

            )
        with col1_2:
            selected_year_Intensity = st.selectbox(
                "Selecione o ano",
                anos_unicos_Intensity,
                key = f"ano_intensidade{key_suffix}"  # Gera um key único
            )

        return [json_data, df, meses_pt, selected_month_Intensity, selected_year_Intensity]
