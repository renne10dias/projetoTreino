import json
import os
from datetime import datetime

from utils.LoadFile import LoadFile


# Função para calcular zonas de intensidade cardíaca
def calculate_heart_rate_zones(hr_max, hr_rest):
    # Método de Karvonen (usando frequência cardíaca de reserva)
    hr_reserve = hr_max - hr_rest
    zones = {
        "Zona 1": {"min": hr_rest, "max": hr_max * 0.50, "description": "Recuperação ativa (< 50% HR Max)"},
        "Zona 2": {"min": hr_max * 0.50, "max": hr_max * 0.60, "description": "Aeróbico leve (50-60% HR Max)"},
        "Zona 3": {"min": hr_max * 0.60, "max": hr_max * 0.70, "description": "Aeróbico moderado (60-70% HR Max)"},
        "Zona 4": {"min": hr_max * 0.70, "max": hr_max * 0.85, "description": "Limiar anaeróbico (70-85% HR Max)"},
        "Zona 5": {"min": hr_max * 0.85, "max": hr_max, "description": "Alta intensidade / VO2 Máx (> 85% HR Max)"}
    }
    return zones


# Função para classificar um treino em uma zona
def classify_training_zone(avg_hr, zones):
    for zone_name, zone_data in zones.items():
        if zone_data["min"] <= avg_hr <= zone_data["max"]:
            return zone_name, zone_data["description"]
    return "Fora de zona", "Frequência cardíaca fora das zonas definidas"


# Função principal para processar os treinos
def process_training_data(training_data, hr_max, hr_rest):
    zones = calculate_heart_rate_zones(hr_max, hr_rest)
    classified_sessions = []

    for session in training_data:
        avg_hr = session["heart_rate"]["average"]
        zone_name, zone_desc = classify_training_zone(avg_hr, zones)
        session_info = {
            "date": session["start_time"],
            "duration": session["duration"],
            "avg_hr": avg_hr,
            "max_hr": session["heart_rate"]["maximum"],
            "calories": session["calories"],
            "zone": zone_name,
            "zone_description": zone_desc
        }
        classified_sessions.append(session_info)

    return classified_sessions



# Executando o script
if __name__ == "__main__":
    # Carregar dados biológicos
    loader = LoadFile()
    bio_data = loader.load_bio_data()


    # Processar os treinos
    classified_sessions = process_training_data(bio_data, hr_max, hr_rest)

    # Exibir resultados
    for session in classified_sessions:
        print(f"Data: {session['date']}")
        print(f"Duração: {session['duration']}")
        print(f"Frequência Cardíaca Média: {session['avg_hr']} bpm")
        print(f"Frequência Cardíaca Máxima: {session['max_hr']} bpm")
        print(f"Calorias: {session['calories']}")
        print(f"Zona: {session['zone']} - {session['zone_description']}")
        print("-" * 50)