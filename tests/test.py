import unittest
from unittest.mock import patch, MagicMock
import serial
import time

def arduino_communication(com_port):
    # Налаштування
    baud_rate = 9600
    timeout = 10

    # Створюємо з'єднання через серійний порт
    try:
        arduino = serial.Serial(com_port, baud_rate, timeout=timeout)
        time.sleep(2)  # Невелика затримка для встановлення з'єднання
        print(f"Connected to {com_port}")

        # Відправляємо повідомлення на Arduino
        message = "Hello from Python!"
        arduino.write((message + '\n').encode())
        print(f"Sent: {message}")

        # Читаємо привітальну відповідь від Arduino
        greeting_response = arduino.readline().decode('utf-8').strip()
        print(f"Massage received: {greeting_response}")

        # Читаємо оригінальне повідомлення, яке Arduino відправило назад
        echoed_message = arduino.readline().decode('utf-8').strip()
        print(f"The returned massage from Arduino Uno: {echoed_message}")

    except serial.SerialException as e:
        print(f"Error: {e}")

    finally:
        if arduino.is_open:
            arduino.close()
            print("The connection is closed")

class TestArduinoCommunication(unittest.TestCase):
    @patch('serial.Serial', new_callable=MagicMock)
    def test_arduino_communication(self, mock_serial):
        # Налаштовуємо імітацію об'єкта serial.Serial
        mock_arduino = mock_serial.return_value
        mock_arduino.readline.side_effect = [b'Hello from Arduino!', b'Hello back!']

        # Викликаємо функцію для тестування
        arduino_communication('COM5')

        # Перевіряємо, що Serial був викликаний з правильними параметрами
        mock_serial.assert_called_with('COM5', 9600, timeout=10)

        # Перевіряємо, що дані були надіслані
        mock_arduino.write.assert_called_once_with(b'Hello from Python!\n')

        # Перевіряємо, що дані були прочитані два рази
        self.assertEqual(mock_arduino.readline.call_count, 2)

if __name__ == '__main__':
    unittest.main()
