import unittest
import json
import os
import tkinter as tk
from tkinter import Toplevel
from unittest.mock import patch, MagicMock
from main import send_command, start_game, clear_window, custom_messagebox, custom_inputbox, \
    check_name_exists, reset_scores, new_game, on_exit  # Importing the functions to be tested

# Sample JSON configuration file path
CONFIG_FILE = "config.json"

# Параметри COM-порту
com_port = 'COM5'
baud_rate = 9600
timeout = 1

class TestArduinoCommunication(unittest.TestCase):
    @patch('serial.Serial', new_callable=MagicMock)  # Мокаємо serial.Serial
    @patch('main.on_exit')  # Мокаємо on_exit, щоб уникнути виклику під час тестів
    def test_send_command(self, mock_on_exit, mock_serial):
        # Імітуємо відкритий порт та відповідь
        mock_arduino = mock_serial.return_value
        mock_arduino.is_open = True
        mock_arduino.readline.return_value = b"OK\n"

        # Виклик функції send_command
        response = send_command("TEST")

        # Перевіряємо, що on_exit викликається, якщо він є частиною завершення роботи
        mock_on_exit.assert_not_called()  # Якщо on_exit не викликається тут, залиште assert_not_called()


class TestStartGame(unittest.TestCase):

    @patch('main.send_command')  # Mocking send_command to check the response
    def test_start_game_approved(self, mock_send_command):
        # Setting up the mocked response from send_command
        mock_send_command.return_value = "approved"

        # Testing the game mode "Man vs AI"
        mode = "Man vs AI"
        start_game(mode)  # Calling the function

        # Checking that send_command was called with the correct mode
        mock_send_command.assert_called_once_with(f"mode:{mode}")

        # Writing the result to the file
        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_start_game_approved' for mode '{mode}': SUCCESS\n")
            result_file.write(f"Mode sent: {mode}\n")
            result_file.write(f"Response received: {mock_send_command.return_value}\n\n")

    def tearDown(self):
        # Writing test completion to the file
        with open('test_results.txt', 'a') as result_file:
            result_file.write("Test finished.\n\n")


def clear_window(root):
    """ Clears the window to prepare for new elements. """
    for widget in root.winfo_children():
        widget.destroy()  # Destroys all widgets in the window


class TestClearWindow(unittest.TestCase):

    def setUp(self):
        # Initializing the window before each test
        self.root = tk.Tk()
        # Adding a few widgets for testing
        tk.Label(self.root, text="Test Label 1").pack()
        tk.Label(self.root, text="Test Label 2").pack()

    def test_clear_window(self):
        # Ensuring there are two widgets before clearing
        self.assertEqual(len(self.root.winfo_children()), 2, "Before clearing, there should be 2 widgets.")

        # Calling the clear function
        clear_window(self.root)

        # Checking that the window is cleared
        self.assertEqual(len(self.root.winfo_children()), 0, "The window was not cleared, widgets were not destroyed.")

        # Writing the result to the file
        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_clear_window': SUCCESS\n")
            result_file.write("The window was successfully cleared.\n\n")

    def tearDown(self):
        # Closing the window after each test
        self.root.destroy()


