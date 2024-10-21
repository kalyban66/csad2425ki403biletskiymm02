

#include <Arduino.h>

int player1_wins = 0;  // Рахунок гравця 1
int player2_wins = 0;  // Рахунок гравця 2
String last_moves[5];  // Буфер для останніх 5 ходів AI1
int move_count = 0;

String player_names[10];  // Масив для збереження імен гравців
int scores_p1[10];
int scores_p2[10];
int score_count = 0;

void setup() {
  Serial.begin(9600);  // Ініціалізуємо серійну комунікацію
}void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');  // Читаємо повідомлення від клієнта

    if (message.startsWith("mode:")) {
      String mode = message.substring(5);  // Отримуємо обраний режим
      approve_mode(mode);  // Підтверджуємо обраний режим
    } else if (message == "reset") {
      reset_scores();  // Скидаємо рахунок
    } else if (message.startsWith("check_name:")) {
      check_name_in_database(message);  // Викликаємо функцію для перевірки імені
    } else if (message.startsWith("save:")) {
      save_score_to_database(message);  // Викликаємо функцію для збереження рахунку
    } else if (message == "get_saved_scores") {  
      send_saved_scores();  // Відправляємо список збережених рахунків
    } else if (message == "ai_move_win_strategy") {
      String ai_move = ai_move_win_strategy();  // Викликаємо функцію для AI
      Serial.println(ai_move);  // Відправляємо хід AI
    } else {
      String result = determine_winner(message);
      Serial.println(result + " " + String(player1_wins) + ":" + String(player2_wins));  // Відправляємо результат
    }
  }
}

String random_choice() {
  int random_num = random(0, 3);  // Генеруємо випадкове число від 0 до 2
  switch (random_num) {
    case 0: return "Rock";
    case 1: return "Paper";
    case 2: return "Scissors";
  }
  return "";  // На всяк випадок
}

String send_command(String command) {
  // Для простоти, тут повертаємо випадковий вибір
  // В реальному коді реалізуйте логіку, щоб повертати найбільш частий хід
  return last_moves[random(0, move_count)];  // Повертаємо випадковий хід з останніх
}

String ai_move_win_strategy() {
  // Вибір AI
  String player1_choice = random_choice(); // Генеруємо випадковий хід для гравця 1 (AI)
  
  // Запит найбільш частого ходу
  String most_frequent = send_command("get_most_frequent"); 

  String player2_choice;
  if (most_frequent == "Rock") {
    player2_choice = "Paper";  // Гравець 2 вибирає Папір
  } else if (most_frequent == "Paper") {
    player2_choice = "Scissors";  // Гравець 2 вибирає Ножиці
  } else {
    player2_choice = "Rock";  // Гравець 2 вибирає Камінь
  }
  
  // Оновлюємо останні ходи для AI
  update_last_moves(player1_choice);

  return player1_choice + ":" + player2_choice;  // Повертаємо ходи
}

void update_last_moves(String move) {
  // Оновлюємо останні ходи AI
  if (move_count < 5) {
    last_moves[move_count] = move;
    move_count++;
  } else {
    // Зсув ходів у буфер і додавання нового ходу
    for (int i = 0; i < 4; i++) {
      last_moves[i] = last_moves[i + 1];
    }
    last_moves[4] = move;
  }
}

void check_name_in_database(String message) {
  String check_name = message.substring(11);  // Отримуємо ім'я для перевірки

  // Перевіряємо, чи існує ім'я в базі
  for (int i = 0; i < score_count; i++) {
    if (player_names[i] == check_name) {
      Serial.println("name_exists");
      return;
    }
  }
  Serial.println("name_available");
}

void save_score_to_database(String message) {
  String save_name = message.substring(5, message.indexOf(":", 5));
  int first_colon = message.indexOf(":", 5);
  int second_colon = message.indexOf(":", first_colon + 1);
  int third_colon = message.indexOf(":", second_colon + 1);
  
  String player1_score = message.substring(first_colon + 1, second_colon);
  String player2_score = message.substring(second_colon + 1, third_colon);

  // Перевіряємо, що рахунки є числами
  if (player1_score.toInt() < 0 || player2_score.toInt() < 0) {
    Serial.println("Invalid scores provided.");
    return;  // Не зберігайте, якщо рахунки негативні
  }

  // Зберігаємо ім'я, рахунок і режим
  if (score_count < 10) {
    player_names[score_count] = save_name;
    scores_p1[score_count] = player1_score.toInt();
    scores_p2[score_count] = player2_score.toInt();
    score_count++;
  }
  
  Serial.println("saved");
}

void send_saved_scores() {
  for (int i = 0; i < score_count; i++) {
    Serial.println(player_names[i] + ":" + String(scores_p1[i]) + ":" + String(scores_p2[i]));
  }
  Serial.println("end");  // Означає кінець списку
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

  // Оновлюємо останні ходи для AI1
  if (move_count < 5) {
    last_moves[move_count] = player1;
    move_count++;
  } else {
    // Зсув ходів у буфер і додавання нового ходу
    for (int i = 0; i < 4; i++) {
      last_moves[i] = last_moves[i + 1];
    }
    last_moves[4] = player1;
  }
}

void reset_scores() {
  player1_wins = 0;
  player2_wins = 0;
  move_count = 0;
  Serial.println("Scores reset.");
}



