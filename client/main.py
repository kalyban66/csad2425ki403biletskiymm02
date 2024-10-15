import serial
import time

# Налаштування COM-порту
com_port = 'COM5'  # Змініть на свій відповідний COM-порт
baud_rate = 9600   # Має збігатися зі швидкістю на Arduino
timeout = 10       # Тайм-аут для очікування даних

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