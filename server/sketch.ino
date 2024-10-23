#include <Arduino.h>

int player1_wins = 0;  // Рахунок гравця 1
int player2_wins = 0;  // Рахунок гравця 2

void setup() {
  Serial.begin(9600);  // Ініціалізуємо серійну комунікацію
}

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');  // Читаємо повідомлення від клієнта

    if (message.startsWith("mode:")) {
      String mode = message.substring(5);  // Отримуємо обраний режим
      approve_mode(mode);  // Підтверджуємо обраний режим
    } else if (message == "reset") {
      reset_scores();  // Скидаємо рахунок
    } else {
      String result = determine_winner(message);
      Serial.println(result + " " + String(player1_wins) + ":" + String(player2_wins));  // Відправляємо результат
    }
  }
}

void approve_mode(String mode) {
  if (mode == "Man vs AI" || mode == "Man vs Man" || mode == "AI vs AI (Random Move)" || mode == "AI vs AI (Win Strategy)") {
    Serial.println("approved");
  } else {
    Serial.println("denied");
  }
}

String determine_winner(String message) {
  String player1 = message.substring(0, message.indexOf(":"));
  String player2 = message.substring(message.indexOf(":") + 1);

  if (player1 == player2) {
    return "It's a tie!";
  } else if ((player1 == "Rock" && player2 == "Scissors") ||
             (player1 == "Paper" && player2 == "Rock") ||
             (player1 == "Scissors" && player2 == "Paper")) {
    player1_wins++;  // Оновлюємо рахунок гравця 1
    return "Player 1 wins!";
  } else {
    player2_wins++;  // Оновлюємо рахунок гравця 2
    return "Player 2 wins!";
  }
}

void reset_scores() {
  player1_wins = 0;
  player2_wins = 0;
  Serial.println("Scores reset.");
}
