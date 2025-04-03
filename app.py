import sys

from teste.Zona2 import Zona2
from utils.LoadFile import LoadFile
from views.DashboardView import DashboardView
from streamlit.web import cli as stcli
from streamlit import runtime


def main():
    # Crie a classe de visualização
    #dashboard_view = DashboardView()

    # Exibe o dashboard
    #dashboard_view.create_intensity_chart()

    # Carregar dados biológicos
    loader = LoadFile()
    workouts = loader.load_bio_data()
    set_data = loader.load_set_data()

    dashboard_view = Zona2(workouts)
    dashboard_view.create_cardiorespiratory_efficiency_charts()


if __name__ == '__main__':
    if runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
