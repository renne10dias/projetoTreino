import os
import sys
import streamlit as st # type: ignore

from utils.PolarAccessLinkExample import PolarAccessLinkExample

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class PolarAccessLinkAdapter(PolarAccessLinkExample):
    def __init__(self):
        # Chamando o construtor original, mas não inicializando o menu
        self.config = self._load_config()
        self.accesslink = self._initialize_accesslink()
        self.running = False  # Para evitar o loop do menu

    def _load_config(self):
        # Carrega a configuração do arquivo
        from utils import load_config  # Importa o método utilitário
        import os
        CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), 'config.yml')
        return load_config(CONFIG_FILENAME)

    def _initialize_accesslink(self):
        # Inicializa o cliente AccessLink
        from accesslink import AccessLink  # Importa a biblioteca AccessLink
        return AccessLink(
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"]
        )
    
    def get_user_information(self):
        # Obtém informações do usuário
        user_info = self.accesslink.users.get_information(
            user_id=self.config["user_id"],
            access_token=self.config["access_token"]
        )
        return user_info  # Retorna as informações em vez de apenas imprimir