import serial
import time
import tkinter as tk
import random
import os
import json
from tkinter import ttk
from tkinter import Menu, Toplevel
from PIL import Image, ImageTk

# @file main.py
# @brief Головний файл для управління з'єднанням з Arduino і графічним інтерфейсом
# @details Цей файл містить функції для налаштування комунікації з Arduino та завантаження конфігурації з файлу.

def load_config():
    """
    @brief Завантажує ком-порт і швидкість з 'config.json'.
    @details Функція відкриває файл конфігурації 'config.json', читає налаштування
    та повертає значення ком-порту та швидкості.
    @return tuple Структура з двох елементів: ком-порт (str) та швидкість (int).
    """
    # Відкриття і читання конфігурації
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        # Повернення налаштувань
        return config['com_port'], config['baud_rate']
# Завантаження конфігурації
com_port, baud_rate = load_config()

# Підключення до Arduino
arduino = serial.Serial(com_port, baud_rate, timeout=1)
time.sleep(2)

# Глобальні змінні для вибору гравців та рахунку
player1_choice = None
player2_choice = None
player1_wins = 0
player2_wins = 0

current_mode = "default_mode"  # Поточний режим гри (можна змінити)
CONFIG_FILE = "config.json"

def send_command(command):
    """
    @brief Відправляє команду на Arduino і отримує відповідь.
    @details Функція відправляє команду у вигляді рядка, закодованого в байти,
    і читає відповідь з Arduino. Відповідь декодується з байтів у рядок.
    @param command Команда для відправлення (str).
    @return str Відповідь Arduino.
    """
    arduino.write((command + '\n').encode())  # Відправка команди
    response = arduino.readline().decode().strip()  # Отримання відповіді
    return response

def send_command1(message):
    """
    @brief Обробляє різні команди, пов'язані з іменами та результатами.
    @details Функція аналізує команду, яка отримана у вигляді рядка.
    Вона обробляє команди для перевірки наявності імені, збереження
    результатів гри та отримання всіх збережених результатів.
    @param message Команда для обробки (str).
    @return str Відповідь про результат обробки команди.
    """
    if message.startswith("check_name"):
        name = message.split(":")[1]  # Отримання імені
        return "name_exists" if check_name_exists(name) else "name_not_exists"
    elif message.startswith("save"):
        _, name, p1_wins, p2_wins = message.split(":")  # Отримання даних для збереження
        save_score_to_file(name, p1_wins, p2_wins)
        return "saved"
    elif message == "get_saved_scores":
        return get_all_scores_from_file()  # Отримання всіх збережених результатів
    return "unknown_command"  # Команда не розпізнана

def custom_messagebox(title, message, style_type):
    """
    @brief Кастомний messagebox для виведення інформації з кнопкою ОК.
    @details Функція створює нове вікно з заголовком та повідомленням.
    Вікно містить кнопку "OK" для закриття.
    @param title Заголовок вікна (str).
    @param message Повідомлення для відображення (str).
    @param style_type Тип стилю для елементів (str).
    """
    # Створюємо нове вікно
    msg_box = Toplevel()
    msg_box.title(title)
    msg_box.geometry("335x150")

    # Стиль кнопок та елементів
    style = ttk.Style()
    style.configure('TLabel', font=('Arial', 12), padding=10)
    style.configure('TButton', background='lightblue', font=('Arial', 10))

    # Задаємо заголовок та повідомлення
    label = ttk.Label(msg_box, text=message, style='TLabel')
    label.pack(pady=20)

    # Додаємо стилізовану кнопку
    button = ttk.Button(msg_box, text="OK", command=msg_box.destroy, style='TButton')
    button.pack(pady=10)


