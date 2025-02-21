import json
import os

import pandas as pd


class UserService:

    # Função para exibir informações do usuário no Streamlit
    def exibir_informacoes_usuario(self):
        # Instanciar a classe adaptadora
        instancia = PolarAccessLinkAdapter()

        # Obter informações do usuário
        user_info = instancia.get_user_information()

        return user_info