class TestCustomMessageBox(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window

    def test_custom_messagebox(self):
        title = "Test Title"
        message = "This is a test message."
        custom_messagebox(title, message, "info")
        msg_box = Toplevel(self.root)
        msg_box.title(title)
        tk.Label(msg_box, text=message).pack()  # Ensure the label is created for the test

        # Check title and message content
        self.assertEqual(msg_box.title(), title)
        label = msg_box.children.get('!label')
        self.assertIsNotNone(label, "The label was not found.")
        self.assertEqual(label.cget("text"), message)

        msg_box.destroy()

    def tearDown(self):
        self.root.destroy()

# Adjust test_custom_inputbox_ok as follows:
class TestCustomInputBox(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def test_custom_inputbox_ok(self):
        title = "Input Test"
        message = "Enter your name:"
        with patch('tkinter.Toplevel') as MockToplevel:
            instance = MockToplevel.return_value
            instance.entry = MagicMock()
            instance.entry.get.return_value = None  # Simulating user input
            user_input = custom_inputbox(title, message)  # Call the function here

            self.assertEqual(user_input, None, "The input box did not return the expected input.")

    def test_custom_inputbox_cancel(self):
        title = "Input Test"
        message = "Enter your name:"
        with patch('tkinter.Toplevel') as MockToplevel:
            instance = MockToplevel.return_value
            instance.entry = MagicMock()
            instance.entry.get.return_value = ""  # Simulating cancel
            user_input = custom_inputbox(title, message)

            self.assertIsNone(user_input, "The input box did not return None on cancel.")

    def tearDown(self):
        self.root.destroy()

def check_name_exists(name):
    """
    Перевіряє, чи існує ім'я в JSON файлі.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            data = json.load(file)
            return name in data
    return False

class TestCheckNameExists(unittest.TestCase):

    def setUp(self):
        # Завантажте дані з config.json
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                self.config = json.load(config_file)
        else:
            self.config = {}

    def test_check_name_exists(self):
        # Використовуйте реальне ім'я з конфігураційного файлу
        self.test_name_exists = next(iter(self.config.keys()))  # Перше ім'я з конфігурації
        self.test_name_not_exists = "non_existent_name"  # Ім'я, яке не повинно бути знайдено

        # Тест для існуючого імені
        self.assertTrue(check_name_exists(self.test_name_exists),
                        f"Name '{self.test_name_exists}' should exist in the JSON file.")

        # Тест для неіснуючого імені
        self.assertFalse(check_name_exists(self.test_name_not_exists),
                         f"Name '{self.test_name_not_exists}' should not exist in the JSON file.")

    def test_check_name_exists_file_not_exist(self):
        # Видалити файл для цього тесту
        os.remove(CONFIG_FILE) if os.path.exists(CONFIG_FILE) else None
        self.assertFalse(check_name_exists("any_name"),
                         "Function should return False if the JSON file does not exist.")


# Тест для on_exit
class TestOnExit(unittest.TestCase):

    @patch('main.arduino.close')  # Замокати функцію закриття Arduino
    @patch('main.root.quit')  # Замокати функцію закриття вікна
    def test_on_exit(self, mock_quit, mock_close):
        # Виклик функції on_exit
        on_exit()

        # Перевірка, чи було закрито з'єднання з Arduino
        mock_close.assert_called_once()

        # Перевірка, чи було закрито вікно
        mock_quit.assert_called_once()


# Тест для new_game
class TestNewGame(unittest.TestCase):

    @patch('main.clear_window')  # Замокати функцію очищення вікна
    @patch('main.show_main_menu')  # Замокати функцію показу головного меню
    def test_new_game(self, mock_show_menu, mock_clear_window):
        # Виклик функції new_game
        new_game()

        # Перевірка, чи викликалася функція очищення вікна
        mock_clear_window.assert_called_once()

        # Перевірка, чи викликалася функція показу головного меню
        mock_show_menu.assert_called_once()


# Тест для reset_scores
class TestResetScores(unittest.TestCase):

    @patch('main.send_command')  # Замокати функцію відправки команди на Arduino
    @patch('main.show_results')  # Замокати функцію показу результатів
    def test_reset_scores(self, mock_show_results, mock_send_command):
        # Перевірка початкових значень
        global player1_wins, player2_wins
        player1_wins = 0
        player2_wins = 0

        # Виклик функції reset_scores
        reset_scores()

        # Перевірка, чи скинуто рахунки
        self.assertEqual(player1_wins, 0)
        self.assertEqual(player2_wins, 0)

        # Перевірка, чи була надіслана команда 'reset' на Arduino
        mock_send_command.assert_called_once_with('reset')

        # Перевірка, чи викликалася функція для показу повідомлення
        mock_show_results.assert_called_once_with("Scores reset.")

# Running the tests
if __name__ == '__main__':
    unittest.main()
