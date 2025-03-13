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
        self.data_selecionada_card_table = None

    def create_intensity_chart(self):

        st.set_page_config(page_title='Dashboard - Treino', layout='wide')


        # st.sidebar.header("Olá, seja muito bem vindo!")
        st.sidebar.header("Olá, Samilly Batista")
        st.sidebar.write(f"Peso: 75 kg")
        st.sidebar.write(f"Altura: 1.45 cm")
        # st.sidebar.write(f"Data do treino: {data_treino.strftime('%d/%m/%Y %H:%M')}")



        treino_data = self.dashboardUtils.load_treino_data()

        img_heart_solid = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images/heart-solid.svg")
        img_heart_solid_pulse = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             "../images/heart-pulse-solid.svg")
        img_fire_solid = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images/fire-solid.svg")

        # Lendo o conteúdo do arquivo SVG corretamente
        with open(img_heart_solid, "r") as file:
            svg_heart_solid = file.read()

        with open(img_heart_solid_pulse, "r") as file:
            svg_heart_solid_pulse = file.read()

        with open(img_fire_solid, "r") as file:
            svg_fire_solid = file.read()

        # Criando as métricas em colunas
        m1, m2, m3, m4, m5 = st.columns((1, 1, 1, 1, 1))

        with m1:
            calorias, frequencia_media, frequencia_maxima, duracao_diaria, numero_exercicios = self.service.col2_resumo_diario()

        with m2:
            st.markdown(f"""
                    <div style="text-align: center;">
                        <h4>Freq. Cardíaca Média</h4>
                        <h2 style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                            <span style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                                <div style="width: 100%; height: 100%; color: red; fill: red;">
                                    {svg_heart_solid}
                                </div>
                            </span>
                            {frequencia_media} bpm
                        </h2>
                    </div>
                """, unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
                    <div style="text-align: center;">
                        <h4>Freq.Cardíaca Máxima</h4>
                        <h2 style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                            <span style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                                <div style="width: 100%; height: 100%; color: red; fill: red;">
                                    {svg_heart_solid_pulse}
                                </div>
                            </span>
                            {frequencia_maxima} bpm
                        </h2>
                    </div>
                """, unsafe_allow_html=True)

        with m4:
            st.markdown(f"""
                   <div style="text-align: center;">
                       <h4>Calorias Perdidas</h4>
                       <h2 style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                           <span style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                               <div style="width: 100%; height: 100%; color: red; fill: red;">
                                   {svg_fire_solid}
                               </div>
                           </span>
                           {calorias}
                       </h2>
                   </div>
               """, unsafe_allow_html=True)

        # Cria colunas para o grid de 2 gráficos
        col1, col2 = st.columns(2)

        """Cria o gráfico de intensidade do treino e exibe no Streamlit."""

        with col1:
            st.subheader("Intensidade do Treino")

            # Obtendo os dados do serviço
            df_filtrado, color_map = self.service.col1_intensidade_treino()

            # Verifica se há dados antes de criar o gráfico
            if df_filtrado.empty:
                st.warning("Nenhum dado disponível para o período selecionado.")
                return

            # Agrupar os dados por categoria e somar as médias
            df_cumulativo = df_filtrado.groupby('cluster_category')['heart_rate_avg'].sum().reset_index()

            # Gráfico de barras
            fig = px.bar(
                df_cumulativo,
                x='cluster_category',
                y='heart_rate_avg',
                color='cluster_category',
                color_discrete_map=color_map,
                labels={
                    'heart_rate_avg': 'Frequência Cardíaca Média (bpm)',
                    'cluster_category': 'Intensidade do Treino'
                },
                category_orders={"cluster_category": ["Alta Intensidade", "Intensidade Moderada", "Baixa Intensidade"]}
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:

            st.subheader("Indicador")

            # Obtendo os dados da classe Utils
            bio_data_filtrado, selected_month_Intensity, calorias_por_mes = self.service.col3_indicador()

            # Selecionar métrica para visualização
            metric_options = ["Calorias", "Duração", "Frequência Cardíaca Máxima", "Frequência Cardíaca Média"]
            selected_metric = st.selectbox("", metric_options)

            if selected_metric == "Calorias":

                # Criar um DataFrame para plotar todas as calorias queimadas
                calorias_por_mes = pd.DataFrame({
                    "Data": bio_data_filtrado["Data"],
                    "Calorias Queimadas": bio_data_filtrado["Calorias"]
                })

                # Gráfico de dispersão
                fig_calorias = px.scatter(
                    calorias_por_mes,
                    x="Data",
                    y="Calorias Queimadas",
                    title=f"Calorias Queimadas Mensais - {selected_month_Intensity}",
                    labels={"Data": "Data", "Calorias Queimadas": "Calorias"},
                    color="Calorias Queimadas",
                    color_continuous_scale="Viridis"
                )

                fig_calorias.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Calorias",
                    template="plotly_dark",
                    xaxis=dict(tickangle=45)
                )

                st.plotly_chart(fig_calorias, use_container_width=True)

            elif selected_metric == "Duração":
                duracoes_por_mes = pd.DataFrame({
                    "Data": bio_data_filtrado["Data"],
                    "Duração do Treino": bio_data_filtrado["Duração"]
                })

                fig_duracao = px.scatter(
                    duracoes_por_mes,
                    x="Data",
                    y="Duração do Treino",
                    title=f"Durações do Treino Mensais - {selected_month_Intensity}",
                    labels={"Data": "Data", "Duração do Treino": "Duração (minutos)"},
                    color="Duração do Treino",
                    color_continuous_scale="Viridis"
                )

                fig_duracao.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Duração (minutos)",
                    template="plotly_dark",
                    xaxis=dict(tickangle=45)
                )

                st.plotly_chart(fig_duracao, use_container_width=True)

            elif selected_metric == "Frequência Cardíaca Máxima":
                frequencias_por_mes = pd.DataFrame({
                    "Data": bio_data_filtrado["Data"],
                    "Frequência Cardíaca": bio_data_filtrado["FC_Max"]
                })

                fig_frequencia = px.scatter(
                    frequencias_por_mes,
                    x="Data",
                    y="Frequência Cardíaca",
                    title=f"Frequências Cardíacas Mensais - {selected_month_Intensity}",
                    labels={"Data": "Data", "Frequência Cardíaca": "Frequência Cardíaca (bpm)"},
                    color="Frequência Cardíaca",
                    color_continuous_scale="Viridis"
                )

                fig_frequencia.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Frequência Cardíaca (bpm)",
                    template="plotly_dark",
                    xaxis=dict(tickangle=45)
                )

                st.plotly_chart(fig_frequencia, use_container_width=True)

            else:
                frequencias_media_por_mes = pd.DataFrame({
                    "Data": bio_data_filtrado["Data"],
                    "Frequência Cardíaca Média": bio_data_filtrado["FC_Media"]
                })

                fig_frequencia_media = px.scatter(
                    frequencias_media_por_mes,
                    x="Data",
                    y="Frequência Cardíaca Média",
                    title=f"Frequências Cardíacas Médias Mensais - {selected_month_Intensity}",
                    labels={"Data": "Data", "Frequência Cardíaca Média": "Frequência Cardíaca (bpm)"},
                    color="Frequência Cardíaca Média",
                    color_continuous_scale="Viridis"
                )

                fig_frequencia_media.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Frequência Cardíaca (bpm)",
                    template="plotly_dark",
                    xaxis=dict(tickangle=45)
                )

                st.plotly_chart(fig_frequencia_media, use_container_width=True)




        st.subheader("📌 Tabela de Treinos Recentes")

        with st.expander("📋 Últimos 5 Treinos"):
            # Carregar os dados da função de serviço
            tabela_categorias_dia = self.service.col4_exercícios_por_categoria()

            if not tabela_categorias_dia.empty:
                # Criar figura do Plotly com tabela formatada
                fig = go.Figure(
                    data=[go.Table(
                        columnorder=[1, 2],
                        columnwidth=[20, 50],  # Ajuste das larguras das colunas
                        header=dict(
                            values=["📅 Data", "🏋️ Tipo"],
                            font=dict(size=14, color='white'),
                            fill_color='#264653',
                            align=['left', 'center'],
                            height=30
                        ),
                        cells=dict(
                            values=[
                                tabela_categorias_dia["Data"].tolist(),
                                tabela_categorias_dia["Tipo"].tolist()
                            ],
                            font=dict(size=12, color='black'),
                            fill_color=[['#F6F6F6', '#E8E8E8'] * (len(tabela_categorias_dia) // 2)],
                            align=['left', 'center'],
                            height=25
                        )
                    )]
                )

                # Layout da tabela
                fig.update_layout(
                    title_text="📊 Resumo dos Últimos 5 Treinos",
                    title_font=dict(size=18, color='#264653'),
                    margin=dict(l=0, r=10, b=10, t=40),
                    height=300  # Ajustei a altura para uma tabela menor
                )

                # Exibir tabela
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Nenhum treino encontrado para os últimos 5 registros.")





