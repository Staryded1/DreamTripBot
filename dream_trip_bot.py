import telebot
from telebot import types
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Токен вашего бота
API_TOKEN = '7537169240:AAEphGXcruCQfF8c-mOGCr3_FGEx1fVe2aQ'

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Инициализация Firebase
cred = credentials.Certificate("dreamtrip-29c62-firebase-adminsdk-nr3zi-a504509610.json")
firebase_admin.initialize_app(cred)

# Подключение к Firestore
db = firestore.client()

# Пример функции для добавления задачи в Firebase
def add_task_to_db(user_id, goal, task):
    doc_ref = db.collection("goals").document(user_id).collection("tasks").document(goal)
    doc_ref.set({
        "tasks": firestore.ArrayUnion([task])
    }, merge=True)

# Пример функции для получения задач из Firebase
def get_tasks_from_db(user_id, goal):
    doc_ref = db.collection("goals").document(user_id).collection("tasks").document(goal)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("tasks", [])
    return []

# Удаление задачи
def remove_task_from_db(user_id, goal, task):
    doc_ref = db.collection("goals").document(user_id).collection("tasks").document(goal)
    doc_ref.update({
        "tasks": firestore.ArrayRemove([task])
    })

# Удаление цели и всех связанных задач
def remove_goal_from_db(user_id, goal):
    tasks_ref = db.collection("goals").document(user_id).collection("tasks").document(goal)
    tasks_ref.delete()

    goal_ref = db.collection("goals").document(user_id)
    goal_ref.update({
        goal: firestore.DELETE_FIELD
    })

# Сохранение дат отпуска
def add_vacation_dates_to_db(user_id, start_date, end_date):
    doc_ref = db.collection("vacations").document(user_id)
    doc_ref.set({
        "start_date": start_date,
        "end_date": end_date
    })

# Получение дат отпуска
def get_vacation_dates_from_db(user_id):
    doc_ref = db.collection("vacations").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

# Основное меню
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Добавить цель отпуска")
    item2 = types.KeyboardButton("Добавить задачу")
    item3 = types.KeyboardButton("Мои планы")
    item4 = types.KeyboardButton("Напомни о планировании")
    item5 = types.KeyboardButton("Удалить или изменить цель отпуска")
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Стартовая команда
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я помогу тебе спланировать отпуск.")
    main_menu(message)

# Запрос дат начала и конца отпуска
@bot.message_handler(func=lambda message: message.text == "Добавить цель отпуска")
def ask_vacation_start(message):
    bot.send_message(message.chat.id, "Пожалуйста, введите дату начала отпуска (в формате ДД.ММ.ГГГГ):")
    bot.register_next_step_handler(message, ask_vacation_end)

def ask_vacation_end(message):
    try:
        start_date = datetime.strptime(message.text, "%d.%m.%Y")
        bot.send_message(message.chat.id, "Теперь введите дату окончания отпуска (в формате ДД.ММ.ГГГГ):")
        bot.register_next_step_handler(message, save_vacation_dates, start_date)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Попробуйте снова.")
        ask_vacation_start(message)

def save_vacation_dates(message, start_date):
    try:
        end_date = datetime.strptime(message.text, "%d.%m.%Y")
        if end_date <= start_date:
            bot.send_message(message.chat.id, "Дата окончания отпуска не может быть раньше даты начала. Попробуйте снова.")
            ask_vacation_end(message)
        else:
            add_vacation_dates_to_db(str(message.chat.id), start_date.strftime("%d.%m.%Y"), end_date.strftime("%d.%m.%Y"))
            bot.send_message(message.chat.id, "Даты отпуска успешно сохранены! Теперь можете добавить цели.")
            bot.send_message(message.chat.id, "Напишите вашу цель для отпуска:")
            bot.register_next_step_handler(message, add_goal)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Попробуйте снова.")
        ask_vacation_end(message)

# Добавление цели отпуска
def add_goal(message):
    goal = message.text
    doc_ref = db.collection("goals").document(str(message.chat.id))
    doc_ref.set({
        goal: []
    }, merge=True)
    bot.send_message(message.chat.id, f"Цель '{goal}' добавлена! Теперь можете добавлять задачи.")
    main_menu(message)

# Добавление задачи
@bot.message_handler(func=lambda message: message.text == "Добавить задачу")
def choose_goal(message):
    goals_ref = db.collection("goals").document(str(message.chat.id))
    goals_doc = goals_ref.get()
    if goals_doc.exists:
        goals = list(goals_doc.to_dict().keys())
        if goals:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for goal in goals:
                markup.add(types.KeyboardButton(goal))
            bot.send_message(message.chat.id, "Выберите цель, для которой вы хотите добавить задачу:", reply_markup=markup)
            bot.register_next_step_handler(message, ask_task)
        else:
            bot.send_message(message.chat.id, "У вас нет целей отпуска. Сначала добавьте цель.")
            main_menu(message)
    else:
        bot.send_message(message.chat.id, "У вас нет целей отпуска. Сначала добавьте цель.")
        main_menu(message)

