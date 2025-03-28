import os

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import pyplot as plt

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

        calorias, frequencia_media, frequencia_maxima, duracao_diaria, numero_exercicios = self.service.col2_resumo_diario()

        st.markdown(
            "<h2 style='text-align: left;'>Últimos 5 Treinos</h2>",
            unsafe_allow_html=True
        )

        # Criando as métricas em colunas
        m1, m2, m3, m4, m5 = st.columns((1, 1, 1, 1, 1))

        with m1:
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


        with m2:
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


        with m3:
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
            st.markdown(
                "<br><h2 style='text-align: left;'>Intensidade do Treino</h2>",
                unsafe_allow_html=True
            )

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
            st.markdown(
                "<br><h2 style='text-align: left;'>Indicador</h2>",
                unsafe_allow_html=True
            )

            # Obtendo os dados da classe Utils
            bio_data_filtrado, selected_month_Intensity, calorias_por_mes, color_map = self.service.col3_indicador()

            # Selecionar métrica para visualização
            metric_options = ["Calorias", "Duração", "Frequência Cardíaca Máxima", "Frequência Cardíaca Média"]
            selected_metric = st.selectbox("", metric_options)

            # Definir cores com base na intensidade do treino
            bio_data_filtrado["cluster_category"] = bio_data_filtrado["cluster_category"].astype(str)

            # Criar dicionário de cores a partir da função anterior
            category_colors = color_map

            if selected_metric == "Calorias":
                df_plot = pd.DataFrame({
                    "Data": bio_data_filtrado["Data"],
                    "Calorias Queimadas": bio_data_filtrado["Calorias"],
                    "Intensidade": bio_data_filtrado["cluster_category"]
                })

                fig_calorias = px.scatter(
                    df_plot,
                    x="Data",
                    y="Calorias Queimadas",
                    title=f"Calorias Queimadas Mensais - {selected_month_Intensity}",
                    labels={"Data": "Data", "Calorias Queimadas": "Calorias"},
                    color="Intensidade",
                    color_discrete_map=category_colors
                )

            elif selected_metric == "Duração":
                df_plot = pd.DataFrame({
                    "Data": bio_data_filtrado["Data"],
                    "Duração do Treino": bio_data_filtrado["Duração"],
                    "Intensidade": bio_data_filtrado["cluster_category"]
                })

                fig_calorias = px.scatter(
                    df_plot,
                    x="Data",
                    y="Duração do Treino",
                    title=f"Durações do Treino Mensais - {selected_month_Intensity}",
                    labels={"Data": "Data", "Duração do Treino": "Duração (minutos)"},
                    color="Intensidade",
                    color_discrete_map=category_colors
                )

            elif selected_metric == "Frequência Cardíaca Máxima":
                df_plot = pd.DataFrame({
                    "Data": bio_data_filtrado["Data"],
                    "Frequência Cardíaca": bio_data_filtrado["FC_Max"],
                    "Intensidade": bio_data_filtrado["cluster_category"]
                })

                fig_calorias = px.scatter(
                    df_plot,
                    x="Data",
                    y="Frequência Cardíaca",
                    title=f"Frequências Cardíacas Máximas - {selected_month_Intensity}",
                    labels={"Data": "Data", "Frequência Cardíaca": "Frequência Cardíaca (bpm)"},
                    color="Intensidade",
                    color_discrete_map=category_colors
                )

            else:  # Frequência Cardíaca Média
                df_plot = pd.DataFrame({
                    "Data": bio_data_filtrado["Data"],
                    "Frequência Cardíaca Média": bio_data_filtrado["FC_Media"],
                    "Intensidade": bio_data_filtrado["cluster_category"]
                })

                fig_calorias = px.scatter(
                    df_plot,
                    x="Data",
                    y="Frequência Cardíaca Média",
                    title=f"Frequências Cardíacas Médias - {selected_month_Intensity}",
                    labels={"Data": "Data", "Frequência Cardíaca Média": "Frequência Cardíaca (bpm)"},
                    color="Intensidade",
                    color_discrete_map=category_colors
                )

            fig_calorias.update_layout(
                xaxis_title="Data",
                template="plotly_dark",
                xaxis=dict(tickangle=45)
            )

            st.plotly_chart(fig_calorias, use_container_width=True)




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


        # Custom title using Markdown (white text for dark mode)
        st.markdown(
            "<h2 style='text-align: left; color: white;'>Calorias Totais e Número de Treinos por Zona de Frequência Cardíaca</h2>",
            unsafe_allow_html=True
        )

        # Get data from the service
        zones, calories, counts = self.service.mostrar_dados_de_treino_por_zona()

        # Create a DataFrame for Plotly
        df = pd.DataFrame({
            'Zonas': zones,
            'Calorias Totais': calories,
            'Número de Treinos': counts
        })

        # Create the figure using Plotly Graph Objects
        fig = go.Figure()

        # Add bar for Total Calories
        fig.add_trace(
            go.Bar(
                x=df['Zonas'],
                y=df['Calorias Totais'],
                name='Calorias Totais',
                marker_color='#4CAF50',  # Green color for calories
                text=[f'{int(val)}' for val in df['Calorias Totais']],  # Data labels
                textposition='auto',
                offsetgroup=1,  # Group for calories
                width=0.4  # Width of the bars
            )
        )

        # Add bar for Number of Workouts
        fig.add_trace(
            go.Bar(
                x=df['Zonas'],
                y=df['Número de Treinos'],
                name='Número de Treinos',
                marker_color='#FF5722',  # Orange color for workouts
                text=[f'{int(val)}' for val in df['Número de Treinos']],  # Data labels
                textposition='auto',
                offsetgroup=2,  # Group for workouts
                width=0.4,  # Width of the bars
                yaxis='y2'  # Secondary y-axis
            )
        )

        # Update layout for side-by-side bars and dark mode
        fig.update_layout(
            title=dict(
                text='Calorias Totais e Número de Treinos por Zona de Frequência Cardíaca',
                font=dict(size=14, color='white', family='Arial'),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title='Zonas de Frequência Cardíaca',
            yaxis=dict(
                title=dict(
                    text='Calorias Totais Queimadas',
                    font=dict(color='#4CAF50', size=12)
                ),
                tickfont=dict(color='#4CAF50'),
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            yaxis2=dict(
                title=dict(
                    text='Número de Treinos',
                    font=dict(color='#FF5722', size=12)
                ),
                tickfont=dict(color='#FF5722'),
                overlaying='y',
                side='right'
            ),
            barmode='group',  # Group bars side by side
            legend=dict(
                x=0.5,
                y=-0.1,
                xanchor='center',
                orientation='h',
                font=dict(size=11, color='white'),
                bgcolor='rgba(0, 0, 0, 0.5)'
            ),
            bargap=0.2,  # Gap between zone groups
            paper_bgcolor='black',
            plot_bgcolor='black',
            template='plotly_dark'
        )

        # Update traces for data label visibility
        fig.update_traces(
            textfont=dict(color='white')  # White text for data labels
        )

        # Render the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            "<br><h2 style='text-align: left;'>Diário de treino</h2>",
            unsafe_allow_html=True
        )

        with st.expander("📋 Lista os treinos"):
            tabela_categorias_dia = self.service.listar_exercicio_por_data()
            if tabela_categorias_dia is not None and not tabela_categorias_dia.empty:
                fig = go.Figure(
                    data=[go.Table(
                        columnorder=[1, 2],
                        columnwidth=[20, 50],
                        header=dict(
                            values=["<b>📅 Data</b>", "<b>🏋️ Tipo</b>"],
                            font=dict(size=14, color='white'),
                            fill_color='#264653',
                            align=['left', 'center'],
                            height=30
                        ),
                        cells=dict(
                            values=[
                                tabela_categorias_dia["Data"].tolist(),
                                tabela_categorias_dia["Categoria"].tolist()
                            ],
                            font=dict(size=12, color='black'),
                            fill_color=[
                                ['#F6F6F6' if i % 2 == 0 else '#E8E8E8' for i in
                                 range(len(tabela_categorias_dia))]
                            ],
                            align=['left', 'center'],
                            height=25
                        )
                    )]
                )

                fig.update_layout(
                    title_text="📊 Resumo dos Treinos do Dia",
                    title_font=dict(size=18, color='#264653'),
                    margin=dict(l=20, r=20, b=20, t=50),
                    height=300
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Nenhum treino encontrado para o dia selecionado.")




















