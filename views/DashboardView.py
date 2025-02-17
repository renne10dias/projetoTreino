import plotly.express as px
import streamlit as st

from services.DashboardService.DashboardService import DashboardService


class DashboardView:

    def __init__(self):
        self.service = DashboardService()

    def create_intensity_chart(self):
        st.set_page_config(layout="wide")

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
