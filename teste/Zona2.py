import plotly.express as px
import plotly.subplots as sp
import streamlit as st
import pandas as pd
import re

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
            A recuperação cardíaca pós-exercício é um indicador de fadiga e condicionamento cardiovascular. 
            Uma rápida queda da frequência cardíaca após o exercício está associada a boa aptidão aeróbica (Imai et al., 1994). 
            Quando a HR Média aumenta sem aumento correspondente nas calorias queimadas, pode indicar ineficiência energética ou fadiga acumulada (Meeusen et al., 2013).
            """)

            # Converter start_time para datetime
            df['Data'] = pd.to_datetime(df['start_time'])

            # Criar gráfico de linhas para HR Médio e Calorias por Minuto
            fig_fadiga = px.line(
                df,
                x='Data',
                y=['HR Médio', 'Calorias por Minuto'],
                labels={
                    'Data': 'Data do Treino',
                    'value': 'Valor',
                    'variable': 'Métrica'
                },
                title='Evolução de HR Média e Eficiência Energética ao Longo do Tempo'
            )

            # Ajustar layout do gráfico de linhas
            fig_fadiga.update_layout(
                yaxis_title="HR Médio (bpm) / Calorias por Minuto (cal/min)",
                font=dict(color=st.get_option("theme.textColor") or "black")
            )

            # Exibir o gráfico de linhas
            st.plotly_chart(fig_fadiga, use_container_width=True)

