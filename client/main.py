import tkinter as tk
from tkinter import Menu, messagebox, simpledialog
import serial
import time
from PIL import Image, ImageTk
import random  # Для AI
import os


# Підключення до Arduino
com_port = 'COM5'
baud_rate = 9600
arduino = serial.Serial(com_port, baud_rate, timeout=1)
time.sleep(2)


# Глобальні змінні для вибору гравців та рахунку
player1_choice = None
player2_choice = None
player1_wins = 0
player2_wins = 0

current_mode = "default_mode"  # Поточний режим гри (можна змінити)

SAVE_FILE = "saved_scores.txt"


def send_command(command):
    """Відправляє команду на Arduino."""
    arduino.write((command + '\n').encode())
    response = arduino.readline().decode().strip()
    return response

def send_command1(message):
    """Симулює відправлення команди на сервер Arduino та отримання відповіді."""
    # Імітація роботи з сервером
    if message.startswith("check_name"):
        name = message.split(":")[1]
        return "name_exists" if check_name_exists(name) else "name_not_exists"
    elif message.startswith("save"):
        _, name, p1_wins, p2_wins = message.split(":")
        save_score_to_file(name, p1_wins, p2_wins)
        return "saved"
    elif message == "get_saved_scores":
        return get_all_scores_from_file()
    return "unknown_command"


def on_exit():
    """Закриває з'єднання з Arduino та виходить з програми."""
    arduino.close()
    root.quit()


def new_game():
    clear_window()
    show_main_menu()


def check_name_exists(name):
    """Перевіряє, чи існує ім'я в текстовому файлі."""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as file:
            for line in file:
                if line.startswith(name):
                    return True
    return False


def save_score_to_file(name, player1_wins, player2_wins):
    """Зберігає ім'я та рахунки в текстовий файл."""
    with open(SAVE_FILE, 'a') as file:
        file.write(f"{name}:{player1_wins}:{player2_wins}\n")


def get_all_scores_from_file():
    """Отримує всі збережені рахунки з текстового файлу."""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as file:
            return file.read().strip()
    return ""


def save_score():
    """Зберігає поточний рахунок і режим на локальний текстовий файл."""
    global player1_wins, player2_wins

    while True:
        name = simpledialog.askstring("Save Score", "Enter your name:")

        if name:  # Якщо ім'я введено
            check_message = f"check_name:{name}"
            response = send_command1(check_message).strip()

            if response == "name_exists":
                messagebox.showwarning("Warning", f"The name '{name}' already exists. Please choose another name.")
            else:
                score_message = f"save:{name}:{player1_wins}:{player2_wins}"
                response = send_command1(score_message).strip()

                if response == "saved":
                    messagebox.showinfo("Success", f"Score saved for {name}!")
                    break
                else:
                    messagebox.showerror("Error", "Failed to save the score.")
                    break
        else:
            messagebox.showwarning("Warning", "You must enter a name to save the score.")
            break


def load_score():
    """Завантажує список збережених рахунків із текстового файлу і дозволяє вибрати для продовження гри."""
    scores = get_all_scores_from_file().strip().split("\n")

    if scores and scores[0]:
        chosen_score = simpledialog.askstring("Load Score", f"Choose a score:\n" + "\n".join(scores))

        if chosen_score:
            for score in scores:
                if score.startswith(chosen_score):
                    parts = score.split(":")
                    if len(parts) >= 3:
                        global player1_wins, player2_wins
                        player1_wins = int(parts[1])
                        player2_wins = int(parts[2])

                        print(
                            f"Loaded score: {chosen_score}, player1_wins: {player1_wins}, player2_wins: {player2_wins}")
                        messagebox.showinfo("Success",
                                            f"Game loaded with score: {chosen_score}!\n{player1_wins} : {player2_wins}")

                        start_game(current_mode)  # Запускаємо гру в завантаженому режимі
                        return
                    else:
                        messagebox.showerror("Error", f"Invalid score format: {score}")
            else:
                messagebox.showerror("Error", "No such score found.")
        else:
            messagebox.showwarning("Warning", "You must choose a score to load the game.")
    else:
        messagebox.showwarning("Warning", "No saved scores available.")


def reset_scores():
    """Скидає рахунок перемог і відправляє команду на Arduino."""
    global player1_wins, player2_wins
    player1_wins = 0
    player2_wins = 0
    send_command('reset')
    show_results("Scores reset.")


