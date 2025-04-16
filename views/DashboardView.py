import os
import re

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

        st.sidebar.header("Olá, " + primeiro_nome + " " + ultimo_nome)
        st.sidebar.write(f"Peso: {peso} kg")
        st.sidebar.write(f"Altura: {altura} cm")

        treino_data = self.dashboardUtils.load_treino_data()

        img_heart_solid = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images/heart-solid.svg")
        img_heart_solid_pulse = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             "../images/heart-pulse-solid.svg")
        img_fire_solid = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images/fire-solid.svg")

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

        # Obter os dados filtrados e os valores de mês e ano selecionados
        df_filtrado, color_map, selected_month_Intensity, selected_year_Intensity = self.service.col1_intensidade_treino()

        # Mapear nomes dos meses para números
        meses_pt_to_num = {
            "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5,
            "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10,
            "Novembro": 11, "Dezembro": 12
        }
        mes = meses_pt_to_num[selected_month_Intensity]
        ano = selected_year_Intensity
        data_inicio = datetime(ano, mes, 1)
        data_fim = datetime(ano, mes + 1, 1) if mes < 12 else datetime(ano + 1, 1, 1)

        # Carregar os dados de bio_data
        workouts = self.loadFile.load_bio_data()
        if not workouts:
            st.error("Nenhum dado de treino disponível.")
            return

        # Criar um DataFrame e filtrar pelo mês e ano selecionados
        df_workouts = pd.DataFrame(workouts)
        df_workouts['Data'] = pd.to_datetime(df_workouts['start_time'])
        df_workouts_filtrado = df_workouts[
            (df_workouts['Data'] >= data_inicio) & (df_workouts['Data'] < data_fim)].copy()

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    "<h2 style='text-align: left;'>Classificação do Treino por Zonas de Intensidade Cardíaca</h2>",
                    unsafe_allow_html=True
                )

                # Essa seção já usa a função ajustada mostrar_dados_de_treino_por_zona
                zones, calories, counts = self.service.mostrar_dados_de_treino_por_zona(mes, ano)

                # Criar o DataFrame apenas com Zonas e Número de Treinos
                df = pd.DataFrame({
                    'Zonas': zones,
                    'Número de Treinos': counts
                })

                # Filtrar para exibir apenas zonas com treinos
                df_filtrado = df[df['Número de Treinos'] > 0]

                if df_filtrado.empty:
                    st.warning("Nenhum dado disponível para exibir no gráfico de barras.")
                else:
                    color_map = {
                        "Zona 1 - Recuperação Ativa": '#FF4B4B',
                        "Zona 2 - Aeróbico Leve": '#4CAF50',
                        "Zona 3 - Aeróbico Moderado": '#FFC107',
                        "Zona 4 - Limiar Anaeróbico": '#1E88E5',
                        "Zona 5 - Alta Intensidade / VO2 Máx": '#AB47BC'
                    }

                    fig2 = px.bar(
                        df_filtrado,
                        x='Zonas',
                        y='Número de Treinos',
                        color='Zonas',
                        color_discrete_map=color_map,
                        labels={
                            'Número de Treinos': 'Número de Treinos',
                            'Zonas': 'Zonas de Frequência Cardíaca'
                        },
                        category_orders={"Zonas": [
                            "Zona 1 - Recuperação Ativa",
                            "Zona 2 - Aeróbico Leve",
                            "Zona 3 - Aeróbico Moderado",
                            "Zona 4 - Limiar Anaeróbico",
                            "Zona 5 - Alta Intensidade / VO2 Máx"
                        ]},
                        text=df_filtrado['Número de Treinos'].apply(lambda x: f'{int(x)}')
                    )

                    fig2.update_traces(
                        hovertemplate="Zona: %{x}<br>Número de treinos: %{y}",
                        textposition='auto'
                    )

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

                    st.plotly_chart(fig2, use_container_width=True)

            with col2:
                st.markdown("<h2 style='text-align: left;'>Relação Tempo x Calorias Queimadas</h2>",
                            unsafe_allow_html=True)
                st.markdown("""
                            A relação entre tempo de treino e calorias queimadas é crucial para determinar a eficiência do exercício. 
                            Treinos curtos e intensos podem apresentar maior eficiência, enquanto treinos longos podem mostrar diminuição de retorno.
                            """)

                # Usar o DataFrame filtrado
                df_calorias = df_workouts_filtrado.copy()
                df_calorias["Duração (min)"] = df_calorias["duration"].apply(self.service.parse_duration)
                df_calorias["Calorias Queimadas"] = df_calorias["calories"]
                df_calorias["Eficiência (cal/min)"] = df_calorias["Calorias Queimadas"] / df_calorias["Duração (min)"]
                df_calorias["HR Médio"] = df_calorias["heart_rate"].apply(
                    lambda x: x["average"] if isinstance(x, dict) else "N/A")
                df_calorias["HR Máximo"] = df_calorias["heart_rate"].apply(
                    lambda x: x["maximum"] if isinstance(x, dict) else "N/A")

                # Calcular a zona de intensidade cardíaca
                df_calorias['Zona'] = df_calorias.apply(
                    lambda row: self.service.get_heart_rate_zone(row['HR Médio'], row['HR Máximo']),
                    axis=1
                )

                # Remover linhas com valores inválidos de HR
                df_calorias = df_calorias[df_calorias['HR Médio'] != "N/A"]
                df_calorias = df_calorias[df_calorias['HR Máximo'] != "N/A"]

                if df_calorias.empty:
                    st.warning("Nenhum dado válido disponível para exibir o gráfico.")
                else:
                    color_map = {
                        "Zona 1 - Recuperação Ativa": '#FF4B4B',
                        "Zona 2 - Aeróbico Leve": '#4CAF50',
                        "Zona 3 - Aeróbico Moderado": '#FFC107',
                        "Zona 4 - Limiar Anaeróbico": '#1E88E5',
                        "Zona 5 - Alta Intensidade / VO2 Máx": '#AB47BC'
                    }

                    fig_calorias = px.scatter(
                        df_calorias,
                        x="Duração (min)",
                        y="Calorias Queimadas",
                        size="Eficiência (cal/min)",
                        color="Zona",
                        color_discrete_map=color_map,
                        hover_data=["start_time", "HR Médio", "HR Máximo"],
                        trendline="ols",
                        title=f"Relação Tempo x Calorias Queimadas - {selected_month_Intensity}/{ano}",
                        labels={"Duração (min)": "Duração do Treino (min)",
                                "Calorias Queimadas": "Calorias Queimadas (kcal)"}
                    )
                    st.plotly_chart(fig_calorias, use_container_width=True)

        with st.container():
            st.markdown(
                "<h2 style='text-align: left;'>Eficiência Cardiorrespiratória e VO2 Máx por Zona</h2>",
                unsafe_allow_html=True
            )

            # Usar o DataFrame filtrado
            df = df_workouts_filtrado.copy()

            df = df.dropna(subset=['heart_rate', 'calories'])
            df = df[df['calories'] > 0]

            if df.empty:
                st.warning("Nenhum dado disponível para exibir no gráfico de dispersão.")
            else:
                df['HR Médio'] = df['heart_rate'].apply(lambda x: x['average'] if isinstance(x, dict) else x)
                df['HR Máximo'] = df['heart_rate'].apply(lambda x: x['maximum'] if isinstance(x, dict) else 200)

                df['Zona'] = df.apply(lambda row: self.service.get_heart_rate_zone(row['HR Médio'], row['HR Máximo']),
                                      axis=1)

                df['VO2 Estimado'] = df['HR Médio'].apply(lambda x: 0.835 * x - 39.3)

                df['Duração (min)'] = df['duration'].apply(self.service.parse_duration)

                df['Calorias por Minuto'] = df['calories'] / df['Duração (min)']

                unique_zones = df['Zona'].unique()
                num_zones = len(unique_zones)

                if num_zones == 0:
                    st.warning("Nenhuma zona de treino identificada.")
                else:
                    st.info(f"Zonas disponíveis no dataset: {', '.join(unique_zones)}")

                    color_map = {
                        "Zona 1 - Recuperação Ativa": '#FF4B4B',
                        "Zona 2 - Aeróbico Leve": '#4CAF50',
                        "Zona 3 - Aeróbico Moderado": '#FFC107',
                        "Zona 4 - Limiar Anaeróbico": '#1E88E5',
                        "Zona 5 - Alta Intensidade / VO2 Máx": '#AB47BC'
                    }

                    fig = px.scatter(
                        df,
                        x='HR Médio',
                        y='VO2 Estimado',
                        size='Calorias por Minuto',
                        color='Zona',
                        color_discrete_map=color_map,
                        labels={
                            'HR Médio': 'Frequência Cardíaca Média (bpm)',
                            'VO2 Estimado': 'VO2 Estimado (mL/kg/min)',
                            'Zona': 'Zona de Intensidade'
                        },
                        hover_data={
                            'calories': True,
                            'Duração (min)': ':.2f',
                            'Calorias por Minuto': ':.2f',
                            'HR Máximo': True
                        }
                    )

                    fig.update_traces(
                        hovertemplate=(
                            "HR Médio: %{x} bpm<br>"
                            "HR Máximo: %{customdata[0]} bpm<br>"
                            "VO2 Estimado: %{y:.2f} mL/kg/min<br>"
                            "Calorias Totais: %{customdata[1]}<br>"
                            "Duração: %{customdata[2]:.2f} min<br>"
                            "Eficiência: %{customdata[3]:.2f} cal/min<br>"
                            "Zona: %{fullData.name}"
                        ),
                        customdata=df[['HR Máximo', 'calories', 'Duração (min)', 'Calorias por Minuto']].values
                    )

                    fig.update_layout(
                        height=400,
                        width=800,
                        title_text=f"Eficiência Cardiorrespiratória por Zona de Intensidade - {selected_month_Intensity}/{ano}",
                        title_x=0.5,
                        xaxis_title="Frequência Cardíaca Média (bpm)",
                        yaxis_title="VO2 Estimado (mL/kg/min)",
                        showlegend=True,
                        legend=dict(
                            x=1.05,
                            y=0.5,
                            xanchor='left',
                            yanchor='middle',
                            orientation='v',
                            title_text='Zonas'
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)

        with st.container():
            st.markdown(
                "<h2 style='text-align: left;'>Análise de Recuperação e Fadiga</h2>",
                unsafe_allow_html=True
            )
            st.markdown("""
            A recuperação cardíaca pós-exercício é um indicador importante para avaliar fadiga e condicionamento cardiovascular. 
            Segundo estudos de Imai et al. (1994), uma rápida queda da frequência cardíaca após o exercício está associada a um bom nível de aptidão aeróbica. 
            Quando a recuperação cardíaca diminui ao longo do tempo, pode indicar fadiga acumulada ou overtraining (Meeusen et al., 2013). 
            Além disso, se a HR Média aumenta sem aumento correspondente de calorias queimadas, pode ser um sinal de ineficiência energética e necessidade de ajuste no treinamento.
            """)

            # Usar o DataFrame filtrado
            df = df_workouts_filtrado.copy()

            if df.empty:
                st.warning(f"Nenhum dado disponível para {selected_month_Intensity}/{ano}.")
            else:
                # Criar as colunas 'HR Médio' e 'HR Máximo'
                df['HR Médio'] = df['heart_rate'].apply(lambda x: x['average'] if isinstance(x, dict) else None)
                df['HR Máximo'] = df['heart_rate'].apply(lambda x: x['maximum'] if isinstance(x, dict) else 200)

                # Criar a coluna 'Duração (min)' e 'Calorias por Minuto'
                df['Duração (min)'] = df['duration'].apply(self.service.parse_duration)
                df['Calorias por Minuto'] = df['calories'] / df['Duração (min)']

                # Remover linhas com valores nulos ou inválidos
                df = df.dropna(subset=['HR Médio', 'HR Máximo', 'Duração (min)', 'Calorias por Minuto'])
                df = df[df['Duração (min)'] > 0]  # Evitar divisão por zero

                if df.empty:
                    st.warning(
                        f"Nenhum dado válido de frequência cardíaca ou calorias disponível para {selected_month_Intensity}/{ano}.")
                else:
                    # Calcular a recuperação cardíaca (HR Máximo - HR Médio)
                    df['Recuperação Cardíaca'] = df['HR Máximo'] - df['HR Médio']

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### Recuperação Cardíaca ao Longo do Mês")
                        fig_recuperacao = px.line(
                            df,
                            x='Data',
                            y='Recuperação Cardíaca',
                            labels={
                                'Data': 'Data do Treino',
                                'Recuperação Cardíaca': 'Recuperação Cardíaca (bpm)'
                            },
                            title=f'Recuperação Cardíaca - {selected_month_Intensity}/{ano}'
                        )
                        fig_recuperacao.update_layout(
                            xaxis_title="Data",
                            yaxis_title="Recuperação Cardíaca (bpm)",
                            font=dict(color="black"),
                            xaxis=dict(tickangle=45)
                        )
                        st.plotly_chart(fig_recuperacao, use_container_width=True)

                    with col2:
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
                            title=f'HR Médio e Eficiência Energética - {selected_month_Intensity}/{ano}'
                        )
                        fig_fadiga.update_layout(
                            yaxis_title="HR (bpm) / Calorias por Minuto (cal/min)",
                            font=dict(color="black"),
                            xaxis=dict(tickangle=45)
                        )
                        st.plotly_chart(fig_fadiga, use_container_width=True)



        with st.container():
            st.markdown("<h2 style='text-align: left;'>Diário de Treino</h2>", unsafe_allow_html=True)

            # Carregar os dados
            loader = LoadFile()
            set_data = loader.load_set_data()

            # Filtrar treinos pelo mês e ano selecionados
            treinos_mes = {date: info for date, info in set_data["schedule"].items()
                           if data_inicio <= datetime.strptime(date, '%Y-%m-%d') < data_fim}

            if not treinos_mes:
                st.warning(f"Nenhum treino encontrado para {selected_month_Intensity}/{ano}.")
            else:
                # Importar o componente de calendário
                from streamlit_calendar import calendar

                # Configurar opções do calendário
                calendar_options = {
                    "editable": False,
                    "selectable": True,
                    "headerToolbar": {
                        "left": "prev,next today",
                        "center": "title",
                        "right": "dayGridMonth"
                    },
                    "initialView": "dayGridMonth",
                    "initialDate": f"{ano}-{mes:02d}-01"
                }

                # Criar eventos para o calendário
                calendar_events = []
                for date, treino in sorted(treinos_mes.items()):
                    foi_treinar = bool(treino.get("exercises", []))
                    evento = {
                        "title": "Treino Realizado" if foi_treinar else "Treino Não Realizado",
                        "start": date,
                        "end": date,
                        "color": "#00FF00" if foi_treinar else "#FF0000",
                        "allDay": True
                    }
                    calendar_events.append(evento)

                # Personalizar o estilo do calendário
                custom_css = """
                .fc {
                    width: 100% !important;
                    max-height: 600px;
                    max-width: 1100px;  /* Ajustar o tamanho do calendário */
                }
                .fc-event-title {
                    font-weight: 700;
                }
                .fc-toolbar-title {
                    font-size: 1.5rem;
                }
                .fc-daygrid-day {
                    font-size: 0.8rem;
                }
                """

                # Criar colunas para o calendário e os detalhes do treino
                col1, col2 = st.columns(2)

                with col1:
                    # Exibir o calendário
                    calendario = calendar(
                        events=calendar_events,
                        options=calendar_options,
                        custom_css=custom_css,
                        key=f"calendario_{mes}_{ano}"
                    )

                with col2:
                    st.markdown("### Detalhes do Treino")

                    # Determinar o treino a ser exibido (mais recente por padrão)
                    if "selected_date" not in st.session_state:
                        # Encontrar a data mais recente
                        latest_date = max(treinos_mes.keys(), key=lambda d: datetime.strptime(d, '%Y-%m-%d'))
                        st.session_state.selected_date = latest_date

                    # Capturar clique no evento (eventClick)
                    if calendario.get("eventClick"):
                        event_data = calendario["eventClick"]["event"]
                        data_clicada = event_data.get("start", None)
                        if data_clicada:
                            data_clicada = data_clicada.split("T")[0] if "T" in data_clicada else data_clicada
                            if data_clicada in treinos_mes:
                                st.session_state.selected_date = data_clicada

                    # Exibir os detalhes do treino selecionado
                    data_selecionada = st.session_state.selected_date
                    if data_selecionada in treinos_mes:
                        treino = treinos_mes[data_selecionada]
                        try:
                            df_treino = pd.DataFrame(treino["exercises"])
                            df_treino["type"] = treino["type"]
                            for col in ["category", "details", "sets"]:
                                if col not in df_treino.columns:
                                    df_treino[col] = "Não informado"
                            df_treino["sets"] = df_treino["sets"].apply(
                                lambda x: ", ".join(x) if isinstance(x, list) else str(x))
                            colunas_disponiveis = [col for col in ["type", "category", "details", "sets"] if
                                                   col in df_treino.columns]
                            st.markdown(f"**Data Selecionada:** {data_selecionada}")
                            st.table(df_treino[colunas_disponiveis].rename(
                                columns={"type": "Tipo", "category": "Categoria", "details": "Detalhes",
                                         "sets": "Exercícios"}
                            ))
                        except Exception as e:
                            st.error(f"Erro ao processar o treino do dia {data_selecionada}: {str(e)}")
                    else:
                        st.info(f"Nenhum treino registrado para o dia {data_selecionada}.")