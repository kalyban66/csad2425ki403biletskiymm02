import unittest
import json
import os
import tkinter as tk
from tkinter import Toplevel
from unittest.mock import patch, MagicMock
from main import send_command, clear_window, custom_messagebox, custom_inputbox, \
    check_name_exists, reset_scores, new_game, on_exit
from coverage import Coverage

CONFIG_FILE = "config.json"

class TestArduinoCommunication(unittest.TestCase):
    @patch('serial.Serial', new_callable=MagicMock)  # Mock serial.Serial
    @patch('main.on_exit')  # Mock on_exit to avoid calling it during tests
    def test_send_command(self, mock_on_exit, mock_serial):
        mock_arduino = mock_serial.return_value
        mock_arduino.is_open = True
        mock_arduino.readline.return_value = b"OK\n"
        response = send_command("TEST")
        mock_on_exit.assert_not_called()

class TestCheckNameExists(unittest.TestCase):

    def setUp(self):
        # Backup current config.json if it exists
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                self.original_config = json.load(config_file)
        else:
            self.original_config = {}

        # Prepare the test config
        self.test_name_exists = "existing_name"
        self.test_name_not_exists = "non_existent_name"

        # Write test data to config.json
        test_config = {self.test_name_exists: True}
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(test_config, config_file)

        # Set environment to simulate test environment
        os.environ['TEST_ENV'] = 'true'  # Ensure the GUI doesn't start

    def test_check_name_exists(self):
        # Test for existing name
        self.assertTrue(check_name_exists(self.test_name_exists),
                        f"Name '{self.test_name_exists}' should exist in the JSON file.")

        # Test for non-existing name
        self.assertFalse(check_name_exists(self.test_name_not_exists),
                         f"Name '{self.test_name_not_exists}' should not exist in the JSON file.")

    def test_check_name_exists_file_not_exist(self):
        # Delete config.json temporarily
        os.remove(CONFIG_FILE) if os.path.exists(CONFIG_FILE) else None
        self.assertFalse(check_name_exists("any_name"),
                         "Function should return False if the JSON file does not exist.")

    def tearDown(self):
        # Restore the original config.json
        if self.original_config:
            with open(CONFIG_FILE, 'w') as config_file:
                json.dump(self.original_config, config_file)
        elif os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)  # Remove test config if it was created


def clear_window(root):
    """ Clears the window to prepare for new elements. """
    for widget in root.winfo_children():
        widget.destroy()  # Destroys all widgets in the window

class TestClearWindow(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        tk.Label(self.root, text="Test Label 1").pack()
        tk.Label(self.root, text="Test Label 2").pack()

    def test_clear_window(self):
        self.assertEqual(len(self.root.winfo_children()), 2, "Before clearing, there should be 2 widgets.")
        clear_window(self.root)
        self.assertEqual(len(self.root.winfo_children()), 0, "The window was not cleared, widgets were not destroyed.")

        # Write the result to the file
        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_clear_window': SUCCESS\n")
            result_file.write("The window was successfully cleared.\n\n")

    def tearDown(self):
        if self.root.winfo_exists():  # Перевіряємо, чи існує вікно перед його знищенням
            self.root.destroy()


class TestCustomMessageBox(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def test_custom_messagebox(self):
        title = "Test Title"
        message = "This is a test message."
        custom_messagebox(title, message, "info")
        msg_box = Toplevel(self.root)
        msg_box.title(title)
        tk.Label(msg_box, text=message).pack()

        self.assertEqual(msg_box.title(), title)
        label = msg_box.children.get('!label')
        self.assertIsNotNone(label, "The label was not found.")
        self.assertEqual(label.cget("text"), message)

        msg_box.destroy()

        # Write the result to the file
        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_custom_messagebox': SUCCESS\n")
            result_file.write(f"Message box title: {title}\n")
            result_file.write(f"Message box message: {message}\n\n")

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
            instance.entry.get.return_value = None  # Simulate user input
            user_input = custom_inputbox(title, message)

            self.assertEqual(user_input, None, "The input box did not return the expected input.")

        # Write the result to the file
        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_custom_inputbox_ok': SUCCESS\n")
            result_file.write(f"User input: {user_input}\n\n")

    def test_custom_inputbox_cancel(self):
        title = "Input Test"
        message = "Enter your name:"
        with patch('tkinter.Toplevel') as MockToplevel:
            instance = MockToplevel.return_value
            instance.entry = MagicMock()
            instance.entry.get.return_value = ""  # Simulate cancel
            user_input = custom_inputbox(title, message)

            self.assertIsNone(user_input, "The input box did not return None on cancel.")

        # Write the result to the file
        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_custom_inputbox_cancel': SUCCESS\n")
            result_file.write(f"User input: {user_input}\n\n")

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
    @patch('main.clear_window')  # Mock clear_window
    @patch('main.show_main_menu')  # Mock show_main_menu
    def test_new_game(self, mock_show_menu, mock_clear_window):
        new_game()
        mock_clear_window.assert_called_once()
        mock_show_menu.assert_called_once()

        # Write the result to the file
        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_new_game': SUCCESS\n")
            result_file.write("New game triggered, window cleared, and main menu displayed.\n\n")


class TestResetScores(unittest.TestCase):
    @patch('main.send_command')  # Mock send_command to Arduino
    @patch('main.show_results')  # Mock show_results
    def test_reset_scores(self, mock_show_results, mock_send_command):
        global player1_wins, player2_wins
        player1_wins = 0
        player2_wins = 0

        reset_scores()

        self.assertEqual(player1_wins, 0)
        self.assertEqual(player2_wins, 0)
        mock_send_command.assert_called_once_with('reset')
        mock_show_results.assert_called_once_with("Scores reset.")

        # Write the result to the file
        with open('test_results.txt', 'a') as result_file:
            result_file.write(f"Test 'test_reset_scores': SUCCESS\n")
            result_file.write(f"Player 1 wins: {player1_wins}, Player 2 wins: {player2_wins}\n")
            result_file.write("Scores were successfully reset.\n\n")


if __name__ == "__main__":
    unittest.main()
