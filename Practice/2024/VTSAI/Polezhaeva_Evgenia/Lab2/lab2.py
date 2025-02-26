# -*- coding: utf-8 -*-
"""lab2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TgUtbnDWTDdRimS4OSPCVPVJY4pyG5Ky

# Лабораторная работа 2

Солодкая М.А. P4240

Полежаева Е.И. P4240

## Стратегии обучения RL

В контексте обучения с подкреплением (Reinforcement Learning, RL), стратегии обучения модели определяют, каким образом агент исследует окружение и выбирает действия для максимизации награды. Эти стратегии разделяются на Exploration (исследование) и Exploitation (использование) и направлены на достижение баланса между изучением новых стратегий и максимизацией текущих знаний.
В обучении с подкреплением присутствует баланс между Exploration и Exploitation. Exploration включает в себя стратегии, направленные на изучение новых действий или состояний, чтобы расширить базу знаний. Exploitation, наоборот, использует текущие знания для выбора оптимальных действий и максимизации награды. Нахождение оптимального баланса между Exploration и Exploitation - ключевой аспект в достижении успешных стратегий обучения с подкреплением.
В данной работе мы рассмотрим различные стратегии и их влияние на обучение агента с использованием библиотек Gymnasium и Stable-Baseline3.

### Подготовка среды и библиотек

Установим необходимые библиотеки и создадим среду CartPole для экспериментов
"""

!pip install gymnasium
!pip install stable-baselines3
!pip install pyvirtualdisplay
!sudo apt-get install xvfb
!pip install swig
!pip install gymnasium[box2d]

"""Установка необходимых библиотек"""

import gymnasium as gym
from stable_baselines3 import SAC,DDPG
import numpy as np
import matplotlib.pyplot as plt

"""Создание окружения CarRacing-v2"""

env = gym.make("CarRacing-v2")

"""### Исследование различных стратегий
Исследуем влияние различных стратегий исследования на процесс обучения агента.

#### Epsilon-Greedy

Epsilon-Greedy - это одна из базовых стратегий исследования в обучении с подкреплением. Агент принимает решение о выборе действия с учетом двух возможных вариантов: с высокой вероятностью (1-epsilon) агент выбирает действие с максимальной оценкой (использование), а с низкой вероятностью (epsilon) - случайное действие (исследование). Это позволяет агенту совмещать использование текущих знаний с возможностью исследования новых стратегий.
"""

def epsilon_greedy(Q_values, epsilon):
    if np.random.rand() < epsilon:
        # Исследование
        return np.random.choice(len(Q_values))
    else:
        # Использование
        return np.argmax(Q_values)

"""#### Softmax
Стратегия Softmax представляет собой метод, который преобразует оценки ценности действий в вероятности их выбора. Эта стратегия учитывает "мягкость" выбора, регулируемую параметром температуры. При высокой температуре вероятности всех действий приближаются друг к другу, что способствует более случайному выбору (исследование), в то время как при низкой температуре выбирается действие с наибольшей оценкой (использованию).

Q-values - список значений Q-функции

temperature - параметр температуры
"""

def softmax(Q_values, temperature):
    exp_values = np.exp((Q_values - np.max(Q_values)) / temperature)
    probabilities = exp_values / exp_values.sum()
    return np.random.choice(len(Q_values), p=probabilities)

"""#### UCB1 (Upper Confidence Bound)
Стратегия UCB1 основана на оценке верхней границы для ценности действий. Агент выбирает действие, которое имеет максимальную смешанную оценку ценности и уверенность в этой оценке. Параметр, который регулирует уровень исследования, зависит от логарифма общего числа выполненных шагов.

total_counts -  кол-во выборов  действий

counts - кол-во выборов каждого действия
"""

def ucb1(Q_values, counts, total_counts):
    ucb_values = Q_values + np.sqrt((2 * np.log(total_counts)) / counts)
    return np.argmax(ucb_values)

"""Каждая из этих стратегий нацелена обеспечивать баланс между исследованием (поиск новых стратегий) и эксплуатацией (использование текущих знаний) в процессе обучения с подкреплением. Выбор конкретной стратегии зависит от характеристик задачи и предпочтений, таких как уровень исследования, требуемый для успешного обучения агента.

### Тестирование различных стратегий
На этом шаге мы рассмотрим модели реализующие некоторые из этих стратегий

#### DDPG
[DDPG](https://stable-baselines3.readthedocs.io/en/master/modules/ddpg.html) использует epsilon-greedy стратегию, добавляя шум к выбранному действию во время исследования.
"""

