import os

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.DashboardService.DashboardService import DashboardService
from services.DashboardService.DashboardUtils import DashboardUtils


class DashboardView:

    def __init__(self):
        self.service = DashboardService()
        self.dashboardUtils = DashboardUtils()

    def create_intensity_chart(self):

        st.set_page_config(page_title='Dashboard - Treino', layout='wide')

        # this is the header

        t1, t2 = st.columns((0.07, 1))

        t1.image(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images/index.png"), width=120)
        t2.title("South Western Ambulance Service - Hospital Handover Report")
        t2.markdown(
            " **tel:** 01392 451192 **| website:** https://www.swast.nhs.uk **| email:** mailto:data.science@swast.nhs.uk")

        """Cria o gráfico de intensidade do treino e exibe no Streamlit."""
        col1, col2 = st.columns(2)




        with col1:
            st.subheader("Intensidade do Treino")
            # Obtendo os dados do serviço
            df_filtrado, color_map = self.service.col1_intensidade_treino()


            # Verifica se há dados antes de criar o gráfico
            if df_filtrado.empty:
                st.warning("Nenhum dado disponível para o período selecionado.")
                return

            # Gráfico de barras
            fig = px.bar(
                df_filtrado,
                x='Data',
                y='heart_rate_avg',
                color='cluster_category',
                color_discrete_map=color_map,
                labels={
                    'heart_rate_avg': 'Frequência Cardíaca Média (bpm)',
                    'Data': 'Data do Treino',
                    'cluster_category': 'Intensidade do Treino'
                },
                category_orders={"cluster_category": ["Alta Intensidade", "Intensidade Moderada", "Baixa Intensidade"]}
            )

            st.plotly_chart(fig, use_container_width=True)





        with col2:
            st.subheader("Resumo Diário")
            # Obtendo os dados do serviço
            calorias, frequencia_media, frequencia_maxima, duracao_diaria, numero_exercicios = self.service.col2_resumo_diario()


            col_icon1, col_icon2 = st.columns(2)
            with col_icon1:
                st.metric("💛 Freq. Cardíaca Média (bpm)", int(frequencia_media))
                st.metric("❤️ Freq. Cardíaca Máxima (bpm)", int(frequencia_maxima))

            with col_icon2:
                st.metric("🔥 Calorias Perdidas", int(calorias))
                st.metric("⏱️ Duração Total (min)", int(duracao_diaria))
                st.metric("🏃 Número de Exercícios", numero_exercicios)



        st.subheader("Indicador")

        # Obtendo os dados da classe Utils
        bio_data_filtrado, selected_month_Intensity, calorias_por_mes = self.service.col3_indicador()

        # Selecionar métrica para visualização
        metric_options = ["Calorias", "Duração", "Frequência Cardíaca Máxima", "Frequência Cardíaca Média"]
        selected_metric = st.selectbox("Indicador:", metric_options)

        if selected_metric == "Calorias":

            # Criar um DataFrame para plotar todas as calorias queimadas
            calorias_por_mes = pd.DataFrame({
                "Data": bio_data_filtrado["Data"],
                "Calorias Queimadas": bio_data_filtrado["Calorias"]  # Supondo que a coluna se chama "Calorias"
            })

            # Plotar gráfico
            # Criar o gráfico de calorias queimadas
            fig_calorias = px.line(
                calorias_por_mes,
                x="Data",
                y="Calorias Queimadas",
                markers=True,
                title=f"Calorias Queimadas Mensais - {selected_month_Intensity}",
                labels={"Data": "Data", "Calorias Queimadas": "Calorias"},
            )

            # Atualizar o layout do gráfico
            fig_calorias.update_layout(
                xaxis_title="Data",
                yaxis_title="Calorias",
                template="plotly_dark",
                xaxis=dict(tickangle=45)
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig_calorias, use_container_width=True)

        elif selected_metric == "Duração":
            # Criar um DataFrame para plotar todas as durações do treino
            duracoes_por_mes = pd.DataFrame({
                "Data": bio_data_filtrado["Data"],
                "Duração do Treino": bio_data_filtrado["Duração"]  # Supondo que a coluna se chama "Duração"
            })

            # Plotar gráfico
            # Criar o gráfico de durações do treino
            fig_duracao = px.line(
                duracoes_por_mes,
                x="Data",
                y="Duração do Treino",
                markers=True,
                title=f"Durações do Treino Mensais - {selected_month_Intensity}",
                labels={"Data": "Data", "Duração do Treino": "Duração (minutos)"},
                line_shape='linear'  # Forma da linha (pode ser ajustada conforme necessário)
            )

            # Atualizar o layout do gráfico
            fig_duracao.update_layout(
                xaxis_title="Data",
                yaxis_title="Duração (minutos)",
                template="plotly_dark",
                xaxis=dict(tickangle=45)
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig_duracao, use_container_width=True)

        elif selected_metric == "Frequência Cardíaca Máxima":
            # Criar um DataFrame para plotar todas as frequências cardíacas
            frequencias_por_mes = pd.DataFrame({
                "Data": bio_data_filtrado["Data"],
                "Frequência Cardíaca": bio_data_filtrado["FC_Max"]
                # Supondo que a coluna se chama "Frequência Cardíaca"
            })

            # Criar o gráfico de frequências cardíacas
            fig_frequencia = px.line(
                frequencias_por_mes,
                x="Data",
                y="Frequência Cardíaca",
                markers=True,
                title=f"Frequências Cardíacas Mensais - {selected_month_Intensity}",
                labels={"Data": "Data", "Frequência Cardíaca": "Frequência Cardíaca (bpm)"},
            )

            # Atualizar o layout do gráfico
            fig_frequencia.update_layout(
                xaxis_title="Data",
                yaxis_title="Frequência Cardíaca (bpm)",
                template="plotly_dark",
                xaxis=dict(tickangle=45)
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig_frequencia, use_container_width=True)

        else:
            # Criar um DataFrame para plotar todas as frequências cardíacas médias
            frequencias_media_por_mes = pd.DataFrame({
                "Data": bio_data_filtrado["Data"],
                "Frequência Cardíaca Média": bio_data_filtrado["FC_Media"]
                # Supondo que a coluna se chama "FC_Media"
            })

            # Criar o gráfico de frequências cardíacas médias
            fig_frequencia_media = px.line(
                frequencias_media_por_mes,
                x="Data",
                y="Frequência Cardíaca Média",
                markers=True,
                title=f"Frequências Cardíacas Médias Mensais - {selected_month_Intensity}",
                labels={"Data": "Data", "Frequência Cardíaca Média": "Frequência Cardíaca (bpm)"},
            )

            # Atualizar o layout do gráfico
            fig_frequencia_media.update_layout(
                xaxis_title="Data",
                yaxis_title="Frequência Cardíaca (bpm)",
                template="plotly_dark",
                xaxis=dict(tickangle=45)
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig_frequencia_media, use_container_width=True)


        st.subheader("Tabela de Exercícios por Categoria")
        with st.expander("Exercícios"):

            self.service.col4_exercícios_por_categoria()



