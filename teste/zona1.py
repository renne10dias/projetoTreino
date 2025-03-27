import json
import matplotlib.pyplot as plt
from utils.LoadFile import LoadFile
from datetime import datetime

# Load the data
loadFile = LoadFile()
workouts = loadFile.load_bio_data()  # Assuming this returns your JSON bio_data

# Function to determine heart rate zone
def get_heart_rate_zone(avg_hr, max_hr):
    percentage = (avg_hr / max_hr) * 100
    if percentage < 50:
        return "Zona 1"
    elif 50 <= percentage <= 60:
        return "Zona 2"
    elif 60 < percentage <= 70:
        return "Zona 3"
    elif 70 < percentage <= 85:
        return "Zona 4"
    else:
        return "Zona 5"

# Function to find workout by date
def find_workout_by_date(workouts, day, month, year):
    target_date = datetime(year, month, day).date()
    for workout in workouts:
        workout_date = datetime.strptime(workout["start_time"], "%Y-%m-%dT%H:%M:%S").date()
        if workout_date == target_date:
            return workout
    return None

# Specify the date (example: 4th September 2024)
day, month, year = 17, 9, 2024  # You can change this to any date in your dataset
selected_workout = find_workout_by_date(workouts, day, month, year)

if selected_workout:
    # Get data for the selected workout
    avg_hr = selected_workout["heart_rate"]["average"]
    max_hr = selected_workout["heart_rate"]["maximum"]
    calories = selected_workout["calories"]
    zone = get_heart_rate_zone(avg_hr, max_hr)

    # Prepare data for plotting
    zones = [zone]
    calories_data = [calories]
    counts_data = [1]  # Single workout, so count is 1

    # Create bar chart
    fig, ax1 = plt.subplots(figsize=(8, 6))

    # Bar width and positions
    bar_width = 0.4
    x = range(len(zones))

    # Plot calories on the left y-axis
    cal_bars = ax1.bar([i - bar_width/2 for i in x], calories_data, bar_width, color='#4CAF50', label='Calorias Totais')
    ax1.set_xlabel('Zona de Frequência Cardíaca', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Calorias Totais Queimadas', color='#4CAF50', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#4CAF50')
    ax1.grid(True, axis='y', linestyle='--', alpha=0.7)

    # Create a second y-axis for workout count
    ax2 = ax1.twinx()
    count_bars = ax2.bar([i + bar_width/2 for i in x], counts_data, bar_width, color='#FF5722', label='Número de Treinos')
    ax2.set_ylabel('Número de Treinos', color='#FF5722', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#FF5722')

    # Add data labels on top of bars
    for bar in cal_bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 10, f'{int(yval)}', ha='center', va='bottom', fontsize=10)
    for bar in count_bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f'{int(yval)}', ha='center', va='bottom', fontsize=10)

    # Title and customization
    plt.title(f'Treino em {day}/{month}/{year}: Zona de Frequência Cardíaca', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x)
    ax1.set_xticklabels(zones, fontsize=11)

    # Add legend
    fig.legend(handles=[cal_bars, count_bars], loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize=11)

    # Adjust layout
    plt.tight_layout()

    # Display the plot
    plt.show()
else:
    print(f"Nenhum treino encontrado para a data {day}/{month}/{year}.")