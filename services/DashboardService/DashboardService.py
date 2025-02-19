import json

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

    def col1_intensidade_treino(self):

        # Obtendo os dados da classe Utils
        json_data, df, meses_pt, selected_month_Intensity, selected_year_Intensity = self.dashboardUtils.selected_month_year_Intensity()

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

        calorias, frequencia_media, frequencia_maxima, duracao_diaria = self.dashboardUtils.get_calories_by_date(
            bio_data_full, data_selecionada)

        if data_str in set_data["schedule"]:
            numero_exercicios = sum(len(exercise["sets"]) for exercise in set_data["schedule"][data_str]["exercises"])

        return [calorias, frequencia_media, frequencia_maxima, duracao_diaria, numero_exercicios]

    def col3_indicador(self):


        # Obtendo os dados da classe Utils
        json_data, df, meses_pt, selected_month_Intensity, selected_year_Intensity = self.dashboardUtils.selected_month_year_Intensity("1")

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
        mes_selecionado = [k for k, v in meses_pt.items() if v == selected_month_Intensity][0]
        treino_data_filtrado = treino_data_df[
            (pd.to_datetime(treino_data_df["Data"]).dt.year == selected_year_Intensity) &
            (pd.to_datetime(treino_data_df["Data"]).dt.month == mes_selecionado)
            ]

        # Agrupar e somar métricas por mês e exercício
        calorias_por_mes = treino_data_filtrado.groupby(["Data", "Exercício"], as_index=False).sum(
            numeric_only=True)


        # Converter a coluna "Data" para datetime, se ainda não estiver
        bio_data_df["Data"] = pd.to_datetime(bio_data_df["Data"], errors='coerce')

        # Filtrar os dados de bio_data_df com base no ano e mês selecionados
        bio_data_filtrado = bio_data_df[
            (bio_data_df["Data"].dt.year == selected_year_Intensity) &
            (bio_data_df["Data"].dt.month == [k for k, v in meses_pt.items() if v == selected_month_Intensity][
                0])
            ]

        return [bio_data_filtrado, selected_month_Intensity, calorias_por_mes]



    def col4_exercícios_por_categoria(self, data_selecionada):

        st.subheader("Tabela de Exercícios por Categoria")
        treino_data = self.dashboardUtils.load_treino_data()
        set_data = self.loadFile.load_set_data()


        data_str = data_selecionada.strftime("%Y-%m-%d")  # Formatar a data para string

        # Verificar se a data está no conjunto de dados
        if data_str not in set_data.get("schedule", {}):
            st.write(f"Data {data_str} não encontrada no cronograma.")
            return pd.DataFrame(columns=["Categoria", "Exercício", "Detalhe 1", "Detalhe 2"])

        # Processar os exercícios do dia
        categorias_sets = []
        exercicios = set_data["schedule"][data_str].get("exercises", [])
        if not exercicios:
            st.write(f"Nenhum exercício encontrado para a data {data_str}.")
            return pd.DataFrame(columns=["Categoria", "Exercício", "Detalhe 1", "Detalhe 2"])

        # Iterar pelos exercícios
        for ex in exercicios:
            categoria = ex.get("category", "Desconhecida")
            sets = ex.get("sets", [])

            if sets:  # Se houver sets, processa
                if isinstance(sets[0], dict):  # Estrutura com dicionários
                    for set_item in sets:
                        exercicio = set_item.get('exercise', 'Sem exercício')
                        detalhes = set_item.get('details', '').split(', ')
                        detalhes_preenchidos = detalhes + [''] * (2 - len(detalhes))
                        categorias_sets.append({
                            "Categoria": categoria,
                            "Exercício": exercicio,
                            "Detalhe 1": detalhes_preenchidos[0],
                            "Detalhe 2": detalhes_preenchidos[1]
                        })
                else:  # Estrutura com strings simples
                    for exercicio in sets:
                        categorias_sets.append({
                            "Categoria": categoria,
                            "Exercício": exercicio,
                            "Detalhe 1": "",
                            "Detalhe 2": ""
                        })
            else:  # Caso a lista de sets esteja vazia
                categorias_sets.append({
                    "Categoria": categoria,
                    "Exercício": "Sem exercício",
                    "Detalhe 1": "",
                    "Detalhe 2": ""
                })

        # Criar e retornar o DataFrame
        return pd.DataFrame(categorias_sets)



