import json
import matplotlib.pyplot as plt
from utils.LoadFile import LoadFile

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

# Aggregate data by zone
zone_data = {
    "Zona 1": {"calories": 0, "count": 0},
    "Zona 2": {"calories": 0, "count": 0},
    "Zona 3": {"calories": 0, "count": 0},
    "Zona 4": {"calories": 0, "count": 0},
    "Zona 5": {"calories": 0, "count": 0}
}

for workout in workouts:
    avg_hr = workout["heart_rate"]["average"]
    max_hr = workout["heart_rate"]["maximum"]
    calories = workout["calories"]  
    zone = get_heart_rate_zone(avg_hr, max_hr)
    zone_data[zone]["calories"] += calories
    zone_data[zone]["count"] += 1

# Extract data for plotting
zones = list(zone_data.keys())
calories = [zone_data[zone]["calories"] for zone in zones]
counts = [zone_data[zone]["count"] for zone in zones]

# Create bar chart
fig, ax1 = plt.subplots(figsize=(12, 7))

# Bar width and positions
bar_width = 0.4
x = range(len(zones))

# Plot calories on the left y-axis
cal_bars = ax1.bar([i - bar_width/2 for i in x], calories, bar_width, color='#4CAF50', label='Calorias Totais')
ax1.set_xlabel('Zonas de Frequência Cardíaca', fontsize=12, fontweight='bold')
ax1.set_ylabel('Calorias Totais Queimadas', color='#4CAF50', fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#4CAF50')
ax1.grid(True, axis='y', linestyle='--', alpha=0.7)

# Create a second y-axis for workout count
ax2 = ax1.twinx()
count_bars = ax2.bar([i + bar_width/2 for i in x], counts, bar_width, color='#FF5722', label='Número de Treinos')
ax2.set_ylabel('Número de Treinos', color='#FF5722', fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='#FF5722')

# Add data labels on top of bars
for bar in cal_bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + 50, f'{int(yval)}', ha='center', va='bottom', fontsize=10)
for bar in count_bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{int(yval)}', ha='center', va='bottom', fontsize=10)

# Title and customization
plt.title('Calorias Totais e Número de Treinos por Zona de Frequência Cardíaca', fontsize=14, fontweight='bold', pad=20)
ax1.set_xticks(x)
ax1.set_xticklabels(zones, fontsize=11)

# Add legend
fig.legend(handles=[cal_bars, count_bars], loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize=11)

# Adjust layout
plt.tight_layout()

# Display the plot
plt.show()