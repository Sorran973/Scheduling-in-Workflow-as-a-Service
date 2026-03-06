import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------------------------------------------
# 1. ВХОДНЫЕ ДАННЫЕ
# -----------------------------------------------------------------------------

# Названия алгоритмов (ось X)
labels = ['СЗЛ', 'КМС', 'EPSM', 'Жадный']
workflows = ['Montage', 'CyberShake', 'LIGO', 'SIPHT', 'Epigenomics']
deadline_factors = ['Плотное', 'Среднее', 'Расслабленное']

# Данные: Количество ВМ
vm_counts = {
    'xlarge': [3, 2, 34, 48],
    'large': [25, 26, 0, 0],
    'medium': [0, 1, 0, 0],
    'small': [1, 1, 4, 0],
    'micro': [3, 9, 2, 0]
}

workflow_name = workflows[3] + " (50 задач)"
deadline_factor = deadline_factors[2]


# Настройки оформления (штриховка и цвета)
# vm_styles = {
#     'xlarge': {'color': '#0D47A1', 'hatch': 'xx', 'label': 'Type Extra Large'},
#     'large':  {'color': '#1E88E5', 'hatch': '//', 'label': 'Type Large'},
#     'medium': {'color': '#42A5F5', 'hatch': '', 'label': 'Type Medium'},
#     'small':  {'color': '#90CAF9', 'hatch': '', 'label': 'Type Small'},
#     'micro':  {'color': '#E3F2FD', 'hatch': '..', 'label': 'Type Micro'}
# }
vm_styles = {
    'xlarge': {'color': '#0D47A1', 'label': 'Тип ВМ xlarge'},
    'large':  {'color': '#1E88E5', 'label': 'Тип ВМ large'},
    'medium': {'color': '#42A5F5', 'label': 'Тип ВМ medium'},
    'small':  {'color': '#90CAF9', 'label': 'Тип ВМ small'},
    'micro':  {'color': '#E3F2FD', 'label': 'Тип ВМ micro'}
}

stack_order = ['micro', 'small', 'medium', 'large', 'xlarge']

# -----------------------------------------------------------------------------
# 2. РАСЧЕТ ПРОЦЕНТОВ
# -----------------------------------------------------------------------------

raw_matrix = np.array([vm_counts[vm] for vm in stack_order])
totals = raw_matrix.sum(axis=0)
percent_matrix = np.divide(raw_matrix, totals, out=np.zeros_like(raw_matrix, dtype=float), where=totals != 0) * 100

# -----------------------------------------------------------------------------
# 3. ОТРИСОВКА
# -----------------------------------------------------------------------------

plt.rcParams.update({'font.size': 14, 'font.family': 'serif'})
fig, ax = plt.subplots(figsize=(10, 6))

bar_width = 0.5
x = np.arange(len(labels))
bottom_y = np.zeros(len(labels))

for i, vm_type in enumerate(stack_order):
    percentages = percent_matrix[i]  # Высота сегмента в %
    counts = raw_matrix[i]           # Реальное число ВМ (для подписи)
    style = vm_styles[vm_type]

    bars = ax.bar(x, percentages, bar_width, bottom=bottom_y,
                  label=style['label'],
                  color=style['color'],
                  edgecolor='black',
                  linewidth=0.8)

    # --- ДОБАВЛЕНИЕ ПОДПИСЕЙ ---
    for j, rect in enumerate(bars):
        height = rect.get_height()  # Высота текущего сегмента (в %)
        count = int(counts[j])  # Количество ВМ

        # Пишем текст только если сегмент достаточно большой (например, > 2%)
        # и если количество не ноль
        if count > 0 and height > 2:
            # Центр сегмента по X и Y
            cx = rect.get_x() + rect.get_width() / 2
            cy = rect.get_y() + height / 2

            # Выбор цвета текста: белый для темных фонов, черный для светлых
            text_color = 'white' if vm_type in ['xlarge'] else 'black'

            ax.text(cx, cy, str(count),
                    ha='center', va='center',
                    color=text_color,
                    fontsize=10,
                    fontweight='bold')

    # Обновляем дно для следующего слоя
    bottom_y += percentages

# Оформление осей
ax.set_ylabel('Распределение экземпляров ВМ по типам', fontweight='bold', fontsize=14)
ax.set_ylim(0, 100)
yticks = ax.get_yticks()
ax.set_yticklabels([f'{int(y)}%' for y in yticks])

ax.set_xticks(x)
ax.set_xticklabels(labels, fontweight='normal', fontsize=12)

# Тики внутрь
ax.tick_params(direction='in', top=True, right=True)

# # Легенда (в обратном порядке)
# handles, legend_labels = ax.get_legend_handles_labels()
# ax.legend(handles[::-1], legend_labels[::-1],
#           loc='upper right',
#           bbox_to_anchor=(0.99, 1.01),
#           frameon=True,
#           edgecolor='black',
#           fancybox=False,
#           fontsize=10)
#
# ax.set_title(workflow_name, fontweight='bold', fontsize=14, y=1.12)
#
# # plt.tight_layout()
# plt.tight_layout(rect=[0, 0, 1, 0.99])

# Заголовок слева (loc='left')
# y=1.02 немного приподнимает его над графиком
ax.set_title(workflow_name + ", " + deadline_factor + " временное ограничение", fontweight='bold', fontsize=14, y=1.08)

# Легенда справа сверху
handles, legend_labels = ax.get_legend_handles_labels()

ax.legend(
    handles[::-1], legend_labels[::-1],
    loc='lower center',           # "Якорь" легенды - её правый нижний угол...
    bbox_to_anchor=(0.5, 1.01),  # ...привязан к правому верхнему углу осей (над графиком)
    ncol=5,                      # В 2 столбца, чтобы было компактнее по высоте
    frameon=True,               # Без рамки (выглядит чище в заголовке)
    fontsize=10,
    borderaxespad=0
)

# # Оставляем место сверху под заголовок и легенду (top=0.85)
plt.subplots_adjust(top=0.85, bottom=0.05, left=0.12, right=0.99)

plt.savefig('vm_breakdown_chart.png', dpi=300)
plt.show()
