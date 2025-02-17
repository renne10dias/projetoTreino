import os
import re
import streamlit as st

import pandas as pd
from sklearn.cluster import KMeans

from services.DashboardService.DashboardUtils import DashboardUtils
from utils.DataLoader import DataLoader
from utils.LoadFile import LoadFile


class DashboardService:
    def __init__(self):
        self.loadFile = LoadFile()
        self.dashboardUtils = DashboardUtils()

    def col1_intensidade_treino(self):
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
                key="mes_intensidade"
            )
        with col1_2:
            selected_year_Intensity = st.selectbox(
                "Selecione o ano",
                anos_unicos_Intensity,
                key="ano_intensidade"
            )

        # Adicionar dados de frequência cardíaca ao DataFrame
        heart_rate_data = [entry["heart_rate"]["average"] for entry in json_data]
        df['heart_rate_avg'] = heart_rate_data

        # Selecionar as colunas para o clustering
        X = df[['heart_rate_avg', 'calories']]

        # Aplicar K-means com 3 clusters
        kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
        df['cluster'] = kmeans.labels_

        # Calcular a média de frequência cardíaca e calorias por cluster
        cluster_means = df.groupby('cluster')[['heart_rate_avg', 'calories']].mean()

        # Ordenar os clusters por calorias e atribuir rótulos baseados nas médias
        sorted_clusters = cluster_means.sort_values(by='calories')
        cluster_labels = {sorted_clusters.index[0]: 'Baixa Intensidade',
                          sorted_clusters.index[1]: 'Intensidade Moderada',
                          sorted_clusters.index[2]: 'Alta Intensidade'}
        df['cluster_category'] = df['cluster'].map(cluster_labels)

        # Definir cores para cada categoria de cluster
        color_map = {
            'Baixa Intensidade': 'green',
            'Intensidade Moderada': 'blue',
            'Alta Intensidade': 'red'
        }

        # Filtrar o DataFrame pelo mês e ano selecionados
        mes_selecionado_num = {v: k for k, v in meses_pt.items()}[selected_month_Intensity]
        df_filtrado = df[
            (df['start_time'].dt.year == selected_year_Intensity) &
            (df['start_time'].dt.month == mes_selecionado_num)
            ]

        return [df_filtrado, color_map]





    def col2_resumo_diario(self):
        # Carrega os dados
        treino_data = self.dashboardUtils.load_treino_data()
        bio_data_full = self.loadFile.load_bio_data()
        set_data = self.loadFile.load_set_data()

        data_selecionada = st.date_input("Data", value=pd.to_datetime(treino_data["Data"].max()))

        data_str = data_selecionada.strftime("%Y-%m-%d")
        numero_exercicios = 0

        calorias, frequencia_media, frequencia_maxima, duracao_diaria = self.dashboardUtils.get_calories_by_date(bio_data_full, data_selecionada)


        if data_str in set_data["schedule"]:
            numero_exercicios = sum(len(exercise["sets"]) for exercise in set_data["schedule"][data_str]["exercises"])




        return [calorias, frequencia_media, frequencia_maxima, duracao_diaria, numero_exercicios]


