import matplotlib.pyplot as plt
import numpy as np

# Данные из примера (Алгоритмы A, Б, В)
algorithms = ['A', 'Б', 'В']
# Нормализованные данные времени и стоимости
time_normalized = [0.0, 1.0, 0.2]
cost_normalized = [1.0, 0.0, 0.83]

# --- Построение графика ---

plt.figure(figsize=(8, 6)) # Устанавливаем размер графика

# Scatter plot (точечный график)
plt.scatter(time_normalized, cost_normalized, color='blue', s=100)

# Добавляем подписи к точкам (названия алгоритмов)
for i, algo in enumerate(algorithms):
    plt.text(time_normalized[i] + 0.03, cost_normalized[i] + 0.03, algo, fontsize=12)

# Настройка осей и заголовка
plt.title('Компромисс между временем и стоимостью (Нормализованные значения)')
plt.xlabel('Нормализованное время выполнения (0=лучшее, 1=худшее)')
plt.ylabel('Нормализованная стоимость (0=лучшее, 1=худшее)')

# Установка пределов осей для наглядности
plt.xlim(-0.1, 1.1)
plt.ylim(-0.1, 1.1)

# Добавление сетки
plt.grid(True, linestyle='--', alpha=0.6)

# Отображение графика
plt.show()