def custom_inputbox(title, message):
    """
    @brief Кастомне вікно для введення тексту з кнопками OK і Cancel.
    @details Функція створює нове вікно для введення тексту,
    яке містить поле вводу та кнопки для підтвердження або скасування введення.
    @param title Заголовок вікна (str).
    @param message Повідомлення для відображення (str).
    @return str Введений текст, або None, якщо вікно закрито без введення.
    """

    def on_ok():
        nonlocal user_input
        user_input = entry.get()  # Отримання введеного тексту
        if user_input:
            window.destroy()  # Закриває вікно, якщо текст введений

    user_input = None

    window = tk.Toplevel()  # Створення нового вікна
    window.title(title)
    window.geometry("300x150")  # Розмір вікна
    window.resizable(False, False)  # Забороняє змінювати розмір

    label = ttk.Label(window, text=message)  # Текст повідомлення
    label.pack(pady=10)

    entry = ttk.Entry(window, width=30)  # Поле для введення
    entry.pack(pady=10)
    entry.focus()  # Фокус на поле введення

    button_frame = ttk.Frame(window)  # Контейнер для кнопок
    button_frame.pack(pady=10)

    ok_button = ttk.Button(button_frame, text="OK", command=on_ok)  # Кнопка OK
    ok_button.pack(side="left", padx=5)

    cancel_button = ttk.Button(button_frame, text="Cancel", command=window.destroy)  # Кнопка Cancel
    cancel_button.pack(side="right", padx=5)

    window.grab_set()  # Блокування інших вікон
    window.wait_window()  # Чекає закриття вікна

    return user_input  # Повертає введений текст

def check_name_exists(name):
    """
    @brief Перевіряє, чи існує ім'я в JSON файлі.
    @details Функція перевіряє, чи ім'я, передане як параметр,
    присутнє в JSON файлі конфігурації.
    Якщо файл не існує, повертає False.
    @param name Ім'я, яке потрібно перевірити (str).
    @return bool True, якщо ім'я існує, інакше False.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            data = json.load(file)
            return name in data
    return False


def save_score_to_file(name, player1_wins, player2_wins):
    """
    @brief Записує рахунок у JSON файл.
    @details Функція зберігає рахунок гравців у JSON файлі конфігурації.
    Якщо файл вже існує, то дані з нього завантажуються і оновлюються.
    @param name Ім'я гравця, чиї результати зберігаються (str).
    @param player1_wins Кількість виграшів гравця 1 (int).
    @param player2_wins Кількість виграшів гравця 2 (int).
    """
    data = {}

    # Якщо файл існує, завантажити попередні дані
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                pass  # Якщо файл порожній або пошкоджений

    data[name] = {
        "player1_wins": player1_wins,
        "player2_wins": player2_wins
    }

    # Записуємо дані у файл із відступами для зручного читання
    with open(CONFIG_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def get_all_scores_from_file():
    """
    @brief Зчитує всі рахунки з файлу, починаючи з третього рядка.
    @details Функція перевіряє наявність файлу конфігурації.
    Якщо файл існує, дані зчитуються з JSON,
    і повертаються всі рахунки, пропускаючи непотрібні поля.
    @return dict Словник з іменами гравців як ключами
    та їх рахунками як значеннями. Повертає порожній словник у разі помилки.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            try:
                data = json.load(file)
                # Ігноруємо COM порт і baud_rate, повертаємо тільки рахунки
                return {k: v for k, v in data.items() if not isinstance(v, dict) or 'player1_wins' in v}
            except json.JSONDecodeError:
                return {}
    return {}


def save_score():
    """
    @brief Зберігає поточний рахунок і режим у файл config.json.
    @details Функція запитує у користувача ім'я для збереження рахунку.
    Якщо ім'я вже існує, видає попередження.
    Якщо ім'я введено коректно, зберігає рахунок у файл.
    """
    global player1_wins, player2_wins

    while True:
        name = custom_inputbox("Save Score", "Enter your name:")

        if name:  # Якщо ім'я введено
            if check_name_exists(name):
                custom_messagebox("Warning", f"The name '{name}' already exists. Please choose another name.",
                                  "warning")
            else:
                save_score_to_file(name, player1_wins, player2_wins)
                custom_messagebox("Success", f"Score saved for {name}!", "info")
                break
        else:
            custom_messagebox("Warning", "You must enter a name to save the score.", "warning")
            break

