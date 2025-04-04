import os
import re

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
from datetime import datetime

from services.DashboardService.DashboardService import DashboardService
from services.DashboardService.DashboardUtils import DashboardUtils
from utils.LoadFile import LoadFile
from utils.PolarAccessLinkAdapter import PolarAccessLinkAdapter


class DashboardView:

    def __init__(self):
        self.service = DashboardService()
        self.dashboardUtils = DashboardUtils()
        self.loadFile = LoadFile()
        self.data_selecionada_card_table = None




    def exibir_informacoes_usuario(self):
        # Instanciar a classe adaptadora
        instancia = PolarAccessLinkAdapter()
        # Obter informações do usuário
        user_info = instancia.get_user_information()
        return user_info


    def create_intensity_chart(self):

        st.set_page_config(page_title='Dashboard - Treino', layout='wide')



        informacoes_usuario = self.exibir_informacoes_usuario()
        primeiro_nome = informacoes_usuario.get("first-name", "Atributo não encontrado")
        ultimo_nome = informacoes_usuario.get("last-name", "Atributo não encontrado")
        peso = informacoes_usuario.get("weight", "Atributo não encontrado")
        altura = informacoes_usuario.get("height", "Atributo não encontrado")

        # st.sidebar.header("Olá, seja muito bem vindo!")
        st.sidebar.header("Olá, " + primeiro_nome + " " + ultimo_nome)
        st.sidebar.write(f"Peso: {peso} kg")
        st.sidebar.write(f"Altura: {altura} cm")



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

        with st.container():
            # Gráfico 1: Calorias Totais e Número de Treinos por Zona
            st.markdown(
                "<h2 style='text-align: left;'>Calorias Totais e Número de Treinos por Zona de Frequência Cardíaca</h2>",
                unsafe_allow_html=True
            )

            # Obter dados de treino por zona
            workouts = self.loadFile.load_bio_data()
            # Obter dados de treino por zona
            zones, calories, counts = self.service.mostrar_dados_de_treino_por_zona()

            # Criar DataFrame para o gráfico de barras
            df = pd.DataFrame({
                'Zonas': zones,
                'Calorias Totais': calories,
                'Número de Treinos': counts
            })

            # Filtrar zonas sem dados (calorias e treinos = 0)
            df_filtrado = df[(df['Calorias Totais'] > 0) | (df['Número de Treinos'] > 0)]

            if df_filtrado.empty:
                st.warning("Nenhum dado disponível para exibir no gráfico de barras.")
            else:
                # Converter para formato longo para barras lado a lado
                df_long = pd.melt(
                    df_filtrado,
                    id_vars=['Zonas'],
                    value_vars=['Calorias Totais', 'Número de Treinos'],
                    var_name='Categoria',
                    value_name='Valor'
                )

                # Adicionar contagem original para hover
                df_long['Quantidade de Treinos'] = df_long['Zonas'].map(
                    df_filtrado.set_index('Zonas')['Número de Treinos'])

                # Mapa de cores para as zonas
                color_map = {
                    "Zona 1 - Recuperação Ativa": '#FF4B4B',  # Vermelho
                    "Zona 2 - Aeróbico Leve": '#4CAF50',      # Verde
                    "Zona 3 - Aeróbico Moderado": '#FFC107',  # Amarelo
                    "Zona 4 - Limiar Anaeróbico": '#1E88E5',  # Azul
                    "Zona 5 - Alta Intensidade / VO2 Máx": '#AB47BC'  # Roxo
                }

                # Criar gráfico de barras
                fig2 = px.bar(
                    df_long,
                    x='Zonas',
                    y='Valor',
                    color='Zonas',
                    color_discrete_map=color_map,
                    labels={
                        'Valor': 'Calorias Totais / Número de Treinos',
                        'Zonas': 'Zonas de Frequência Cardíaca'
                    },
                    category_orders={"Zonas": [
                        "Zona 1 - Recuperação Ativa",
                        "Zona 2 - Aeróbico Leve",
                        "Zona 3 - Aeróbico Moderado",
                        "Zona 4 - Limiar Anaeróbico",
                        "Zona 5 - Alta Intensidade / VO2 Máx"
                    ]},
                    barmode='group',
                    text=df_long['Valor'].apply(lambda x: f'{int(x)}'),
                    custom_data=['Categoria', 'Quantidade de Treinos']
                )

                # Personalizar hover
                fig2.update_traces(
                    hovertemplate="%{customdata[0]}: %{y}<br>Quantidade de treinos = %{customdata[1]}<br>Zona: %{x}",
                    textposition='auto'
                )

                # Ajustar layout com legenda à direita
                fig2.update_layout(
                    legend=dict(
                        x=1.05,
                        y=0.5,
                        xanchor='left',
                        yanchor='middle',
                        orientation='v',
                        title_text='Zonas'
                    ),
                    showlegend=True
                )

                # Exibir o gráfico de barras
                st.plotly_chart(fig2, use_container_width=True)

            # Gráfico 2: Eficiência Cardiorrespiratória e VO2 Máx por Zona
            st.markdown(
                "<h2 style='text-align: left;'>Eficiência Cardiorrespiratória e VO2 Máx por Zona</h2>",
                unsafe_allow_html=True
            )

            # Criar DataFrame a partir dos dados fornecidos
            df = pd.DataFrame(workouts)

            # Filtrar entradas inválidas
            df = df.dropna(subset=['heart_rate', 'calories'])
            df = df[df['calories'] > 0]

            if df.empty:
                st.warning("Nenhum dado disponível para exibir no gráfico de dispersão.")
                return

            # Extrair HR Médio e HR Máximo
            df['HR Médio'] = df['heart_rate'].apply(lambda x: x['average'] if isinstance(x, dict) else x)
            df['HR Máximo'] = df['heart_rate'].apply(lambda x: x['maximum'] if isinstance(x, dict) else 200)

            # Calcular zonas de intensidade
            df['Zona'] = df.apply(lambda row: self.service.get_heart_rate_zone(row['HR Médio'], row['HR Máximo']), axis=1)

            # Calcular VO2 estimado (Swain et al., 1994)
            df['VO2 Estimado'] = df['HR Médio'].apply(lambda x: 0.835 * x - 39.3)

            # Converter duração para minutos
            df['Duração (min)'] = df['duration'].apply(self.service.parse_duration)

            # Calcular calorias por minuto
            df['Calorias por Minuto'] = df['calories'] / df['Duração (min)']

            # Identificar zonas únicas presentes nos dados
            unique_zones = df['Zona'].unique()
            num_zones = len(unique_zones)

            if num_zones == 0:
                st.warning("Nenhuma zona de treino identificada.")
                return

            # Informar ao usuário quais zonas estão sendo exibidas
            st.info(f"Zonas disponíveis no dataset: {', '.join(unique_zones)}")

            # Mapa de cores para as zonas
            color_map = {
                "Zona 1 - Recuperação Ativa": '#FF4B4B',  # Vermelho
                "Zona 2 - Aeróbico Leve": '#4CAF50',      # Verde
                "Zona 3 - Aeróbico Moderado": '#FFC107',  # Amarelo
                "Zona 4 - Limiar Anaeróbico": '#1E88E5',  # Azul
                "Zona 5 - Alta Intensidade / VO2 Máx": '#AB47BC'  # Roxo
            }

            # Criar subplots: um gráfico por zona, dispostos horizontalmente
            fig = sp.make_subplots(
                rows=1, cols=num_zones,
                subplot_titles=[f"{zone}" for zone in unique_zones],
                horizontal_spacing=0.05
            )

            # Adicionar um gráfico de dispersão para cada zona
            for i, zone in enumerate(unique_zones, 1):
                zone_df = df[df['Zona'] == zone]
                if not zone_df.empty:
                    scatter = px.scatter(
                        zone_df,
                        x='HR Médio',
                        y='VO2 Estimado',
                        size='Calorias por Minuto',
                        color_discrete_sequence=[color_map[zone]],
                        labels={
                            'HR Médio': 'Frequência Cardíaca Média (bpm)',
                            'VO2 Estimado': 'VO2 Estimado (mL/kg/min)'
                        },
                        hover_data={
                            'calories': True,
                            'Duração (min)': ':.2f',
                            'Calorias por Minuto': ':.2f',
                            'HR Máximo': True
                        }
                    )

                    # Adicionar traços ao subplot correspondente
                    for trace in scatter.data:
                        fig.add_trace(trace, row=1, col=i)

                    # Personalizar o hover
                    fig.update_traces(
                        hovertemplate=(
                            "HR Médio: %{x} bpm<br>"
                            "HR Máximo: %{customdata[0]} bpm<br>"
                            "VO2 Estimado: %{y:.2f} mL/kg/min<br>"
                            "Calorias Totais: %{customdata[1]}<br>"
                            "Duração: %{customdata[2]:.2f} min<br>"
                            "Eficiência: %{customdata[3]:.2f} cal/min"
                        ),
                        customdata=zone_df[['HR Máximo', 'calories', 'Duração (min)', 'Calorias por Minuto']].values,
                        row=1, col=i
                    )

            # Ajustar layout geral dos gráficos de dispersão
            fig.update_layout(
                height=400,
                width=300 * num_zones,
                showlegend=False,
                title_text="Eficiência Cardiorrespiratória por Zona de Intensidade",
                title_x=0.5
            )

            # Ajustar eixos dos gráficos de dispersão
            for i in range(1, num_zones + 1):
                fig.update_xaxes(title_text="Frequência Cardíaca Média (bpm)", row=1, col=i)
                fig.update_yaxes(title_text="VO2 Estimado (mL/kg/min)", row=1, col=i)

            # Exibir o gráfico de dispersão
            st.plotly_chart(fig, use_container_width=True)

            # Gráfico 3: Análise de Recuperação e Fadiga
            st.markdown(
                "<h2 style='text-align: left;'>Análise de Recuperação e Fadiga</h2>",
                unsafe_allow_html=True
            )
            st.markdown("""
            A recuperação cardíaca pós-exercício é um indicador importante para avaliar fadiga e condicionamento cardiovascular. 
            Segundo estudos de Imai et al. (1994), uma rápida queda da frequência cardíaca após o exercício está associada a um bom nível de aptidão aeróbica. 
            A recuperação cardíaca pode ser calculada como **Recuperação Cardíaca = HR Máximo − HR Médio após 1 min de descanso**. 
            Quando essa métrica diminui ao longo do tempo, pode indicar fadiga acumulada ou overtraining (Meeusen et al., 2013). 
            Além disso, se a HR Média aumenta sem aumento correspondente de calorias queimadas, pode ser um sinal de ineficiência energética e necessidade de ajuste no treinamento.
            """)

            # Converter start_time para datetime
            df['Data'] = pd.to_datetime(df['start_time'])

            # Dividir a tela em duas colunas
            col1, col2 = st.columns(2)

            # Gráfico à esquerda: Evolução de HR Médio e Calorias por Minuto
            with col1:
                st.markdown("#### Evolução ao Longo do Tempo")
                fig_fadiga = px.line(
                    df,
                    x='Data',
                    y=['HR Médio', 'Calorias por Minuto'],
                    labels={
                        'Data': 'Data do Treino',
                        'value': 'Valor',
                        'variable': 'Métrica'
                    },
                    title='HR Médio e Eficiência Energética'
                )
                fig_fadiga.update_layout(
                    yaxis_title="HR (bpm) / Calorias por Minuto (cal/min)",
                    font=dict(color=st.get_option("theme.textColor") or "black")
                )
                st.plotly_chart(fig_fadiga, use_container_width=True)

            # Gráfico à direita: Análise de Recuperação Cardíaca
            with col2:
                st.markdown("#### Análise de Recuperação Cardíaca")
                st.markdown("Selecione a data do treino e insira o valor de HR Após 1 Minuto para calcular a Recuperação Cardíaca.")

                # Criar coluna para HR Após 1 Minuto e Recuperação Cardíaca, se não existirem
                if 'HR Após 1 Min' not in df.columns:
                    df['HR Após 1 Min'] = pd.NA
                if 'Recuperação Cardíaca' not in df.columns:
                    df['Recuperação Cardíaca'] = pd.NA

                # Dividir em duas colunas para o dropdown e o campo de entrada
                col_data, col_hr = st.columns(2)

                # Dropdown para selecionar a data do treino (padrão: treino mais recente)
                with col_data:
                    datas_treino = df['Data'].dt.strftime('%Y-%m-%d %H:%M').tolist()
                    data_mais_recente = max(datas_treino)
                    data_selecionada = st.selectbox(
                        "Data do Treino",
                        datas_treino,
                        index=datas_treino.index(data_mais_recente)
                    )

                # Filtrar o treino selecionado
                treino_selecionado = df[df['Data'].dt.strftime('%Y-%m-%d %H:%M') == data_selecionada].iloc[0]
                hr_max = treino_selecionado['HR Máximo']

                # Campo de entrada para HR Após 1 Minuto
                with col_hr:
                    hr_apos_1min = st.number_input(
                        f"HR Após 1 Min (HR Máx: {hr_max} bpm)",
                        min_value=0.0,
                        max_value=float(hr_max),
                        value=0.0,
                        step=1.0,
                        key=f"HR Após 1 Min - {data_selecionada}"
                    )

                # Botão para calcular
                calcular = st.button("Calcular")

                # Gráfico de barras para Recuperação Cardíaca
                if calcular and hr_apos_1min > 0:
                    # Atualizar o DataFrame com o valor inserido
                    index_selecionado = df.index[df['Data'].dt.strftime('%Y-%m-%d %H:%M') == data_selecionada][0]
                    df.at[index_selecionado, 'HR Após 1 Min'] = hr_apos_1min
                    df.at[index_selecionado, 'Recuperação Cardíaca'] = hr_max - hr_apos_1min

                    # Filtrar apenas o treino selecionado e preparar os dados em formato long
                    df_recuperacao = df[df['Data'].dt.strftime('%Y-%m-%d %H:%M') == data_selecionada][['HR Médio', 'HR Máximo', 'HR Após 1 Min', 'Recuperação Cardíaca']]
                    df_recuperacao_long = pd.melt(
                        df_recuperacao,
                        value_vars=['HR Médio', 'HR Máximo', 'HR Após 1 Min', 'Recuperação Cardíaca'],
                        var_name='Métrica',
                        value_name='Valor (bpm)'
                    )

                    # Criar gráfico de barras
                    fig_recuperacao = px.bar(
                        df_recuperacao_long,
                        x='Métrica',
                        y='Valor (bpm)',
                        labels={'Métrica': 'Métrica', 'Valor (bpm)': 'Valor (bpm)'},
                        title=f'Recuperação Cardíaca - {data_selecionada}',
                        text_auto=True
                    )
                    fig_recuperacao.update_traces(textposition='auto')
                    fig_recuperacao.update_layout(
                        yaxis_title="Frequência Cardíaca (bpm)",
                        font=dict(color=st.get_option("theme.textColor") or "black")
                    )
                    st.plotly_chart(fig_recuperacao, use_container_width=True)
                else:
                    st.info("Insira um valor válido para HR Após 1 Min e clique em 'Calcular' para ver o gráfico.")


            # Container para o Diário de Treino
            with st.container():
                st.markdown("<h2 style='text-align: left;'>Diário de Treino</h2>", unsafe_allow_html=True)

                # Carregar dados biológicos
                loader = LoadFile()
                set_data = loader.load_set_data()

                # Dicionário de meses em português
                meses_pt = {
                    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio",
                    6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro",
                    11: "Novembro", 12: "Dezembro"
                }

                # Seleção de mês e ano
                col_mes, col_ano = st.columns(2)
                with col_mes:
                    mes_nome = st.selectbox("Mês", list(meses_pt.values()), index=9)  # Padrão: Outubro
                    mes = [k for k, v in meses_pt.items() if v == mes_nome][
                        0]  # Converte o nome do mês de volta para número
                with col_ano:
                    anos_disponiveis = sorted(set(pd.to_datetime(list(set_data["schedule"].keys())).year))
                    ano = st.selectbox("Ano", anos_disponiveis,
                                       index=anos_disponiveis.index(2024) if 2024 in anos_disponiveis else 0)

                # Filtrar treinos do mês e ano selecionados
                data_inicio = datetime(ano, mes, 1)
                data_fim = datetime(ano, mes + 1, 1) if mes < 12 else datetime(ano + 1, 1, 1)
                treinos_mes = {date: info for date, info in set_data["schedule"].items()
                               if data_inicio <= datetime.strptime(date, '%Y-%m-%d') < data_fim}

                if not treinos_mes:
                    st.warning(f"Nenhum treino encontrado para {meses_pt[mes]}/{ano}.")
                else:
                    for date, treino in sorted(treinos_mes.items()):
                        with st.expander(f"Treino do dia {date}"):
                            try:
                                df_treino = pd.DataFrame(treino["exercises"])
                                df_treino["type"] = treino["type"]

                                # Garantir que as colunas esperadas existam, preenchendo com "Não informado" se ausentes
                                for col in ["category", "details", "sets"]:
                                    if col not in df_treino.columns:
                                        df_treino[col] = "Não informado"
                                df_treino["sets"] = df_treino["sets"].apply(
                                    lambda x: ", ".join(x) if isinstance(x, list) else str(x))

                                # Selecionar apenas as colunas disponíveis e renomear
                                colunas_disponiveis = [col for col in ["type", "category", "details", "sets"] if
                                                       col in df_treino.columns]
                                st.table(df_treino[colunas_disponiveis].rename(
                                    columns={"type": "Tipo", "category": "Categoria", "details": "Detalhes",
                                             "sets": "Exercícios"}
                                ))
                            except Exception as e:
                                st.error(f"Erro ao processar o treino do dia {date}: {str(e)}")

        if workouts:
            with st.container():
                st.markdown("<h2 style='text-align: left;'>Relação Tempo x Calorias Queimadas</h2>",
                            unsafe_allow_html=True)
                st.markdown("""
                            A relação entre tempo de treino e calorias queimadas é crucial para determinar a eficiência do exercício. 
                            Treinos curtos e intensos podem apresentar maior eficiência, enquanto treinos longos podem mostrar diminuição de retorno.
                            """)

                # Criar DataFrame com os dados fornecidos
                df_calorias = pd.DataFrame(workouts)
                df_calorias["Duração (min)"] = df_calorias["duration"].apply(self.service.parse_duration)
                df_calorias["Calorias Queimadas"] = df_calorias["calories"]
                df_calorias["Eficiência (cal/min)"] = df_calorias["Calorias Queimadas"] / df_calorias["Duração (min)"]
                df_calorias["Tipo"] = df_calorias["sport"]
                # Extrair HR média e máxima do dicionário heart_rate
                df_calorias["HR Médio"] = df_calorias["heart_rate"].apply(
                    lambda x: x["average"] if isinstance(x, dict) else "N/A")
                df_calorias["HR Máximo"] = df_calorias["heart_rate"].apply(
                    lambda x: x["maximum"] if isinstance(x, dict) else "N/A")

                # Gráfico de Dispersão
                fig_calorias = px.scatter(
                    df_calorias,
                    x="Duração (min)",
                    y="Calorias Queimadas",
                    size="Eficiência (cal/min)",
                    color="Tipo",
                    hover_data=["start_time", "HR Médio", "HR Máximo"],  # Exibir valores específicos
                    trendline="ols",
                    title="Relação Tempo x Calorias Queimadas",
                    labels={"Duração (min)": "Duração do Treino (min)",
                            "Calorias Queimadas": "Calorias Queimadas (kcal)"}
                )
                st.plotly_chart(fig_calorias, use_container_width=True)


