def show_actions_page():
    clear_window()

    # Текст "Welcome to Rock-Paper-Scissors"
    welcome_label = tk.Label(root, text="Welcome \n to \n Rock-Paper-Scissors", font=("Helvetica", 24, "bold"), fg="white", bg="#282c34")
    welcome_label.pack(pady=2)  # Додаємо відступ перед і після

    avatar_img = resize_image("images/avatar.png", 125, 125)
    root.avatar_image = avatar_img

    avatar_label = tk.Label(root, image=avatar_img)
    avatar_label.pack(pady=10)

    title_label = tk.Label(root, text="Сhoose an action:", font=("Helvetica", 24, "bold"), fg="white", bg="#282c34")
    title_label.pack(pady=20)

    # Кнопки дій
    actions = ["New", "Load", "Exit"]
    commands = [new_game, load_score, on_exit]

    for action, cmd in zip(actions, commands):
        # Встановлюємо червоний колір для кнопки "Exit"
        if action == "Exit":
            button = tk.Button(root, text=action, font=("Helvetica", 18), command=cmd, bg="red",
                               activebackground="#ff6666", bd=0, relief="flat", highlightthickness=0)
        else:
            button = tk.Button(root, text=action, font=("Helvetica", 18), command=cmd, bg="#6583e6",
                               activebackground="#528aa4", bd=0, relief="flat", highlightthickness=0)
        button.pack(pady=5)


def show_main_menu():
    """Відображає головне меню гри."""
    clear_window()

    title_label = tk.Label(root, text="Main Menu", font=("Helvetica", 32, "bold"), fg="white", bg="#282c34")
    title_label.pack(pady=20)

    tk.Label(root, text="Select Play Mode:", font=("Helvetica", 25), fg="white", bg="#282c34").pack(pady=10)

    play_modes = ["Man vs AI", "Man vs Man", "AI vs AI (Random Move)", "AI vs AI (Win Strategy)"]
    for mode in play_modes:
        button = tk.Button(root, text=mode, font=("Helvetica", 18), command=lambda m=mode: start_game(m), bg="#6583e6",
                           activebackground="#528aa4", bd=0, relief="flat", highlightthickness=0)
        button.pack(pady=5)

    exit_choice = ["Back to actions"]
    for mode in exit_choice:
        button = tk.Button(root, text=mode, font=("Helvetica", 18), command=show_actions_page, bg="red",
                           activebackground="#528aa4", bd=0, relief="flat", highlightthickness=0)
        button.pack(pady=5)


def clear_window():
    """Очищає вікно, щоб підготувати до нових елементів."""
    for widget in root.winfo_children():
        widget.destroy()


def start_game(mode):
    """Починає гру в залежності від вибраного режиму."""
    global current_mode, player1_choice, player2_choice
    current_mode = mode

    # Ініціалізуємо вибори
    player1_choice = None
    player2_choice = None

    # Надсилаємо вибраний режим на Arduino для підтвердження
    response = send_command(f"mode:{mode}").strip()
    print(f"Sent mode: {mode}, received response: {response}")  # Логування

    # Логування відповідей Arduino для діагностики
    if response == "approved":
        print(f"Mode '{mode}' approved by Arduino.")
        if mode == "Man vs Man":
            show_player_choice_page(1)
        elif mode == "Man vs AI":
            show_player_choice_page(1)  # Показуємо вибір гравця 1
        elif mode == "AI vs AI (Random Move)":
            ai_move()
        elif mode == "AI vs AI (Win Strategy)":
            ai_move_win_strategy()


def show_player_choice_page(player_num):
    """Показує вибір гравця."""
    clear_window()

    title = f"Player {player_num} Turn"
    title_label = tk.Label(root, text=title, font=("Helvetica", 24), fg="white", bg="#282c34")
    title_label.pack(pady=20)

    rock_img = resize_image("images/rock.png", 100, 100)
    paper_img = resize_image("images/paper.png", 100, 100)
    scissors_img = resize_image("images/scissors.png", 100, 100)

    tk.Button(root, image=rock_img, command=lambda: player_move(player_num, "Rock")).pack(pady=10)
    tk.Button(root, image=paper_img, command=lambda: player_move(player_num, "Paper")).pack(pady=10)
    tk.Button(root, image=scissors_img, command=lambda: player_move(player_num, "Scissors")).pack(pady=10)

    root.rock_img = rock_img
    root.paper_img = paper_img
    root.scissors_img = scissors_img