from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise
n_actions = env.action_space.shape[-1]
# создание шума
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
# инициализация модели DDPG
model = DDPG("MlpPolicy", env, action_noise=action_noise, verbose=1)
# обучение модели
model.learn(total_timesteps=5000, log_interval=1)
# сохранение модели
model.save("ddpg_car_racing")

# импорт модулей
import gym
from IPython import display
from pyvirtualdisplay import Display
from matplotlib import animation

# удаление предыдущей модели
del model
timestamp = 1000
# загрузка обученной модели
model = DDPG.load("ddpg_car_racing")
ddpg_reward = []
# запуск виртуального дисплея
d = Display()
d.start()
# создание среды CarRacing-v2
env = gym.make('CarRacing-v2')
obs = env.reset()
img = []
for i in range(timestamp):
    # предсказание действий
    action, _states = model.predict(obs)
    # выполнение действий в среде
    obs, reward, terminated, truncated = env.step(action)
    # добавление награды
    ddpg_reward.append(reward)
    # очистка вывода Collab
    display.clear_output(wait=True)
    # получение кадра среды
    img.append(env.render('rgb_array'))
    if d:
        env.reset()

# установка параметров
dpi = 72
interval = 1 # ms

# отображение анимации
plt.figure(figsize=(img[0].shape[1]/dpi,img[0].shape[0]/dpi),dpi=dpi)
patch = plt.imshow(img[0])
plt.axis=('off')
animate = lambda i: patch.set_data(img[i])
ani = animation.FuncAnimation(plt.gcf(),animate,frames=len(img),interval=interval)
display.display(display.HTML(ani.to_jshtml()))
env.close()

"""#### SAC
Стратегия исследования softmax применяется через термин энтропии в [SAC](https://stable-baselines3.readthedocs.io/en/master/modules/sac.html). Термин энтропия поощряет мягкое, вероятностное распределение действий, способствуя исследованию.
"""

import gymnasium as gym
# создание окружения CarRacing-v2
env = gym.make('CarRacing-v2', render_mode="rgb_array")
# инициализация
model = SAC("MlpPolicy", env, verbose=1)
# обучение модели
model.learn(total_timesteps=5000, log_interval=1)
# сохранение модели
model.save("sac_car_racing")

import gym
# удаление предыдущей модели
del model
# загрузка обученной модели
model = SAC.load("sac_car_racing")
# список для хранения значений награды для каждого шага
sac_reward = []
d = Display()
d.start()
# создание среды CarRacing-v2
env = gym.make('CarRacing-v2')
# сброс среды и получение начального наблюдения
obs = env.reset()
img = []
for i in range(timestamp):
    # предсказание действий
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated = env.step(action)
    # добавление награды в список
    sac_reward.append(reward)
    # очистка вывода Collab
    display.clear_output(wait=True)
    # получение кадра среды
    img.append(env.render('rgb_array'))
    if d:
        env.reset()

# установка параметров для анимации
dpi = 72
interval = 1 # ms

# отображение анимации
plt.figure(figsize=(img[0].shape[1]/dpi,img[0].shape[0]/dpi),dpi=dpi)
patch = plt.imshow(img[0])
plt.axis=('off')
animate = lambda i: patch.set_data(img[i])
ani = animation.FuncAnimation(plt.gcf(),animate,frames=len(img),interval=interval)
display.display(display.HTML(ani.to_jshtml()))
env.close()

"""Примеры выше демонстрируют возможность решить одну и ту же задачу с помощью двух моделей различных моделей, которые используют расмотренные ранее стратегии. Далее построим график, который отображает процесс обучения этих моделей."""

def plot_training_results(model_logs, model_names, total_steps=100):
    plt.figure(figsize=(12, 6))
    # построение графика
    for i, logs in enumerate(model_logs):
        plt.plot(np.arange(0, total_steps, 1), logs["reward"][:total_steps], label=model_names[i])
    plt.title("Comparison: SAC vs DDPG")
    plt.xlabel("Steps")
    plt.ylabel("Reward")
    plt.legend()
    plt.grid(True)
    plt.show()

# сохранение результатов обучения моделей DDPG и SAC
ddpg_logs = {"reward": []}
sac_logs = {"reward": []}

# добавление значение метрики reward в соответствующие словари
ddpg_logs["reward"] = ddpg_reward
sac_logs["reward"] = sac_reward

