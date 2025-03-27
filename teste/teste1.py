import matplotlib.pyplot as plt
import numpy as np

# Dados fictícios: calorias queimadas por zona em diferentes dias
dias = ['Dia 1', 'Dia 2', 'Dia 3', 'Dia 4', 'Dia 5']  # Eixo X (dias)
zonas = ['Zona 1', 'Zona 2', 'Zona 3']  # Eixo Y (zonas de intensidade)

# Calorias queimadas por zona em cada dia (valores fictícios)
calorias_zona1 = [100, 120, 130, 110, 140]
calorias_zona2 = [150, 180, 160, 170, 180]
calorias_zona3 = [200, 210, 190, 220, 230]

# Quantidade de treinos por zona
treinos_zona1 = [4, 4, 4, 4, 4]
treinos_zona2 = [5, 5, 5, 5, 5]
treinos_zona3 = [5, 5, 5, 5, 5]

# Configuração para as barras agrupadas
bar_width = 0.25  # Largura das barras
index = np.arange(len(dias))  # Posições no eixo X

# Criação do gráfico de barras agrupadas
plt.figure(figsize=(10, 6))

# Barras para Zona 1, Zona 2 e Zona 3
plt.bar(index - bar_width, calorias_zona1, bar_width, label=f'Zona 1 (Treinos: {sum(treinos_zona1)})', color='blue')
plt.bar(index, calorias_zona2, bar_width, label=f'Zona 2 (Treinos: {sum(treinos_zona2)})', color='green')
plt.bar(index + bar_width, calorias_zona3, bar_width, label=f'Zona 3 (Treinos: {sum(treinos_zona3)})', color='orange')

# Adicionando título e rótulos
plt.title('Calorias Queimadas por Zona de Intensidade e Dia', fontsize=14)
plt.xlabel('Dias', fontsize=12)
plt.ylabel('Calorias Queimadas', fontsize=12)
plt.xticks(index, dias, fontsize=10)
plt.legend()

# Mostrar o gráfico
plt.tight_layout()
plt.show()