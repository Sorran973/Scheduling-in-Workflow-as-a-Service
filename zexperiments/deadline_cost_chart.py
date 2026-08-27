import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------------------------------------------
# 1. ВХОДНЫЕ ДАННЫЕ (Замени эти цифры на свои реальные значения)
# -----------------------------------------------------------------------------

# Ось X: Множители дедлайна
deadline_factors = ['Плотный', 'Средний', 'Расслабленный']

# Названия потоков работ (для Легенды)
algorithms = ['СЗЛ', 'КМС', 'EPSM', 'Жадный']
workflows = ['Montage', 'CyberShake', 'LIGO', 'SIPHT', 'Epigenomics']

# Данные по Normalized Cost (Стоимость) для каждого потока при каждом дедлайне.
# Структура: Каждый список соответствует одному Workflow.
# В списке должно быть столько же чисел, сколько значений в deadline_factors (8 штук).
montage = { # T=3 (between 0 and 1)
    'СЗЛ':    [1780, 1203, 963],
    'КМС':    [1780, 1203, 907],
    'EPSM':   [1799, 1460, 925],
    'Жадный': [2515, 1940, 1166]
}

cybershake = { # T=3 (between 0 and 1)
    'СЗЛ':    [2361, 2030, 1682],
    'КМС':    [2295, 1988, 1651],
    'EPSM':   [2951, 2107, 1664],
    'Жадный': [3580, 2268, 1787]
}

ligo = { # T=3 (between 1 and 2)
    'СЗЛ':    [4100, 3303, 2684],
    'КМС':    [4086, 3296, 2539],
    'EPSM':   [4228, 3377, 2539],
    'Жадный': [5232, 3691, 2714]
}

sipht = { # T=3 (between 1 and 2)
    'СЗЛ':    [1100, 792, 585],
    'КМС':    [1104, 776, 600],
    'EPSM':   [1487, 1080, 615],
    'Жадный': [1804, 1129, 654]
}

epigenomics = {
    'СЗЛ':    [4974, 3690, 3193],
    'КМС':    [4262, 3438, 2910],
    'EPSM':   [5512, 3951, 2911],
    'Жадный': [6793, 4941, 3277]
}


raw_data = epigenomics
workflow_name = workflows[4] + " (50 задач)"

# normalized_data = raw_data

max_baseline_cost = max(raw_data['Жадный'])
normalized_data = {}
for alg in algorithms:
    # Делим каждый элемент на max_baseline_cost
    normalized_data[alg] = [round(val / max_baseline_cost, 2) for val in raw_data[alg]]

# normalized_data = {}
# for alg in algorithms:
#     normalized_data[alg] = []
#     for i in range(len(deadline_factors)):
#         base_val = raw_data['Жадный'][i]
#         curr_val = raw_data[alg][i]
#         normalized_data[alg].append(curr_val / base_val)

# Цвета для каждого столбца (можно поменять на свои hex-коды или названия)
# Цвета подобраны похожими на твой скриншот (бордовый, голубой, розовый, сиреневый, фиолетовый)
colors = ['#8c4660', '#bceef4', '#f49ac1', '#b8bdf6']
# colors = ['blue', 'green', 'red', 'orange']


# -----------------------------------------------------------------------------
# 2. НАСТРОЙКА И ОТРИСОВКА ГРАФИКА
# -----------------------------------------------------------------------------

# Настройка размеров шрифтов для академического стиля
plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})

# Создаем фигуру
fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(deadline_factors))  # Позиции меток на оси X
width = 0.15  # Ширина одного столбца (подбери, чтобы влезало)

# Цикл отрисовки столбцов для каждого Workflow
for i, wf in enumerate(algorithms):
    # Вычисляем смещение для группы столбцов
    # Если 5 групп, смещения будут: -2*w, -1*w, 0, 1*w, 2*w
    offset = (i - len(algorithms) / 2 + 0.5) * width

    # Рисуем столбцы
    # zorder=3 ставит столбцы поверх сетки
    rects = ax.bar(x + offset, normalized_data[wf], width, label=wf, color=colors[i], edgecolor='black', zorder=3)

# -----------------------------------------------------------------------------
# 3. ОФОРМЛЕНИЕ ОСЕЙ И ЛЕГЕНДЫ
# -----------------------------------------------------------------------------

# Подписи осей (жирным шрифтом, как на скрине)
ax.set_xlabel('Временное ограничение', fontweight='bold', fontsize=12)
ax.set_ylabel('Нормализованная стоимость', fontweight='bold', fontsize=12)

# Настройка оси X
ax.set_xticks(x)
ax.set_xticklabels(deadline_factors)

# Настройка оси Y
# Устанавливаем лимит чуть выше максимума данных для красоты
ax.set_ylim(0, 1.15) # Увеличил лимит, чтобы столбцы не прилипали к верху
# ax.set_ylim(0, 2000)
# Сетка только по оси Y (горизонтальная), пунктирная
ax.grid(axis='y', linestyle='-', alpha=0.7, zorder=0)

# 1. ЗАГОЛОВОК (Title)
# y=1.15 поднимает заголовок еще выше, освобождая место для легенды
# fontsize=14 делает его крупнее
# Workflow Name можно сделать переменной
ax.set_title(workflow_name, fontweight='bold', fontsize=14, y=1.12)

# 2. ЛЕГЕНДА
# bbox_to_anchor=(0.5, 1.02) ставит легенду сразу над осями графика, но НИЖЕ заголовка
ax.legend(
    loc='lower center',
    bbox_to_anchor=(0.5, 1.01),
    ncol=4,
    frameon=True,
    borderaxespad=0
)

# 3. КОМПОНОВКА (Layout)
# rect=[0, 0, 1, 0.90] оставляет сверху 10% пустого места под заголовок и легенду
plt.tight_layout(rect=[0, 0, 1, 0.99])

# -----------------------------------------------------------------------------
# 4. СОХРАНЕНИЕ И ПОКАЗ
# -----------------------------------------------------------------------------

# Сохранить в высоком качестве (для вставки в диссертацию)
plt.savefig('deadline_cost_chart.png', dpi=300)
plt.savefig('deadline_cost_chart.pdf') # Векторный формат лучше для LaTeX

# Показать окно с графиком
# plt.show()