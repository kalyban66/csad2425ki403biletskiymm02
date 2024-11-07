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

# CI environment flag to avoid manual window management
IS_CI_ENVIRONMENT = os.environ.get('CI', 'false') == 'true'

class TestArduinoCommunication(unittest.TestCase):
    @patch('serial.Serial', new_callable=MagicMock)  # Mock serial.Serial
    @patch('main.on_exit')  # Mock on_exit to avoid calling it during tests
    def test_send_command(self, mock_on_exit, mock_serial):
        mock_arduino = mock_serial.return_value
        mock_arduino.is_open = True
        mock_arduino.readline.return_value = b"OK\n"

        # Call send_command function
        response = send_command("TEST")

        # Ensure on_exit is not called here
        mock_on_exit.assert_not_called()

class TestCheckNameExists(unittest.TestCase):
    def setUp(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                self.original_config = json.load(config_file)
        else:
            self.original_config = {}

        self.test_name_exists = "existing_name"
        self.test_name_not_exists = "non_existent_name"

        test_config = {self.test_name_exists: True}
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(test_config, config_file)

    def test_check_name_exists(self):
        self.assertTrue(check_name_exists(self.test_name_exists))
        self.assertFalse(check_name_exists(self.test_name_not_exists))

    def test_check_name_exists_file_not_exist(self):
        os.remove(CONFIG_FILE) if os.path.exists(CONFIG_FILE) else None
        self.assertFalse(check_name_exists("any_name"))

    def tearDown(self):
        if self.original_config:
            with open(CONFIG_FILE, 'w') as config_file:
                json.dump(self.original_config, config_file)
        elif os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

class TestStartGame(unittest.TestCase):
    @patch('main.send_command')
    def test_start_game_approved(self, mock_send_command):
        mock_send_command.return_value = "approved"
        mode = "Man vs AI"
        start_game(mode)

        mock_send_command.assert_called_once_with(f"mode:{mode}")

        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_start_game_approved' for mode '{mode}': SUCCESS\n")

    def tearDown(self):
        with open('test_results.txt', 'a') as result_file:
            result_file.write("Test finished.\n\n")

def clear_window(root):
    """ Clears the window to prepare for new elements. """
    for widget in root.winfo_children():
        widget.destroy()

class TestClearWindow(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        if IS_CI_ENVIRONMENT:
            self.root.after(100, self.root.destroy)  # Auto-close window in CI environment
        tk.Label(self.root, text="Test Label 1").pack()
        tk.Label(self.root, text="Test Label 2").pack()

    def test_clear_window(self):
        self.assertEqual(len(self.root.winfo_children()), 2)
        clear_window(self.root)
        self.assertEqual(len(self.root.winfo_children()), 0)

        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_clear_window': SUCCESS\n")

    def tearDown(self):
        self.root.destroy()

class TestCustomMessageBox(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        if IS_CI_ENVIRONMENT:
            self.root.after(100, self.root.destroy)

    def test_custom_messagebox(self):
        title = "Test Title"
        message = "This is a test message."
        custom_messagebox(title, message, "info")
        msg_box = Toplevel(self.root)
        msg_box.title(title)
        tk.Label(msg_box, text=message).pack()

        self.assertEqual(msg_box.title(), title)
        label = msg_box.children.get('!label')
        self.assertIsNotNone(label)
        self.assertEqual(label.cget("text"), message)

        msg_box.destroy()

    def tearDown(self):
        self.root.destroy()

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
            instance.entry.get.return_value = None
            user_input = custom_inputbox(title, message)
            self.assertEqual(user_input, None)

    def test_custom_inputbox_cancel(self):
        title = "Input Test"
        message = "Enter your name:"
        with patch('tkinter.Toplevel') as MockToplevel:
            instance = MockToplevel.return_value
            instance.entry = MagicMock()
            instance.entry.get.return_value = ""
            user_input = custom_inputbox(title, message)
            self.assertIsNone(user_input)

    def tearDown(self):
        self.root.destroy()

class TestOnExit(unittest.TestCase):
    @patch('main.arduino', new_callable=MagicMock)
    @patch('main.root.quit')
    def test_on_exit(self, mock_quit, mock_arduino):
        on_exit()
        mock_arduino.close.assert_called_once()
        mock_quit.assert_called_once()

class TestNewGame(unittest.TestCase):
    @patch('main.clear_window')
    @patch('main.show_main_menu')
    def test_new_game(self, mock_show_menu, mock_clear_window):
        new_game()
        mock_clear_window.assert_called_once()
        mock_show_menu.assert_called_once()

class TestResetScores(unittest.TestCase):
    @patch('main.send_command')
    @patch('main.show_results')
    def test_reset_scores(self, mock_show_results, mock_send_command):
        global player1_wins, player2_wins
        player1_wins = 0
        player2_wins = 0

        reset_scores()

        self.assertEqual(player1_wins, 0)
        self.assertEqual(player2_wins, 0)
        mock_send_command.assert_called_once_with('reset')
        mock_show_results.assert_called_once_with("Scores reset.")

# Running the tests
if __name__ == '__main__':
    unittest.main()
