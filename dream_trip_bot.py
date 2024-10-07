import telebot
from telebot import types

# Токен вашего бота (получите его у BotFather)
API_TOKEN = '7537169240:AAEphGXcruCQfF8c-mOGCr3_FGEx1fVe2aQ'

bot = telebot.TeleBot(API_TOKEN)

# Основное меню
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Добавить цель отпуска")
    item2 = types.KeyboardButton("Добавить задачу")
    item3 = types.KeyboardButton("Мои планы")
    item4 = types.KeyboardButton("Напомни о планировании")
    markup.add(item1, item2, item3, item4)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Стартовая команда
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я помогу тебе спланировать отпуск.")
    main_menu(message)

# Обработка выбора пользователя
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "Добавить цель отпуска":
        bot.send_message(message.chat.id, "Напишите вашу цель для отпуска:")
        bot.register_next_step_handler(message, add_goal)
    elif message.text == "Добавить задачу":
        bot.send_message(message.chat.id, "Напишите задачу, которую нужно выполнить:")
        bot.register_next_step_handler(message, add_task)
    elif message.text == "Мои планы":
        # Получение списка планов (пока заглушка)
        bot.send_message(message.chat.id, "Вот твои текущие планы: (данные пока заглушены)")
    elif message.text == "Напомни о планировании":
        # Напоминание о планировании (пока заглушка)
        bot.send_message(message.chat.id, "Не забудь согласовать даты и подумать, куда хочешь поехать!")

# Добавление цели отпуска
def add_goal(message):
    goal = message.text
    # Здесь нужно будет сохранить цель в базу данных
    bot.send_message(message.chat.id, f"Цель '{goal}' добавлена в ваш план!")

# Добавление задачи
def add_task(message):
    task = message.text
    # Здесь нужно будет сохранить задачу в базу данных
    bot.send_message(message.chat.id, f"Задача '{task}' добавлена в ваш план!")

# Запуск бота
bot.polling(none_stop=True)