def ask_task(message):
    selected_goal = message.text
    bot.send_message(message.chat.id, f"Введите задачу для цели '{selected_goal}':")
    bot.register_next_step_handler(message, save_task, selected_goal)

def save_task(message, selected_goal):
    task = message.text
    add_task_to_db(str(message.chat.id), selected_goal, task)
    bot.send_message(message.chat.id, f"Задача '{task}' добавлена в цель '{selected_goal}'!")
    main_menu(message)

# Удаление или изменение цели отпуска
@bot.message_handler(func=lambda message: message.text == "Удалить или изменить цель отпуска")
def choose_goal_for_edit(message):
    goals_ref = db.collection("goals").document(str(message.chat.id))
    goals_doc = goals_ref.get()
    if goals_doc.exists:
        goals = list(goals_doc.to_dict().keys())
        if goals:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for goal in goals:
                markup.add(types.KeyboardButton(goal))
            bot.send_message(message.chat.id, "Выберите цель, которую хотите удалить или изменить:", reply_markup=markup)
            bot.register_next_step_handler(message, goal_edit_menu)
        else:
            bot.send_message(message.chat.id, "У вас нет целей отпуска.")
            main_menu(message)
    else:
        bot.send_message(message.chat.id, "У вас нет целей отпуска.")
        main_menu(message)

def goal_edit_menu(message):
    selected_goal = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton(f"Изменить задачи для '{selected_goal}'"))
    markup.add(types.KeyboardButton(f"Удалить цель '{selected_goal}'"))
    bot.send_message(message.chat.id, "Что вы хотите сделать?", reply_markup=markup)
    bot.register_next_step_handler(message, process_goal_edit, selected_goal)

def process_goal_edit(message, selected_goal):
    if "Изменить задачи" in message.text:
        tasks = get_tasks_from_db(str(message.chat.id), selected_goal)
        if tasks:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for task in tasks:
                markup.add(types.KeyboardButton(f"Удалить задачу '{task}'"))
            bot.send_message(message.chat.id, "Выберите задачу, которую хотите удалить:", reply_markup=markup)
            bot.register_next_step_handler(message, remove_task, selected_goal)
        else:
            bot.send_message(message.chat.id, f"В цели '{selected_goal}' нет задач для удаления.")
            main_menu(message)
    elif "Удалить цель" in message.text:
        remove_goal_from_db(str(message.chat.id), selected_goal)
        bot.send_message(message.chat.id, f"Цель '{selected_goal}' и все связанные задачи удалены!")
        main_menu(message)

def remove_task(message, selected_goal):
    task_to_remove = message.text.replace("Удалить задачу '", "").replace("'", "")
    remove_task_from_db(str(message.chat.id), selected_goal, task_to_remove)
    bot.send_message(message.chat.id, f"Задача '{task_to_remove}' удалена из цели '{selected_goal}'.")
    main_menu(message)

# Вывод планов (целей и задач)
@bot.message_handler(func=lambda message: message.text == "Мои планы")
def show_tasks(message):
    goals_ref = db.collection("goals").document(str(message.chat.id))
    goals_doc = goals_ref.get()
    if goals_doc.exists:
        response = ""
        for goal, tasks in goals_doc.to_dict().items():
            tasks_ref = db.collection("goals").document(str(message.chat.id)).collection("tasks").document(goal)
            tasks_doc = tasks_ref.get()
            task_list = tasks_doc.to_dict().get("tasks", []) if tasks_doc.exists else []
            response += f"Цель: {goal}\nЗадачи:\n" + "\n".join(task_list) + "\n\n"
        bot.send_message(message.chat.id, response if response else "У вас нет добавленных целей и задач.")
    else:
        bot.send_message(message.chat.id, "У вас нет добавленных целей и задач.")
    main_menu(message)

# Напоминание о планировании
@bot.message_handler(func=lambda message: message.text == "Напомни о планировании")
def remind_planning(message):
    vacation_info = get_vacation_dates_from_db(str(message.chat.id))
    if vacation_info:
        start_date = datetime.strptime(vacation_info["start_date"], "%d.%m.%Y")
        days_left = (start_date - datetime.now()).days

        if days_left > 0:
            response = f"До начала отпуска осталось {days_left} дней.\n"
            goals_ref = db.collection("goals").document(str(message.chat.id))
            goals_doc = goals_ref.get()
            if goals_doc.exists:
                for goal, tasks in goals_doc.to_dict().items():
                    tasks_ref = db.collection("goals").document(str(message.chat.id)).collection("tasks").document(goal)
                    tasks_doc = tasks_ref.get()
                    task_list = tasks_doc.to_dict().get("tasks", []) if tasks_doc.exists else []
                    response += f"\nЦель: {goal}\nЗадачи:\n" + "\n".join(task_list) + "\n"
            else:
                response += "У вас нет добавленных целей."
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Ваш отпуск уже начался или закончился!")
    else:
        bot.send_message(message.chat.id, "Вы еще не указали даты отпуска.")
    main_menu(message)

# Запуск бота
bot.polling(none_stop=True)
