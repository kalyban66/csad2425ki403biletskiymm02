import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock
import main  # Імпортуємо ваш файл main

class TestGameFunctions(unittest.TestCase):
    """Тестування функцій гри."""

    @patch('main.arduino', new_callable=MagicMock)
    def test_send_command(self, mock_arduino):
        """Тестує функцію відправки команди на Arduino."""

        # Встановлюємо, що має повертати readline
        mock_arduino.readline.return_value = b'response\n'

        command = 'test_command'
        response = main.send_command(command)

        # Перевіряємо, що response є правильним
        self.assertEqual(response, 'response')

        # Перевіряємо, що arduino.write викликалась з правильним аргументом
        mock_arduino.write.assert_called_once_with(b'test_command\n')

    @patch('main.check_name_exists', return_value=True)  # Мок для check_name_exists
    @patch('main.save_score_to_file')  # Мок для save_score_to_file
    @patch('main.get_all_scores_from_file', return_value='scores_list')  # Мок для get_all_scores_from_file
    def test_send_command1(self, mock_get_all_scores, mock_save_score, mock_check_name):
        """Тестує функцію обробки команд."""

        # Тест на перевірку існування імені
        response = main.send_command1("check_name:John")
        self.assertEqual(response, "name_exists")
        mock_check_name.assert_called_once_with('John')

        # Тест на збереження результату
        response = main.send_command1("save:John:5:3")
        self.assertEqual(response, "saved")
        mock_save_score.assert_called_once_with('John', '5', '3')

        # Тест на отримання збережених результатів
        response = main.send_command1("get_saved_scores")
        self.assertEqual(response, 'scores_list')
        mock_get_all_scores.assert_called_once()

        # Тест на невідому команду
        response = main.send_command1("unknown_command")
        self.assertEqual(response, "unknown_command")

    @patch('main.load_config')
    def test_load_config(self, mock_load_config):
        """Тестує функцію завантаження конфігурації.

        Перевіряє, чи повертаються правильні значення порту та швидкості передачі.
        """
        mock_load_config.return_value = ('COM5', 9600)
        com_port, baud_rate = main.load_config()
        self.assertEqual(com_port, 'COM5')
        self.assertEqual(baud_rate, 9600)

    @patch('main.send_command')
    def test_send_command(self, mock_send_command):
        """Тестує функцію відправки команди.

        Перевіряє, чи повертається правильна відповідь.
        """
        mock_send_command.return_value = 'response'
        response = main.send_command('test_command')
        self.assertEqual(response, 'response')
        mock_send_command.assert_called_once_with('test_command')


    @patch('main.os.path.exists', return_value=True)
    @patch('main.json.load')
    def test_check_name_exists(self, mock_json_load, mock_path_exists):
        """Тестує функцію перевірки існування імені.
        Перевіряє, чи правильно визначається наявність імені в конфігурації.
        """
        mock_json_load.return_value = {'name1': {'player1_wins': 1, 'player2_wins': 2}}
        result = main.check_name_exists('name1')
        self.assertTrue(result)
        result = main.check_name_exists('non_existent_name')
        self.assertFalse(result)

    @patch('main.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    @patch('main.get_all_scores_from_file')  # Мок для уникнення виклику реальної операції читання
    def test_save_score_to_file(self, mock_get_all_scores_from_file, mock_json_dump, mock_open):
        """Тестує функцію збереження рахунку у файл.

        Перевіряє, чи правильно викликаються функції для збереження даних.
        """
        score_data = {
            'name1': {
                'player1_wins': 1,
                'player2_wins': 2
            }
        }

        # Мок для існуючих даних рахунку
        mock_get_all_scores_from_file.return_value = score_data

        # Виклик тестованої функції
        main.save_score_to_file('name1', 1, 2)

        # Перевірка, що json.dump викликався з правильними параметрами
        mock_json_dump.assert_called_once_with(score_data, mock_open(), indent=4)


    @patch('main.open', new_callable=unittest.mock.mock_open,
           read_data='{"name1": {"player1_wins": 1, "player2_wins": 2}}')
    def test_get_all_scores_from_file(self, mock_open):
        """Тестує функцію отримання всіх рахунків з файлу.

        Перевіряє, чи правильно повертаються дані з файлу.
        """
        result = main.get_all_scores_from_file()
        self.assertEqual(result, {'name1': {'player1_wins': 1, 'player2_wins': 2}})

    @patch('main.custom_inputbox', return_value='name1')
    @patch('main.check_name_exists', return_value=False)
    @patch('main.save_score_to_file')
    def test_save_score(self, mock_save_score_to_file, mock_check_name_exists, mock_custom_inputbox):
        """Тестує функцію збереження рахунку.

        Перевіряє, чи правильно викликаються функції для збереження рахунку.
        """
        main.player1_wins = 1
        main.player2_wins = 2
        main.chosen_name = 'name1'

        main.save_score()

        mock_custom_inputbox.assert_called_once_with("Save Score", "Enter your name:")
        mock_save_score_to_file.assert_called_once_with('name1', 1, 2)

    class TestLoadScore(unittest.TestCase):
        @patch('main.custom_messagebox')  # Мокуємо custom_messagebox
        @patch('main.get_all_scores_from_file')  # Мокуємо функцію для отримання рахунків з файлу
        def test_load_score(self, mock_get_all_scores_from_file, mock_custom_messagebox):
            """Тестуємо завантаження рахунку і перевіряємо виклик custom_messagebox."""

            # Мокуємо повернене значення функції get_all_scores_from_file
            mock_get_all_scores_from_file.return_value = {
                'name1': {'player1_wins': 1, 'player2_wins': 2}
            }

            # Встановлюємо значення глобальних змінних для тестування
            main.chosen_name = 'name1'
            main.player1_wins = 1
            main.player2_wins = 2

            # Викликаємо функцію load_score
            main.load_score()

            # Перевіряємо, що custom_messagebox викликано з очікуваними аргументами
            mock_custom_messagebox.assert_called_once_with(
                "Success", f"Game loaded with score: name1!\n1 : 2", 'info'
            )

    @patch('main.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    @patch('main.get_all_scores_from_file')  # Mock to avoid triggering read operation
    def test_save_score_to_file(self, mock_get_all_scores_from_file, mock_json_dump, mock_open):
        """
        Тестує функцію збереження рахунку у файл.
        Перевіряє, чи правильно викликаються функції для збереження даних.
        """
        score_data = {
            'name1': {
                'player1_wins': 1,
                'player2_wins': 2
            }
        }

        # Simulate existing scores for saving
        mock_get_all_scores_from_file.return_value = score_data

        # Call the function being tested
        main.save_score_to_file('name1', 1, 2)

        # Check that json.dump was called with the correct parameters
        mock_json_dump.assert_called_once_with(score_data, mock_open(), indent=4)

class TestShowResults(unittest.TestCase):
    @patch('main.tk.Label')
    @patch('main.tk.Button')
    @patch('main.clear_window')  # Мокаємо функцію clear_window
    @patch('main.resize_image', return_value=MagicMock())  # Мокаємо функцію зміни розміру зображення
    def test_show_results(self, mock_resize_image, mock_button, mock_label, mock_clear_window):
        """Тестуємо функцію show_results."""

        # Налаштування тестових значень
        main.root = tk.Tk()  # Створення кореневого вікна Tkinter
        main.player1_choice = "Rock"
        main.player2_choice = "Scissors"
        main.player1_wins = 1
        main.player2_wins = 0

        response = "Player 1 Wins!"

        # Викликаємо тестовану функцію
        main.show_results(response)

        # Перевіряємо, що clear_window був викликаний хоча б один раз
        mock_clear_window.assert_called()

        # Виводимо всі виклики mock_label
        print("Label calls:", mock_label.call_args_list)

        # Перевіряємо, що Label був викликаний з правильними параметрами
        expected_calls = [
            (main.root, "Results", ("Helvetica", 25), "white", "#282c34"),
            (main.root, "Player 1 choice: Rock", ("Helvetica", 18), "white", "#282c34"),
            (main.root, "Player 2 choice: Scissors", ("Helvetica", 18), "white", "#282c34"),
            (main.root, response, ("Helvetica", 18), "yellow", "#282c34"),
            (main.root, "Player 1 Wins: 1", ("Helvetica", 18), "white", "#282c34"),
            (main.root, "Player 2 Wins: 0", ("Helvetica", 18), "white", "#282c34"),
        ]

        # Перевіряємо, що кожен очікуваний виклик був виконаний
        for args in expected_calls:
            mock_label.assert_any_call(*args)

        # Перевіряємо створення кнопок
        button_calls = [
            (main.root, mock_resize_image.return_value, main.reset_scores, "red"),
            (main.root, "Save Score", main.save_score, "#6583e6"),
            (main.root, "Play Again", main.play_again, "#6583e6"),
            (main.root, "Back to menu", main.new_game, "red"),
        ]

        # Перевіряємо виклики кнопок
        for button_call in button_calls:
            mock_button.assert_any_call(*button_call)
            mock_button.return_value.pack.assert_called_once_with(pady=10)

    def tearDown(self):
        """Очищення після кожного тесту."""
        main.root.destroy()




class TestCustomInputbox(unittest.TestCase):
    @patch('tkinter.Toplevel', new_callable=MagicMock)
    @patch('tkinter.Entry', new_callable=MagicMock)
    @patch('tkinter.Label', new_callable=MagicMock)
    @patch('tkinter.Button', new_callable=MagicMock)
    def test_custom_inputbox_ok(self, mock_button, mock_label, mock_entry, mock_toplevel):
        """Тестує функцію custom_inputbox при натисканні OK."""

        # Створюємо мок для вікна
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window

        # Налаштовуємо, щоб Entry повертав конкретне значення
        mock_entry.return_value.get.return_value = "test_input"

        # Симулюємо натискання кнопки OK
        ok_button = mock_button.return_value
        ok_button.invoke.side_effect = lambda: mock_window.destroy()

        # Виклик функції custom_inputbox
        result = main.custom_inputbox("Test Title", "Enter something:")

        # Перевіряємо, що результат правильний
        self.assertEqual(result, "test_input")

        # Перевіряємо, що вікно закрилося
        mock_window.destroy.assert_called_once()

    @patch('tkinter.Toplevel', new_callable=MagicMock)
    @patch('tkinter.Entry', new_callable=MagicMock)
    @patch('tkinter.Label', new_callable=MagicMock)
    @patch('tkinter.Button', new_callable=MagicMock)
    def test_custom_inputbox_cancel(self, mock_button, mock_label, mock_entry, mock_toplevel):
        """Тестує функцію custom_inputbox при натисканні Cancel."""

        # Створюємо мок для вікна
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window

        # Налаштовуємо, щоб Entry повертав пусте значення
        mock_entry.return_value.get.return_value = ""

        # Симулюємо натискання кнопки Cancel
        cancel_button = mock_button.return_value
        cancel_button.invoke.side_effect = lambda: mock_window.destroy()

        # Виклик функції custom_inputbox
        result = main.custom_inputbox("Test Title", "Enter something:")

        # Перевіряємо, що результат None
        self.assertIsNone(result)

        # Перевіряємо, що вікно закрилося
        mock_window.destroy.assert_called_once()


if __name__ == '__main__':
    unittest.main()