# вывод графика на экран
plot_training_results([ddpg_logs, sac_logs], ["DDPG", "SAC"])

"""
### Исследование влияния Learning Rate

Learning Rate (LR) является одним из ключевых гиперпараметров алгоритмов обучения с подкреплением, включая алгоритм Soft Actor-Critic (SAC). Этот параметр оказывает значительное влияние на эффективность обучения и способность алгоритма адаптироваться к изменениям в окружающей среде.

Learning Rate определяет размер шага, с которым модель обновляет свои веса в процессе градиентного спуска. В случае SAC, который является алгоритмом глубокого обучения, правильный выбор Learning Rate может определить успешность сходимости модели и её способность обучаться оптимальной стратегии.

В данном блоке мы рассмотрим важность параметра Learning Rate для алгоритма SAC, исследуем, как различные значения этого параметра могут влиять на процесс обучения. Далее мы представим код, который демонстрирует обучение модели SAC при различных значениях Learning Rate, а также проанализируем графики, позволяющие визуально оценить влияние этого параметра."""

import gymnasium as gym
# создание среды CarRacing-v2 из Gym
env = gym.make('CarRacing-v2')

# список learning rate, которые хотим проверить
learning_rates = [0.0001, 0.001, 0.01]
sac_reward = {0.0001:[],0.001:[],0.01:[]}

# итерация по разным learning rates
for lr in learning_rates:
    # создание модели SAC с заданным learning rate
    model = SAC('MlpPolicy', env, learning_rate=lr, verbose=1)

    # обучение модели
    model.learn(total_timesteps=5000)

    # сохранение обученной модели
    model.save(f'sac_car_racing_lr_{lr}')
    obs, info = env.reset()
    for i in range(50):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        sac_reward[lr].append(reward)
        if terminated or truncated:
            obs, info = env.reset()

# закрытие среды
env.close()

"""Проанализировав логи обучения модели можно увидеть, что выбор параметра learning_rate влияет, например, на время обучения модели.
Так же можно посчитать средний reward для различных значений learning_rate
"""

print(sum(sac_reward[0.0001])/len(sac_reward[0.0001]))
print(sum(sac_reward[0.001])/len(sac_reward[0.001]))
print(sum(sac_reward[0.01])/len(sac_reward[0.01]))

"""Представим результаты reward для моделей обученных с различным learning_rate на графике"""

sac_e4,sac_e3,sac_e2 = {}, {}, {}

sac_e4["reward"] = sac_reward[0.0001]
sac_e3["reward"] = sac_reward[0.001]
sac_e2["reward"] = sac_reward[0.01]

plot_training_results([sac_e4, sac_e3, sac_e2], ["0,0001", "0,001", "0,01"], total_steps=50)

"""Изменение параметра learning_rate при обучении алгоритма может существенно влиять на его производительность.

#### Маленький learning rate:

Обучение будет медленным, так как обновления весов модели будут небольшими.
Может потребоваться больше времени для достижения сходимости.
Существует риск застревания в локальных минимумах.

#### Средний learning rate:

Может оказаться хорошим компромиссом между скоростью обучения и стабильностью.
Быстрее, чем маленький learning_rate, но может все еще требовать достаточно большое количество времени для сходимости. Требует аккуратного подбора значения.

#### Большой learning rate:
Обучение в среднем будет быстрее, так как веса модели обновляются с большими шагами.
Может привести к нестабильному обучению, особенно если learning rate слишком велик.
Существует риск "перепрыгивания" оптимальных значений, что может замедлить или прервать сходимость.

#### Рекомендации
Начинать с относительно небольшого learning rate и постепенно увеличивать его, наблюдая за производительностью алгоритма. Можно также попробовать методы настройки гиперпараметров, чтобы автоматически подобрать оптимальные значения learning rate.

Помните, что результаты могут зависеть от конкретной задачи и структуры среды, поэтому рекомендуется проводить несколько экспериментов и внимательно анализировать результаты.

В данной лабораторной работе мы исследовали различные стратегии и влияние learning_rate на процесс обучения агента. Эксперименты позволяют нам понять, что различные стратегии и параметры лучше подходят для разных задач.
В качестве самостоятельной работы вы может дополнительно провести свои эксперименты, изменяя параметры и используя различные стратегии, чтобы более глубоко понять их влияние на обучение модели. Например, попробовать использовать одну из используемых в данной работе моделей на другом окружении Gym.

"""