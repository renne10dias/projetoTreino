import json
import re

import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
import plotly.graph_objects as go

from services.DashboardService.DashboardUtils import DashboardUtils
from utils.LoadFile import LoadFile


class DashboardService:
    def __init__(self):
        self.loadFile = LoadFile()
        self.dashboardUtils = DashboardUtils()
        self.json_data = None
        self.df = None
        self.meses_pt = None
        self.selected_month_Intensity = None
        self.selected_year_Intensity = None

    def col1_intensidade_treino(self):

        # Obtendo os dados da classe Utils
        self.json_data, self.df, self.meses_pt, self.selected_month_Intensity, self.selected_year_Intensity = self.dashboardUtils.selected_month_year_Intensity(
            "1")

        # Adicionar dados de frequência cardíaca ao DataFrame
        heart_rate_data = [entry["heart_rate"]["average"] for entry in self.json_data]
        self.df['heart_rate_avg'] = heart_rate_data

        # Selecionar as colunas para o clustering
        X = self.df[['heart_rate_avg', 'calories']]

        # Aplicar K-means com 3 clusters
        kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
        self.df['cluster'] = kmeans.labels_

        # Calcular a média de frequência cardíaca e calorias por cluster
        cluster_means = self.df.groupby('cluster')[['heart_rate_avg', 'calories']].mean()

        # Ordenar os clusters por calorias e atribuir rótulos baseados nas médias
        sorted_clusters = cluster_means.sort_values(by='calories')
        cluster_labels = {sorted_clusters.index[0]: 'Baixa Intensidade',
                          sorted_clusters.index[1]: 'Intensidade Moderada',
                          sorted_clusters.index[2]: 'Alta Intensidade'}
        self.df['cluster_category'] = self.df['cluster'].map(cluster_labels)

        # Definir cores para cada categoria de cluster
        color_map = {
            'Baixa Intensidade': 'green',
            'Intensidade Moderada': 'blue',
            'Alta Intensidade': 'red'
        }

        # Filtrar o DataFrame pelo mês e ano selecionados
        mes_selecionado_num = {v: k for k, v in self.meses_pt.items()}[self.selected_month_Intensity]
        df_filtrado = self.df[
            (self.df['start_time'].dt.year == self.selected_year_Intensity) &
            (self.df['start_time'].dt.month == mes_selecionado_num)
            ]

        return [df_filtrado, color_map, self.selected_month_Intensity, self.selected_year_Intensity]

    # Função ajustada para resumo diário sem data específica
    def col2_resumo_diario(self):
        # Carrega os dados
        bio_data_full = self.loadFile.load_bio_data()  # Supondo que retorna o JSON de bio_data
        set_data = self.loadFile.load_set_data()  # Supondo que retorna o JSON de schedule

        # Calcula as médias dos últimos 5 treinos e obtém os treinos
        calorias, frequencia_media, frequencia_maxima, duracao_diaria, last_5_workouts = self.dashboardUtils.get_calories_last_5_workouts(bio_data_full)

        # Calcula o número total de exercícios planejados para as datas dos últimos 5 treinos
        numero_exercicios = 0
        for workout in last_5_workouts:
            workout_date_str = workout["date"].strftime("%Y-%m-%d")  # Converte a data do treino para string
            if workout_date_str in set_data["schedule"]:
                numero_exercicios += sum(
                    len(exercise["sets"]) for exercise in set_data["schedule"][workout_date_str]["exercises"])

        return [calorias, frequencia_media, frequencia_maxima, duracao_diaria, numero_exercicios]

    import pandas as pd
    from sklearn.cluster import KMeans

    def col3_indicador(self):

        # Carrega os dados
        bio_data_full = self.loadFile.load_bio_data()
        set_data = self.loadFile.load_set_data()

        # Criar bio_data_df
        bio_data_df = pd.DataFrame(bio_data_full)
        bio_data_df["Data"] = pd.to_datetime(bio_data_df["start_time"]).dt.date
        bio_data_df["Calorias"] = bio_data_df["calories"]
        bio_data_df["Duração"] = (pd.to_timedelta(bio_data_df["duration"]) / pd.Timedelta(seconds=1)) / 60
        bio_data_df["FC_Max"] = bio_data_df["heart_rate"].apply(
            lambda x: x.get("maximum", 0) if isinstance(x, dict) else 0)
        bio_data_df["FC_Media"] = bio_data_df["heart_rate"].apply(
            lambda x: x.get("average", 0) if isinstance(x, dict) else 0)

        treino_data_df = pd.DataFrame(set_data["schedule"].values())
        treino_data_df["Data"] = pd.to_datetime(treino_data_df.index).date
        treino_data_df = treino_data_df.explode("exercises")
        treino_data_df = treino_data_df.reset_index(drop=True)
        treino_data_df["Exercício"] = treino_data_df["exercises"].apply(
            lambda x: x["sets"] if isinstance(x, dict) else None)

        # Merge dos DataFrames
        treino_data_df = treino_data_df.merge(
            bio_data_df[["Data", "Calorias", "Duração", "FC_Max", "FC_Media"]],
            on="Data",
            how="left"
        )

        # Filtrar dados pelo mês e ano selecionados
        mes_selecionado = [k for k, v in self.meses_pt.items() if v == self.selected_month_Intensity][0]
        treino_data_filtrado = treino_data_df[
            (pd.to_datetime(treino_data_df["Data"]).dt.year == self.selected_year_Intensity) &
            (pd.to_datetime(treino_data_df["Data"]).dt.month == mes_selecionado)
            ]

        # Agrupar e somar métricas por mês e exercício
        calorias_por_mes = treino_data_filtrado.groupby(["Data", "Exercício"], as_index=False).sum(
            numeric_only=True)

        # Converter a coluna "Data" para datetime, se ainda não estiver
        bio_data_df["Data"] = pd.to_datetime(bio_data_df["Data"], errors='coerce')

        # Filtrar os dados de bio_data_df com base no ano e mês selecionados
        bio_data_filtrado = bio_data_df[
            (bio_data_df["Data"].dt.year == self.selected_year_Intensity) &
            (bio_data_df["Data"].dt.month == mes_selecionado)
            ]

        # Aplicar K-means para classificar a intensidade do treino
        X = bio_data_filtrado[['FC_Media', 'Calorias']].dropna()

        if len(X) >= 3:
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            bio_data_filtrado['cluster'] = kmeans.fit_predict(X)

            # Calcular a média de calorias e FC_Media por cluster
            cluster_means = bio_data_filtrado.groupby('cluster')[['FC_Media', 'Calorias']].mean()

            # Ordenar clusters pelo gasto calórico e atribuir rótulos
            sorted_clusters = cluster_means.sort_values(by='Calorias')
            cluster_labels = {
                sorted_clusters.index[0]: 'Baixa Intensidade',
                sorted_clusters.index[1]: 'Intensidade Moderada',
                sorted_clusters.index[2]: 'Alta Intensidade'
            }
            bio_data_filtrado['cluster_category'] = bio_data_filtrado['cluster'].map(cluster_labels)
        else:
            bio_data_filtrado['cluster_category'] = 'Baixa Intensidade'  # Default caso não haja dados suficientes

        # Criar dicionário de cores igual ao da função `col1_intensidade_treino`
        color_map = {
            'Baixa Intensidade': 'green',
            'Intensidade Moderada': 'blue',
            'Alta Intensidade': 'red'
        }

        return [bio_data_filtrado, self.selected_month_Intensity, calorias_por_mes, color_map]

    def col4_exercícios_por_categoria(self):
        bio_data_full = self.loadFile.load_bio_data()  # Supondo que retorna o JSON de bio_data
        set_data = self.loadFile.load_set_data()  # Supondo que retorna o JSON de schedule

        # Calcula as médias dos últimos 5 treinos e obtém os treinos
        calorias, frequencia_media, frequencia_maxima, duracao_diaria, last_5_workouts = self.dashboardUtils.get_calories_last_5_workouts(bio_data_full)

        # Lista para armazenar os dados de data e tipo
        data_tipo = []

        # Itera sobre os últimos 5 treinos
        for workout in last_5_workouts:
            workout_date_str = workout["date"].strftime("%Y-%m-%d")  # Converte a data do treino para string
            tipo_treino = "Não agendado"  # Valor padrão se não houver agendamento
            if workout_date_str in set_data["schedule"]:
                tipo_treino = set_data["schedule"][workout_date_str].get("type", "Desconhecido")

            # Adiciona a data e o tipo à lista
            data_tipo.append({
                "Data": workout_date_str,
                "Tipo": tipo_treino
            })

        # Retorna um DataFrame com os dados, ou vazio se não houver treinos
        if data_tipo:
            return pd.DataFrame(data_tipo)
        else:
            return pd.DataFrame(columns=["Data", "Tipo"])

    def parse_duration(self, duration_str):
        """Converte duração no formato ISO 8601 (ex.: PT3370S) para minutos."""
        match = re.match(r"PT([\d.]+)S", duration_str)
        if match:
            seconds = float(match.group(1))
            return seconds / 60
        return 30  # Valor padrão se não for possível converter

    def get_heart_rate_zone(self, avg_hr, max_hr):
        """Classifica a zona de intensidade cardíaca com base no texto fornecido."""
        percentage = (avg_hr / max_hr) * 100
        if percentage < 50:
            return "Zona 1 - Recuperação Ativa"
        elif 50 <= percentage <= 60:
            return "Zona 2 - Aeróbico Leve"
        elif 60 < percentage <= 70:
            return "Zona 3 - Aeróbico Moderado"
        elif 70 < percentage <= 85:
            return "Zona 4 - Limiar Anaeróbico"
        else:
            return "Zona 5 - Alta Intensidade / VO2 Máx"

    def mostrar_dados_de_treino_por_zona(self, mes, ano):
        """Prepara os dados de treino por zona de frequência cardíaca para o mês e ano especificados.

        Args:
            mes (int): Número do mês (1 a 12).
            ano (int): Ano (e.g., 2024).

        Returns:
            tuple: (zones, calories, counts) com as zonas, calorias totais e contagem de treinos por zona.
        """
        workouts = self.loadFile.load_bio_data()  # Supondo que retorna o JSON de bio_data
        if workouts is None:
            return [], [], []  # Retornar listas vazias se não houver dados

        # Inicializar dicionário com todas as zonas possíveis usando os nomes completos
        zone_data = {
            "Zona 1 - Recuperação Ativa": {"calories": 0, "count": 0},
            "Zona 2 - Aeróbico Leve": {"calories": 0, "count": 0},
            "Zona 3 - Aeróbico Moderado": {"calories": 0, "count": 0},
            "Zona 4 - Limiar Anaeróbico": {"calories": 0, "count": 0},
            "Zona 5 - Alta Intensidade / VO2 Máx": {"calories": 0, "count": 0}
        }

        # Definir o intervalo de datas para o mês e ano especificados
        from datetime import datetime
        data_inicio = datetime(ano, mes, 1)
        data_fim = datetime(ano, mes + 1, 1) if mes < 12 else datetime(ano + 1, 1, 1)

        # Filtrar treinos pelo mês e ano
        filtered_workouts = [
            workout for workout in workouts
            if "start_time" in workout and workout["start_time"]
               and data_inicio <= datetime.strptime(workout["start_time"], '%Y-%m-%dT%H:%M:%S') < data_fim
        ]

        # Processar cada treino filtrado e acumular calorias e contagem por zona
        for workout in filtered_workouts:
            avg_hr = workout["heart_rate"]["average"]
            max_hr = workout["heart_rate"].get("maximum", 200)  # Usar 200 como padrão se não fornecido
            calories = workout["calories"]
            zone = self.get_heart_rate_zone(avg_hr, max_hr)
            zone_data[zone]["calories"] += calories
            zone_data[zone]["count"] += 1

        # Extrair dados para plotagem
        zones = list(zone_data.keys())
        calories = [zone_data[zone]["calories"] for zone in zones]
        counts = [zone_data[zone]["count"] for zone in zones]

        return zones, calories, counts






