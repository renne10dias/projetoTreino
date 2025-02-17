from views.DashboardView import DashboardView


def main():
    # Crie a classe de visualização
    dashboard_view = DashboardView()

    # Exibe o dashboard
    dashboard_view.create_intensity_chart()

if __name__ == "__main__":
    main()
