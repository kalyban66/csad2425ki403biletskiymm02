void setup() { 
  Serial.begin(9600);               // Ініціалізуємо серійну комунікацію
  pinMode(12, OUTPUT);              // Встановлюємо 12 пін як вихід для індикації отримання
  pinMode(13, OUTPUT);              // Встановлюємо 13 пін як вихід для індикації надсилання
}

void loop() {
  if (Serial.available() > 0) {
    digitalWrite(12, HIGH);         // Увімкнути індикатор отримання
    String message = Serial.readStringUntil('\n');  // Читаємо повідомлення від клієнта
    digitalWrite(12, LOW);          // Вимкнути індикатор отримання

    // Відправляємо привітальне повідомлення клієнту
    digitalWrite(13, HIGH);         // Увімкнути індикатор надсилання
    Serial.println("Greetings from Arduino Uno!");  // Відправити привітальне повідомлення
    digitalWrite(13, LOW);          // Вимкнути індикатор надсилання

    // Відправляємо назад отримане повідомлення
    digitalWrite(13, HIGH);         // Увімкнути індикатор надсилання
    Serial.println(message);        // Відправляємо назад отримане повідомлення
    digitalWrite(13, LOW);          // Вимкнути індикатор надсилання
  }
}