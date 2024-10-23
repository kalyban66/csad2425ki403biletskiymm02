import unittest
from unittest.mock import patch, MagicMock
import main  # Замініть на назву вашого модуля, якщо потрібно


class TestGameFunctions(unittest.TestCase):
    """Тестування функцій гри."""

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
        mock_json_load.return_value = {'test_name': {'player1_wins': 1, 'player2_wins': 2}}
        result = main.check_name_exists('test_name')
        self.assertTrue(result)
        result = main.check_name_exists('non_existent_name')
        self.assertFalse(result)

    @patch('main.open', new_callable=unittest.mock.mock_open)
    def test_save_score_to_file(self, mock_open):
        """Тестує функцію збереження рахунку у файл.

        Перевіряє, чи правильно викликаються функції для збереження даних.
        """
        score_data = {
            'test_name': {
                'player1_wins': 1,
                'player2_wins': 2
            }
        }

        with patch('json.dump') as mock_json_dump:
            main.save_score_to_file('test_name', 1, 2)
            mock_open.assert_called_once_with('config.json', 'w')
            mock_json_dump.assert_called_once_with(score_data, mock_open(), indent=4)

    @patch('main.open', new_callable=unittest.mock.mock_open,
           read_data='{"test_name": {"player1_wins": 1, "player2_wins": 2}}')
    def test_get_all_scores_from_file(self, mock_open):
        """Тестує функцію отримання всіх рахунків з файлу.

        Перевіряє, чи правильно повертаються дані з файлу.
        """
        result = main.get_all_scores_from_file()
        self.assertEqual(result, {'test_name': {'player1_wins': 1, 'player2_wins': 2}})

    @patch('main.custom_inputbox', return_value='test_name')
    @patch('main.check_name_exists', return_value=False)
    @patch('main.save_score_to_file')
    def test_save_score(self, mock_save_score_to_file, mock_check_name_exists, mock_custom_inputbox):
        """Тестує функцію збереження рахунку.

        Перевіряє, чи правильно викликаються функції для збереження рахунку.
        """
        main.player1_wins = 1
        main.player2_wins = 2

        main.save_score()

        mock_custom_inputbox.assert_called_once_with("Save Score", "Enter your name:")
        mock_check_name_exists.assert_called_once_with('test_name')
        mock_save_score_to_file.assert_called_once_with('test_name', 1, 2)

    @patch('main.open', new_callable=unittest.mock.mock_open,
           read_data='{"test_name": {"player1_wins": 1, "player2_wins": 2}}')
    @patch('main.custom_messagebox')
    def test_load_score(self, mock_custom_messagebox, mock_open):
        """Тестує функцію завантаження рахунку.

        Перевіряє, чи правильно викликається повідомлення про успіх при завантаженні.
        """
        main.load_score()
        mock_custom_messagebox.assert_called_once_with("Success", "Game loaded with score: test_name!\n1 : 2", 'info')

    @patch('main.os.path.exists', return_value=False)
    @patch('main.custom_messagebox')
    def test_load_score_no_file(self, mock_custom_messagebox, mock_path_exists):
        """Тестує функцію завантаження рахунку без наявності файлу.

        Перевіряє, чи правильно викликається попередження про відсутність збережених рахунків.
        """
        main.load_score()
        mock_custom_messagebox.assert_called_once_with("Warning", "No saved scores available.", 'warning')


if __name__ == '__main__':
    unittest.main()
