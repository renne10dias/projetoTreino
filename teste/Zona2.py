import plotly.express as px
import plotly.subplots as sp
import streamlit as st
import pandas as pd
import re
from datetime import datetime

from utils.LoadFile import LoadFile


class Zona2:
    def __init__(self, workouts):
        self.workouts = workouts

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

    def mostrar_dados_de_treino_por_zona(self, workouts=None):
        """Prepara os dados de treino por zona de frequência cardíaca."""
        if workouts is None:
            workouts = self.workouts

        # Inicializar dicionário com todas as zonas possíveis usando os nomes completos
        zone_data = {
            "Zona 1 - Recuperação Ativa": {"calories": 0, "count": 0},
            "Zona 2 - Aeróbico Leve": {"calories": 0, "count": 0},
            "Zona 3 - Aeróbico Moderado": {"calories": 0, "count": 0},
            "Zona 4 - Limiar Anaeróbico": {"calories": 0, "count": 0},
            "Zona 5 - Alta Intensidade / VO2 Máx": {"calories": 0, "count": 0}
        }

        # Processar cada treino e acumular calorias e contagem por zona
        for workout in workouts:
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

    def create_cardiorespiratory_efficiency_charts(self):
        st.set_page_config(page_title='Dashboard - Treino', layout='wide')
        with st.container():
            # Gráfico 1: Calorias Totais e Número de Treinos por Zona
            st.markdown(
                "<h2 style='text-align: left;'>Calorias Totais e Número de Treinos por Zona de Frequência Cardíaca</h2>",
                unsafe_allow_html=True
            )

            # Obter dados de treino por zona
            zones, calories, counts = self.mostrar_dados_de_treino_por_zona(self.workouts)

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
            df = pd.DataFrame(self.workouts)

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
            df['Zona'] = df.apply(lambda row: self.get_heart_rate_zone(row['HR Médio'], row['HR Máximo']), axis=1)

            # Calcular VO2 estimado (Swain et al., 1994)
            df['VO2 Estimado'] = df['HR Médio'].apply(lambda x: 0.835 * x - 39.3)

            # Converter duração para minutos
            df['Duração (min)'] = df['duration'].apply(self.parse_duration)

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

                # Seleção de mês e ano
                col_mes, col_ano = st.columns(2)
                with col_mes:
                    mes = st.selectbox("Mês", list(range(1, 13)), index=9)  # Padrão: Outubro (10)
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
                    st.warning(f"Nenhum treino encontrado para {mes}/{ano}.")
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




