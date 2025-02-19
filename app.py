import sys

from views.DashboardView import DashboardView
from streamlit.web import cli as stcli
from streamlit import runtime


def main():
    # Crie a classe de visualização
    dashboard_view = DashboardView()

    # Exibe o dashboard
    dashboard_view.create_intensity_chart()


if __name__ == '__main__':
    if runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
