#!/usr/bin/env python

import json
import yaml
import os


class Utils_web:

    def __init__(self, filename):
        self.filename = filename

    def load_config(self):
        """Load configuration from a yaml file"""
        with open(self.filename, 'r') as f:
            # Ler o conteúdo e adicionar espaço após os dois pontos manualmente, caso esteja faltando
            content = f.read().replace(":", ": ")
            print("Conteúdo bruto do arquivo corrigido:\n", content)  # Mostra o conteúdo com os espaços adicionados
            config = yaml.safe_load(content)
            print("Tipo de config:", type(config))  # Verificar o tipo carregado
            print("Config carregado:", config)  # Exibe o conteúdo
            return config

    def save_config(self, config):
        """Save configuration to a yaml file"""
        with open(self.filename, "w+") as f:
            yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)

    def pretty_print_json(self, data):
        print(json.dumps(data, indent=4, sort_keys=True))

    def load_existing_json(self):
        """Load existing JSON data from file if it exists"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as json_file:
                try:
                    return json.load(json_file)
                except json.JSONDecodeError:
                    return []
        return []

    def save_as_json(self, new_data):
        """Save new data to a JSON file without duplicating existing content"""
        # Carregar dados existentes
        existing_data = self.load_existing_json()

        # Garantir que novos dados não sejam duplicados
        # Aqui estou assumindo que cada "dado" é um dicionário único com uma chave exclusiva como 'id'
        new_ids = {item['id'] for item in new_data}
        combined_data = [item for item in existing_data if item['id'] not in new_ids] + new_data

        # Salvar os dados combinados (existentes + novos) no arquivo
        with open(self.filename, "w") as json_file:
            json.dump(combined_data, json_file, indent=4, sort_keys=True)
            print(f"Dados atualizados e salvos em {self.filename} no formato JSON")

    def save_as_json_data_transacional(self, data):
        """Save data to a JSON file"""
        with open(self.filename, "w") as json_file:
            json.dump(data, json_file, indent=4, sort_keys=True)
            print(f"Dados salvos em {self.filename} no formato JSON")