def player_move(player_num, move):
    """Обробляє хід гравця."""
    global player1_choice, player2_choice
    if player_num == 1:
        player1_choice = move
        print(f"Player 1 chose {move}")

        if current_mode == "Man vs AI":
            player2_choice = random.choice(["Rock", "Paper", "Scissors"])  # AI робить випадковий хід
            print(f"AI chose {player2_choice}")
            determine_winner()  # Визначаємо переможця після вибору гравця 1 і AI
        else:
            show_player_choice_page(2)  # Якщо це режим Man vs Man, показуємо вибір для гравця 2
    elif player_num == 2:
        player2_choice = move
        print(f"Player 2 chose {move}")
        determine_winner()  # Визначаємо переможця після вибору гравця 2 або AI


def ai_move():
    """AI робить випадковий хід."""
    global player1_choice, player2_choice
    player1_choice = random.choice(["Rock", "Paper", "Scissors"])
    player2_choice = random.choice(["Rock", "Paper", "Scissors"])
    determine_winner()


def ai_move_win_strategy():
    """AI грає за стратегією виграшу."""
    global player1_choice, player2_choice
    player1_choice = random.choice(["Rock", "Paper", "Scissors"])

    # Request the most frequent move from Arduino
    most_frequent = send_command('get_most_frequent')

    if most_frequent == "Rock":
        player2_choice = "Paper"
    elif most_frequent == "Paper":
        player2_choice = "Scissors"
    else:
        player2_choice = "Rock"
    determine_winner()


def determine_winner():
    global player1_wins, player2_wins
    command = f"{player1_choice}:{player2_choice}"
    response = send_command(command)

    if "Player 1 wins!" in response:
        player1_wins += 1
    elif "Player 2 wins!" in response:
        player2_wins += 1

    # Виведення рахунку з відповіді від Arduino
    show_results(response)


def reset_scores():
    """Скидає рахунок перемог і відправляє команду на Arduino."""
    global player1_wins, player2_wins
    player1_wins = 0
    player2_wins = 0
    send_command('reset')
    show_results("Scores reset.")


def play_again():
    """Починає новий раунд у поточному режимі."""
    if current_mode == "Man vs Man":
        show_player_choice_page(1)
    elif current_mode == "Man vs AI":
        show_player_choice_page(1)
    elif current_mode == "AI vs AI (Random Move)":
        ai_move()
    elif current_mode == "AI vs AI (Win Strategy)":
        ai_move_win_strategy()


def show_results(response):
    """Відображає результати гри та оновлені рахунки."""
    clear_window()

    # Збільшення шрифтів до 25
    title_label = tk.Label(root, text="Results", font=("Helvetica", 25), fg="white", bg="#282c34")
    title_label.pack(pady=20)

    tk.Label(root, text=f"Player 1 choice: {player1_choice}", font=("Helvetica", 18), fg="white", bg="#282c34").pack(pady=5)
    tk.Label(root, text=f"Player 2 choice: {player2_choice}", font=("Helvetica", 18), fg="white", bg="#282c34").pack(pady=5)
    tk.Label(root, text=response, font=("Helvetica", 18), fg="yellow", bg="#282c34").pack(pady=20)

    tk.Label(root, text=f"Player 1 Wins: {player1_wins}", font=("Helvetica", 18), fg="white", bg="#282c34").pack(pady=5)
    tk.Label(root, text=f"Player 2 Wins: {player2_wins}", font=("Helvetica", 18), fg="white", bg="#282c34").pack(pady=5)

    # Збільшення розміру зображення для кнопки
    reset_img = resize_image("images/refresh.png", 25, 25)  # Збільшений розмір

    # Збільшення кнопок до розміру шрифту 25
    tk.Button(root, image=reset_img, command=reset_scores, bg="red", activebackground="#528aa4", bd=0).pack(pady=10)

    # Додаємо кнопку "Save Score"
    save_button = tk.Button(root, text="Save Score", font=("Helvetica", 16), command=save_score, bg="#6583e6", activebackground="#61afef")
    save_button.pack(pady=10)

    tk.Button(root, text="Play Again", font=("Helvetica", 18), command=play_again, bg="#6583e6", activebackground="#528aa4").pack(pady=10)

    tk.Button(root, text="Back to menu", font=("Helvetica", 18), command=new_game, bg="red", activebackground="#528aa4").pack(pady=10)

    root.reset_img = reset_img  # Store image reference


def resize_image(path, width, height):
    """Змінює розмір зображення."""
    image = Image.open(path)
    return ImageTk.PhotoImage(image.resize((width, height)))


root = tk.Tk()
root.title("Rock-Paper-Scissors")
root.geometry("500x600")
root.configure(bg="#282c34")

menu = Menu(root)
root.config(menu=menu)

game_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="Game", menu=game_menu)
game_menu.add_command(label="New", command=new_game)
game_menu.add_command(label="Save", command=save_score)
game_menu.add_command(label="Load", command=load_score)

show_actions_page()
root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()





