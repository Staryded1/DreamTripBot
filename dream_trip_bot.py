import telebot
from telebot import types
import firebase_admin
from firebase_admin import credentials, firestore
import requests  # Для загрузки изображений с Flask-сервера
import random  # Для генерации случайных чисел

# Токен бота
API_TOKEN = '7537169240:AAEphGXcruCQfF8c-mOGCr3_FGEx1fVe2aQ'

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)
bot.remove_webhook()

# Инициализация Firebase
cred = credentials.Certificate("dreamtrip-29c62-firebase-adminsdk-nr3zi-afa1f51676.json")
firebase_admin.initialize_app(cred)

# Подключение к Firestore
db = firestore.client()

# Адрес Flask-сервера (который отдает изображения)
FLASK_SERVER_URL = "http://localhost:5000/image/"

# ======= Функции работы с базой данных (Firebase) =======

# Сохранение данных об отпуске
def save_vacation_data(user_id, data_type, data):
    doc_ref = db.collection("vacations").document(user_id)
    doc_ref.set({data_type: data}, merge=True)

# Получение данных об отпуске
def get_vacation_data(user_id):
    doc_ref = db.collection("vacations").document(user_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

# ======= Основное меню =======
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Начать планирование", "Мои планы", "Напомни о подготовке", "Редактировать план"]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# ======= Стартовая команда =======
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я помогу тебе спланировать отпуск.")
    main_menu(message)

# Напоминание о подготовке с отправкой случайного изображения
@bot.message_handler(func=lambda message: message.text == "Напомни о подготовке")
def send_reminder_with_random_image(message):
    # Генерируем случайное число для выбора изображения 
    random_image_number = random.randint(1, 13)
    image_url = FLASK_SERVER_URL + f"{random_image_number}.jpg"

    try:
        # Загружаем изображение
        image_response = requests.get(image_url)
        image_response.raise_for_status()  # Проверка на ошибки загрузки

        # Отправляем изображение
        bot.send_photo(message.chat.id, image_response.content, caption="Не забудь начать подготовку к отпуску!")
    except requests.exceptions.RequestException:
        bot.send_message(message.chat.id, "Не удалось загрузить изображение с сервера.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")
    main_menu(message)


# ======= Начало планирования =======
@bot.message_handler(func=lambda message: message.text == "Начать планирование")
def ask_supervisor_approval(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Да", "Нет")
    bot.send_message(message.chat.id, "А согласовал ли ты даты своего отпуска с руководством?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_vacation_destination)

def ask_vacation_destination(message):
    response = message.text
    save_vacation_data(str(message.chat.id), "supervisor_approval", response)
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Да", "Нет")
    bot.send_message(message.chat.id, "Есть ли у тебя планы, куда поехать?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_travel_destination)

def ask_travel_destination(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Куда ты планируешь поехать?")
        bot.register_next_step_handler(message, ask_travel_partner)
    else:
        bot.send_message(message.chat.id, "Хорошо, я помогу тебе спланировать позже.")
        main_menu(message)

def ask_travel_partner(message):
    destination = message.text
    save_vacation_data(str(message.chat.id), "destination", destination)
    
    bot.send_message(message.chat.id, "С кем ты поедешь?")
    bot.register_next_step_handler(message, ask_vacation_tasks)

def ask_vacation_tasks(message):
    travel_partner = message.text
    save_vacation_data(str(message.chat.id), "travel_partner", travel_partner)
    
    bot.send_message(message.chat.id, "Напиши, что нужно успеть сделать в течение следующего отпуска — я напомню!")
    bot.register_next_step_handler(message, ask_ticket_booking)

def ask_ticket_booking(message):
    tasks = message.text
    save_vacation_data(str(message.chat.id), "tasks", tasks)
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Да", "Нет")
    bot.send_message(message.chat.id, "Забронированы ли билеты?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_ticket_date)

def ask_ticket_date(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "На какое число были куплены билеты?")
        bot.register_next_step_handler(message, ask_hotel_booking)
    else:
        save_vacation_data(str(message.chat.id), "ticket_date", "Не забронированы")
        save_vacation_data(str(message.chat.id), "ticket_status", "Нет")
        ask_hotel_booking(message)

def ask_hotel_booking(message):
    ticket_date = message.text
    if ticket_date != "Не забронированы":
        save_vacation_data(str(message.chat.id), "ticket_date", ticket_date)
        save_vacation_data(str(message.chat.id), "ticket_status", "Да")
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Да", "Нет")
    bot.send_message(message.chat.id, "Забронирован ли отель?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_hotel_date)

def ask_hotel_date(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "На какое число был забронирован отель?")
        bot.register_next_step_handler(message, ask_items_to_pack)
    else:
        save_vacation_data(str(message.chat.id), "hotel_date", "Не забронирован")
        save_vacation_data(str(message.chat.id), "hotel_status", "Нет")
        ask_items_to_pack(message)

def ask_items_to_pack(message):
    hotel_date = message.text
    if hotel_date != "Не забронирован":
        save_vacation_data(str(message.chat.id), "hotel_date", hotel_date)
        save_vacation_data(str(message.chat.id), "hotel_status", "Да")
    
    bot.send_message(message.chat.id, "Какие вещи ты планируешь взять с собой?")
    bot.register_next_step_handler(message, finish_planning)

def finish_planning(message):
    items = message.text
    save_vacation_data(str(message.chat.id), "items_to_pack", items)
    bot.send_message(message.chat.id, "Планирование завершено! Я сохраню все твои данные и буду напоминать тебе об отпуске.")
    main_menu(message)

# ======= Редактирование плана =======
@bot.message_handler(func=lambda message: message.text == "Редактировать план")
def edit_plan(message):
    user_id = str(message.chat.id)
    vacation_data = get_vacation_data(user_id)
    
    if vacation_data:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        buttons = []
        
        # Проверка на статус билетов
        ticket_status = vacation_data.get("ticket_status")
        if ticket_status == "Нет" or ticket_status is None:
            buttons.append("Добавить дату покупки билетов")
        
        # Проверка на статус отеля
        hotel_status = vacation_data.get("hotel_status")
        if hotel_status == "Нет" or hotel_status is None:
            buttons.append("Добавить дату бронирования отеля")
        
        if buttons:
            markup.add(*buttons)
            bot.send_message(message.chat.id, "Что вы хотите обновить?", reply_markup=markup)
            bot.register_next_step_handler(message, handle_edit_selection)
        else:
            bot.send_message(message.chat.id, "Все пункты уже заполнены.")
            main_menu(message)
    else:
        bot.send_message(message.chat.id, "У тебя пока нет сохраненных данных для редактирования.")
        main_menu(message)

# ======= Обработка выбора редактирования =======
def handle_edit_selection(message):
    if message.text == "Добавить дату покупки билетов":
        ask_ticket_edit(message)
    elif message.text == "Добавить дату бронирования отеля":
        ask_hotel_edit(message)
    else:
        bot.send_message(message.chat.id, "Неверный выбор. Попробуйте снова.")
        main_menu(message)

# ======= Вопросы для билетов =======
def ask_ticket_edit(message):
    bot.send_message(message.chat.id, "На какое число вы планируете купить билеты?")
    bot.register_next_step_handler(message, save_ticket_edit)

def save_ticket_edit(message):
    ticket_date = message.text
    save_vacation_data(str(message.chat.id), "ticket_date", ticket_date)
    save_vacation_data(str(message.chat.id), "ticket_status", "Да")
    bot.send_message(message.chat.id, "Дата покупки билетов обновлена.")
    main_menu(message)

# ======= Вопросы для отеля =======
def ask_hotel_edit(message):
    bot.send_message(message.chat.id, "На какое число был забронирован отель?")
    bot.register_next_step_handler(message, save_hotel_edit)

def save_hotel_edit(message):
    hotel_date = message.text
    save_vacation_data(str(message.chat.id), "hotel_date", hotel_date)
    save_vacation_data(str(message.chat.id), "hotel_status", "Да")
    bot.send_message(message.chat.id, "Дата бронирования отеля обновлена.")
    main_menu(message)

# Запуск бота
bot.infinity_polling()
