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
            self.data_selecionada_card_table = st.date_input("Data", value=pd.to_datetime(treino_data["Data"].max()))
            calorias, frequencia_media, frequencia_maxima, duracao_diaria, numero_exercicios = self.service.col2_resumo_diario(self.data_selecionada_card_table)

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
            st.subheader("Tabela de Exercícios por Categoria")
            with st.expander("Exercícios"):


                tabela_categorias_dia = self.service.col4_exercícios_por_categoria(self.data_selecionada_card_table)

                # Exibir a tabela no Plotly se houver dados
                if not tabela_categorias_dia.empty:
                    #st.write(f"Exibindo dados para a data: {data_selecionada.strftime('%Y-%m-%d')}")

                    fig = go.Figure(
                        data=[go.Table(
                            columnorder=[1, 2, 3, 4],
                            columnwidth=[20, 30, 20, 20],  # Ajuste de largura das colunas
                            header=dict(
                                values=list(tabela_categorias_dia.columns),
                                font=dict(size=14, color='white'),
                                fill_color='#264653',
                                align=['left', 'center'],
                                height=30
                            ),
                            cells=dict(
                                values=[tabela_categorias_dia[col].tolist() for col in tabela_categorias_dia.columns],
                                font=dict(size=12, color='black'),
                                fill_color=[['#F6F6F6', '#E8E8E8'] * (len(tabela_categorias_dia) // 2)],
                                align=['left', 'center'],
                                height=25
                            )
                        )]
                    )

                    fig.update_layout(
                        title_text="",
                        title_font=dict(size=18, color='#264653'),
                        margin=dict(l=0, r=10, b=10, t=40),
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("Nenhum exercício encontrado para a data selecionada.")

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
