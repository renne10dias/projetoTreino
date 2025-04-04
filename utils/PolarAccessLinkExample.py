#!/usr/bin/env python

from __future__ import print_function
from utils.utils import load_config, save_config, pretty_print_json, save_as_json, save_as_json_data_transacional
from accesslink import AccessLink
import os

CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), 'config.yml')

#CONFIG_FILENAME = "config.yml"

class PolarAccessLinkExample(object):
    """Aplicação exemplo para Polar Open AccessLink v3."""

    def __init__(self):
        # Carrega a configuração do arquivo config.yml
        self.config = load_config(CONFIG_FILENAME)

        # Verifica se o token de acesso está presente na configuração
        if "access_token" not in self.config:
            print("Autorização necessária. Execute authorization.py primeiro e complete o processo de autenticação.")
            return

        # Inicializa o cliente AccessLink com as credenciais fornecidas
        self.accesslink = AccessLink(client_id=self.config["client_id"],
                                     client_secret=self.config["client_secret"])

        self.running = True
        self.show_menu()

    def show_menu(self):
        # Exibe o menu principal
        while self.running:
            print("\nEscolha uma opção:\n" +
                  "-----------------------\n" +
                  "1) Obter informações do usuário\n" +
                  #"2) Obter dados transacionais disponíveis\n" +
                  "3) Obter dados não transacionais disponíveis\n" +
                  #"4) Revogar token de acesso\n" +
                  "5) Sair\n" +
                  "-----------------------")
            self.get_menu_choice()

    def get_menu_choice(self):
        # Processa a escolha do menu
        choice = input("> ")
        {
            "1": self.get_user_information,
            "2": self.check_available_data,
            "3": self.print_data,
            "4": self.revoke_access_token,
            "5": self.exit
        }.get(choice, self.get_menu_choice)()

    def print_data(self):
        # Obtém e exibe dados disponíveis
        exercise = self.accesslink.get_exercises(access_token=self.config["access_token"])
        sleep =  self.accesslink.get_sleep(access_token=self.config["access_token"])
        recharge = self.accesslink.get_recharge(access_token=self.config["access_token"])
        #cardio = self.accesslink.get_cardio(access_token=self.config["access_token"])
        heart_rate = self.accesslink.get_heart_rate(access_token=self.config["access_token"])

        print("Exercícios: ", end='')

        # Verifica se o JSON de exercícios está vazio
        if not exercise:
            print("O JSON de exercícios está vazio.")
        else:
            print("O JSON de exercícios contém dados:", exercise)
            pretty_print_json(exercise)
            save_as_json(exercise, 'Data/bioData.json')

    def get_user_information(self):
        # Obtém informações do usuário
        user_info = self.accesslink.users.get_information(user_id=self.config["user_id"],
                                                          access_token=self.config["access_token"])
        pretty_print_json(user_info)

    def check_available_data(self):
        # Verifica dados disponíveis para sincronização
        available_data = self.accesslink.pull_notifications.list()

        if not available_data:
            print("Nenhum dado novo disponível.")
            return

        print("Dados disponíveis:")
        pretty_print_json(available_data)
        for item in available_data["available-user-data"]:
            if item["data-type"] == "EXERCISE":
                self.get_exercises()
            elif item["data-type"] == "ACTIVITY_SUMMARY":
                self.get_daily_activity()
            elif item["data-type"] == "PHYSICAL_INFORMATION":
                self.get_physical_info()

    def revoke_access_token(self):
        # Revoga o token de acesso
        self.accesslink.users.delete(user_id=self.config["user_id"],
                                     access_token=self.config["access_token"])

        # Remove o token e o ID do usuário da configuração
        del self.config["access_token"]
        del self.config["user_id"]
        save_config(self.config, CONFIG_FILENAME)

        print("Token de acesso revogado com sucesso.")
        self.exit()

    def exit(self):
        # Finaliza o programa
        self.running = False

    def get_exercises(self):
        # Obtém dados de exercícios
        transaction = self.accesslink.training_data.create_transaction(user_id=self.config["user_id"],
                                                                       access_token=self.config["access_token"])
        if not transaction:
            print("Nenhum exercício novo disponível.")
            return

        resource_urls = transaction.list_exercises()["exercises"]

        for url in resource_urls:
            exercise_summary = transaction.get_exercise_summary(url)

            print("Resumo do exercício:")
            pretty_print_json(exercise_summary)
            save_as_json_data_transacional(exercise_summary, 'Data/exercise_summary.json')

        transaction.commit()

    def get_daily_activity(self):
        # Obtém dados de atividade diária
        transaction = self.accesslink.daily_activity.create_transaction(user_id=self.config["user_id"],
                                                                        access_token=self.config["access_token"])
        if not transaction:
            print("Nenhuma atividade diária nova disponível.")
            return

        resource_urls = transaction.list_activities()["activity-log"]

        for url in resource_urls:
            activity_summary = transaction.get_activity_summary(url)

            print("Resumo da atividade:")
            pretty_print_json(activity_summary)
            save_as_json_data_transacional(activity_summary, 'Data/activity_summary.json')

        transaction.commit()

    def get_physical_info(self):
        # Obtém informações físicas
        transaction = self.accesslink.physical_info.create_transaction(user_id=self.config["user_id"],
                                                                       access_token=self.config["access_token"])
        if not transaction:
            print("Nenhuma informação física nova disponível.")
            return

        resource_urls = transaction.list_physical_infos()["physical-informations"]

        for url in resource_urls:
            physical_info = transaction.get_physical_info(url)

            print("Informação física:")
            pretty_print_json(physical_info)
            save_as_json_data_transacional(physical_info, 'Data/physical_info.json')
        transaction.commit()


if __name__ == "__main__":
    PolarAccessLinkExample()