def load_score():
    """
    @brief Завантажує збережені рахунки з файлу config.json.
    @details Функція відкриває файл конфігурації для зчитування збережених рахунків.
    Якщо файл не знайдено або дані не можуть бути розпізнані,
    відображається повідомлення. Якщо рахунки доступні,
    створюється нове вікно для їх відображення.
    """
    try:
        with open(CONFIG_FILE, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        custom_messagebox("Warning", "No saved scores available.", 'warning')
        return

    if not data:
        custom_messagebox("Warning", "No saved scores available.", 'warning')
        return

    # Створення нового вікна
    load_window = tk.Toplevel(root)
    load_window.title("Load Score")
    load_window.geometry("300x400")
    load_window.configure(bg="#282c34")

    # Створення listbox з scrollbar
    list_frame = tk.Frame(load_window)
    list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Helvetica", 14))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    # Додавання збережень у listbox, пропускаючи перші два ключі
    skip_keys = ['com_port', 'baud_rate']  # ключі, які пропускаємо
    for name in data.keys():
        if name not in skip_keys:
            listbox.insert(tk.END, name)

    def select_score():
        """
        @brief Вибирає та завантажує вибране збереження.
        @details Функція отримує вибране ім'я рахунку з listbox.
        Якщо вибір не зроблено, відображається попередження.
        При завантаженні рахунку оновлюються глобальні змінні
        для рахунків гравців.
        """
        selected = listbox.curselection()
        if not selected:
            custom_messagebox("Warning", "Please select a score to load.", 'warning')
            return

        chosen_name = listbox.get(selected[0])
        score_data = data[chosen_name]

        global player1_wins, player2_wins
        player1_wins = score_data["player1_wins"]
        player2_wins = score_data["player2_wins"]

        custom_messagebox("Success", f"Game loaded with score: {chosen_name}!\n{player1_wins} : {player2_wins}", 'info')
        load_window.destroy()  # Закриваємо вікно після завантаження
        start_game(current_mode)

    def delete_score():
        """
        @brief Видаляє вибране збереження з файлу та listbox.
        @details Функція видаляє вибране ім'я рахунку з listbox
        і оновлює файл конфігурації, зберігаючи зміни.
        Якщо вибір не зроблено, відображається попередження.
        """
        selected = listbox.curselection()
        if not selected:
            custom_messagebox("Warning", "Please select a score to delete.", 'warning')
            return

        chosen_name = listbox.get(selected[0])
        del data[chosen_name]
        listbox.delete(selected[0])

        # Оновлення файлу після видалення
        with open(CONFIG_FILE, 'w') as file:
            json.dump(data, file, indent=4)

        custom_messagebox("Success", "Score deleted successfully!", 'info')

    # Кнопки для вибору та видалення
    select_button = tk.Button(load_window, text="Load save", font=("Helvetica", 14), command=select_score, bg="#6583e6",
                              activebackground="#528aa4")
    select_button.pack(pady=10)

    delete_button = tk.Button(load_window, text="Delete save", font=("Helvetica", 14), command=delete_score, bg="red",
                              activebackground="#528aa4")
    delete_button.pack(pady=10)

def on_exit():
    """
    @brief Закриває з'єднання з Arduino і виходить з програми.
    @details Функція закриває серійне з'єднання з Arduino
    та завершує роботу програми.
    """
    arduino.close()  # Закриває серійне з'єднання
    root.quit()  # Завершує роботу програми


def new_game():
    """
    @brief Очищає вікно та показує головне меню.
    @details Функція очищає поточний вміст вікна
    та відображає головне меню гри.
    """
    clear_window()  # Очищення поточного вмісту вікна
    show_main_menu()  # Показує головне меню


def reset_scores():
    """
    @brief Скидає рахунок перемог і відправляє команду на Arduino.
    @details Функція скидає рахунок гравців до нуля
    і надсилає команду 'reset' на Arduino.
    """
    global player1_wins, player2_wins
    player1_wins = 0
    player2_wins = 0
    send_command('reset')
    show_results("Scores reset.")


def show_actions_page():
    """
    @brief Показує сторінку з діями в грі 'Камінь-Ножиці-Папір'.
    @details Функція очищає вміст поточного вікна
    та відображає вітальний текст, аватар, заголовок та кнопки для дій.
    """
    clear_window()  # Очищує поточний вміст вікна

    # Вітальний текст
    welcome_label = tk.Label(root, text="Welcome \n to \n Rock-Paper-Scissors", font=("Helvetica", 24, "bold"), fg="white", bg="#282c34")
    welcome_label.pack(pady=2)  # Відступ

    avatar_img = resize_image("images/avatar.png", 125, 125)  # Завантажує і змінює розмір зображення
    root.avatar_image = avatar_img  # Зберігає зображення в корені

    avatar_label = tk.Label(root, image=avatar_img)  # Відображає аватар
    avatar_label.pack(pady=10)

    title_label = tk.Label(root, text="Сhoose an action:", font=("Helvetica", 24, "bold"), fg="white", bg="#282c34")
    title_label.pack(pady=20)

    # Кнопки дій
    actions = ["New", "Load", "Exit"]  # Назви кнопок
    commands = [new_game, load_score, on_exit]  # Відповідні функції для кожної кнопки

    for action, cmd in zip(actions, commands):
        # Встановлює червоний колір для кнопки "Exit"
        if action == "Exit":
            button = tk.Button(root, text=action, font=("Helvetica", 18), command=cmd, bg="red",
                               activebackground="#ff6666", bd=0, relief="flat", highlightthickness=0)
        else:
            button = tk.Button(root, text=action, font=("Helvetica", 18), command=cmd, bg="#6583e6",
                               activebackground="#528aa4", bd=0, relief="flat", highlightthickness=0)
        button.pack(pady=5)  # Відступ між кнопками

def show_main_menu():
    """
    @brief Відображає головне меню гри.
    @details Функція очищає вміст поточного вікна,
    відображає заголовок меню, текст інструкції,
    кнопки для вибору режиму гри та кнопку повернення.
    """
    clear_window()  # Очищує поточний вміст вікна

    title_label = tk.Label(root, text="Main Menu", font=("Helvetica", 32, "bold"), fg="white", bg="#282c34")
    title_label.pack(pady=20)  # Відображає заголовок "Main Menu"

    tk.Label(root, text="Select Play Mode:", font=("Helvetica", 25), fg="white", bg="#282c34").pack(pady=10)  # Текст інструкції

    play_modes = ["Man vs AI", "Man vs Man", "AI vs AI (Random Move)", "AI vs AI (Win Strategy)"]  # Варіанти гри
    for mode in play_modes:
        button = tk.Button(root, text=mode, font=("Helvetica", 18), command=lambda m=mode: start_game(m), bg="#6583e6",
                           activebackground="#528aa4", bd=0, relief="flat", highlightthickness=0)
        button.pack(pady=5)  # Створює кнопку для кожного режиму гри

    exit_choice = ["Back to actions"]  # Кнопка повернення до попереднього меню
    for mode in exit_choice:
        button = tk.Button(root, text=mode, font=("Helvetica", 18), command=show_actions_page, bg="red",
                           activebackground="#528aa4", bd=0, relief="flat", highlightthickness=0)
        button.pack(pady=5)  # Кнопка для повернення до сторінки дій


def clear_window():
    """
    @brief Очищає вікно, щоб підготувати до нових елементів.
    @details Функція знищує всі віджети у вікні,
    щоб підготувати його для відображення нових елементів.
    """
    for widget in root.winfo_children():
        widget.destroy()  # Знищує всі віджети у вікні

def start_game(mode):
    """
    @brief Починає гру в залежності від вибраного режиму.
    @param mode Вибраний режим гри.
    @details Глобальні змінні для режиму та виборів гравців
    ініціалізуються. Відправляє обраний режим на Arduino для підтвердження
    та відкриває відповідний вибір в залежності від режиму гри.
    """
    global current_mode, player1_choice, player2_choice  # Глобальні змінні для режиму та виборів гравців
    current_mode = mode  # Зберігає обраний режим

    # Ініціалізуємо вибори
    player1_choice = None
    player2_choice = None

    # Надсилає вибраний режим на Arduino для підтвердження
    response = send_command(f"mode:{mode}").strip()  # Відправляє команду і отримує відповідь
    print(f"Sent mode: {mode}, received response: {response}")  # Логування

    # Логування відповідей Arduino для діагностики
    if response == "approved":
        print(f"Mode '{mode}' approved by Arduino.")
        # Відкриває відповідний вибір для кожного режиму
        if mode == "Man vs Man":
            show_player_choice_page(1)  # Показує вибір для гравця 1
        elif mode == "Man vs AI":
            show_player_choice_page(1)  # Показує вибір для гравця 1
        elif mode == "AI vs AI (Random Move)":
            ai_move()  # Запускає гру для AI з випадковими ходами
        elif mode == "AI vs AI (Win Strategy)":
            ai_move_win_strategy()  # Запускає гру для AI з виграшною стратегією

def show_player_choice_page(player_num):
    """
    @brief Показує вибір гравця.
    @param player_num Номер гравця (1 або 2).
    @details Функція очищає вікно, відображає заголовок
    з номером гравця та створює кнопки для вибору ходу
    (Камінь, Ножиці, Папір).
    """
    clear_window()  # Очищає вікно для нових елементів

    title = f"Player {player_num} Turn"
    title_label = tk.Label(root, text=title, font=("Helvetica", 24), fg="white", bg="#282c34")
    title_label.pack(pady=20)  # Відображає заголовок з номером гравця

    # Завантаження зображень для вибору
    rock_img = resize_image("images/rock.png", 100, 100)
    paper_img = resize_image("images/paper.png", 100, 100)
    scissors_img = resize_image("images/scissors.png", 100, 100)

    # Кнопки для вибору ходу
    tk.Button(root, image=rock_img, command=lambda: player_move(player_num, "Rock")).pack(pady=10)
    tk.Button(root, image=paper_img, command=lambda: player_move(player_num, "Paper")).pack(pady=10)
    tk.Button(root, image=scissors_img, command=lambda: player_move(player_num, "Scissors")).pack(pady=10)

    # Зберігання зображень для подальшого використання
    root.rock_img = rock_img
    root.paper_img = paper_img
    root.scissors_img = scissors_img


def player_move(player_num, move):
    """
    @brief Обробляє хід гравця.
    @param player_num Номер гравця (1 або 2).
    @param move Вибір гравця (Камінь, Ножиці, Папір).
    @details Зберігає вибір гравця 1 або 2 в залежності від номера
    гравця. У режимі "Man vs AI" AI робить випадковий хід
    і визначається переможець. У режимі "Man vs Man"
    показується вибір для другого гравця.
    """
    global player1_choice, player2_choice  # Глобальні змінні для виборів гравців
    if player_num == 1:
        player1_choice = move  # Зберігає вибір гравця 1
        print(f"Player 1 chose {move}")

        if current_mode == "Man vs AI":
            player2_choice = random.choice(["Rock", "Paper", "Scissors"])  # AI робить випадковий хід
            print(f"AI chose {player2_choice}")
            determine_winner()  # Визначає переможця
        else:
            show_player_choice_page(2)  # Показує вибір для гравця 2 в режимі Man vs Man
    elif player_num == 2:
        player2_choice = move  # Зберігає вибір гравця 2
        print(f"Player 2 chose {move}")
        determine_winner()  # Визначає переможця після вибору гравця 2

def ai_move():
    """
    @brief AI робить випадковий хід.
    @details Функція генерує випадкові ходи для гравців
    1 та 2 (AI) і викликає функцію для визначення переможця.
    """
    global player1_choice, player2_choice
    player1_choice = random.choice(["Rock", "Paper", "Scissors"])
    player2_choice = random.choice(["Rock", "Paper", "Scissors"])
    determine_winner()

# Глобальна змінна для зберігання виборів гравця 1 за останні 5 ігор
player1_history = []

def ai_move_win_strategy():
    """
    @brief AI робить хід, реагуючи на частоту виборів гравця 1.
    @details AI генерує вибір гравця 1, зберігає його
    в історії і підраховує частоту виборів. AI потім вибирає
    контр-елемент на основі найчастішого вибору гравця 1.
    """
    global player1_choice, player2_choice

    # Гравець 1 робить випадковий хід
    player1_choice = random.choice(["Rock", "Paper", "Scissors"])

    # Додаємо вибір гравця 1 до історії
    player1_history.append(player1_choice)

    # Зберігаємо тільки останні 5 ходів
    if len(player1_history) > 5:
        player1_history.pop(0)

    # Підрахунок частоти виборів гравця 1
    frequency = {
        "Rock": player1_history.count("Rock"),
        "Paper": player1_history.count("Paper"),
        "Scissors": player1_history.count("Scissors"),
    }

    # Знаходимо найчастіший вибір
    most_common_choice = max(frequency, key=frequency.get)

    # Вибираємо контр-елемент
    if most_common_choice == "Rock":
        player2_choice = "Paper"  # Папір переможе камінь
    elif most_common_choice == "Paper":
        player2_choice = "Scissors"  # Ножиці переможуть папір
    else:
        player2_choice = "Rock"  # Камінь переможе ножиці

    print(f"Player 1 chose {player1_choice}, AI counters with {player2_choice}")
    determine_winner()  # Визначаємо переможця

def determine_winner():
    """
    @brief Визначає переможця гри на основі виборів гравців.
    @details Формує команду з виборів обох гравців,
    відправляє її на Arduino та отримує відповідь.
    Якщо один з гравців виграв, оновлюється рахунок.
    """
    global player1_wins, player2_wins  # Використовуємо глобальні змінні для рахунку
    command = f"{player1_choice}:{player2_choice}"  # Формуємо команду з виборів
    response = send_command(command)  # Відправляємо команду на Arduino та отримуємо відповідь

    # Перевіряємо, хто виграв
    if "Player 1 wins!" in response:
        player1_wins += 1  # Збільшуємо рахунок гравця 1
    elif "Player 2 wins!" in response:
        player2_wins += 1  # Збільшуємо рахунок гравця 2

    # Виводимо результати гри
    show_results(response)


def reset_scores():
    """
    @brief Скидає рахунок перемог.
    @details Оновлює глобальні змінні для рахунку гравців до нуля
    і відправляє команду на Arduino для скидання.
    Виводить повідомлення про скидання рахунку.
    """
    global player1_wins, player2_wins  # Використовуємо глобальні змінні для рахунку
    player1_wins = 0  # Скидаємо рахунок гравця 1
    player2_wins = 0  # Скидаємо рахунок гравця 2
    send_command('reset')  # Відправляємо команду на Arduino для скидання
    show_results("Scores reset.")  # Виводимо повідомлення про скидання рахунку


def play_again():
    """
    @brief Починає новий раунд у поточному режимі гри.
    @details Вибирає функцію для початку нового раунду
    в залежності від режиму гри, у якому зараз перебувають гравці.
    """
    # Вибирає функцію для початку нового раунду в залежності від режиму гри
    if current_mode == "Man vs Man":
        show_player_choice_page(1)  # Показує вибір для гравця 1
    elif current_mode == "Man vs AI":
        show_player_choice_page(1)  # Показує вибір для гравця 1
    elif current_mode == "AI vs AI (Random Move)":
        ai_move()  # AI робить випадковий хід
    elif current_mode == "AI vs AI (Win Strategy)":
        ai_move_win_strategy()  # AI використовує стратегію виграшу

def show_results(response):
    """
    @brief Відображає результати гри та оновлені рахунки.
    @details Очищає вікно, відображає вибір кожного гравця,
    результат гри, а також поточні рахунки.
    Додає кнопки для скидання рахунку,
    збереження результату, початку нової гри та повернення до меню.
    """
    clear_window()  # Очищає вікно для нових елементів

    # Заголовок результатів
    title_label = tk.Label(root, text="Results", font=("Helvetica", 25), fg="white", bg="#282c34")
    title_label.pack(pady=20)

    # Виводить вибір кожного гравця
    tk.Label(root, text=f"Player 1 choice: {player1_choice}", font=("Helvetica", 18), fg="white", bg="#282c34").pack(pady=5)
    tk.Label(root, text=f"Player 2 choice: {player2_choice}", font=("Helvetica", 18), fg="white", bg="#282c34").pack(pady=5)
    tk.Label(root, text=response, font=("Helvetica", 18), fg="yellow", bg="#282c34").pack(pady=20)

    # Виводить рахунок перемог
    tk.Label(root, text=f"Player 1 Wins: {player1_wins}", font=("Helvetica", 18), fg="white", bg="#282c34").pack(pady=5)
    tk.Label(root, text=f"Player 2 Wins: {player2_wins}", font=("Helvetica", 18), fg="white", bg="#282c34").pack(pady=5)

    # Додає кнопку для скидання рахунку зображенням
    reset_img = resize_image("images/refresh.png", 25, 25)  # Збільшує розмір зображення
    tk.Button(root, image=reset_img, command=reset_scores, bg="red", activebackground="#61afef", bd=0).pack(pady=10)

    # Додає кнопку для збереження рахунку
    save_button = tk.Button(root, text="Save Score", font=("Helvetica", 16), command=save_score, bg="#6583e6", activebackground="#61afef")
    save_button.pack(pady=10)

    # Кнопка для початку нової гри
    tk.Button(root, text="Play Again", font=("Helvetica", 18), command=play_again, bg="#6583e6", activebackground="#61afef").pack(pady=10)

    # Кнопка для повернення до головного меню
    tk.Button(root, text="Back to menu", font=("Helvetica", 18), command=new_game, bg="red", activebackground="#528aa4").pack(pady=10)

    root.reset_img = reset_img  # Зберігаємо посилання на зображення


def resize_image(path, width, height):
    """
    @brief Змінює розмір зображення.
    @param path Шлях до зображення, яке потрібно змінити.
    @param width Новий ширина зображення.
    @param height Новий висота зображення.
    @return Повертає зображення в форматі PhotoImage.
    """
    image = Image.open(path)  # Відкриваємо зображення з вказаного шляху
    return ImageTk.PhotoImage(image.resize((width, height)))  # Змінюємо розмір і повертаємо PhotoImage


# Створюємо основне вікно для гри
root = tk.Tk()  # Ініціалізуємо Tkinter
root.title("Rock-Paper-Scissors")  # Встановлюємо заголовок вікна
root.geometry("500x600")  # Встановлюємо розміри вікна
root.configure(bg="#282c34")  # Встановлюємо фон вікна

# Створюємо меню для гри
menu = Menu(root)  # Ініціалізуємо меню
root.config(menu=menu)  # Призначаємо меню головному вікну

# Створюємо підменю "Game"
game_menu = Menu(menu, tearoff=0)  # Ініціалізуємо підменю без роздільника
menu.add_cascade(label="Game", menu=game_menu)  # Додаємо підменю до головного меню

# Додаємо команди до підменю
game_menu.add_command(label="New", command=new_game)  # Команда для нової гри
game_menu.add_command(label="Save", command=save_score)  # Команда для збереження результату
game_menu.add_command(label="Load", command=load_score)  # Команда для завантаження результату

# Показуємо початкову сторінку дій
show_actions_page()  # Викликаємо функцію для відображення сторінки дій

# Обробка події закриття вікна
root.protocol("WM_DELETE_WINDOW", on_exit)  # Визначаємо, що робити при закритті вікна
root.mainloop()  # Запускаємо основний цикл обробки подій






