import telebot
from telebot import types

from DB import createDatabase
from DB import funcForTasks as FFT
from config import TOKEN
from suportFuncs import before_create, show_tasks, before_update, randomStic, actual_tasks

createDatabase()

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [
    "📝 Новая задача",
    "✏️ Обновить",
    "👀 Мои задачи",
    "✅ Завершить",
    "📋 Завершенные"
]
markup.add(*buttons)

API_TOKEN = TOKEN

bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'салам погнали', parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def working(message):
    username = message.from_user.username
    chat_id = message.chat.id

    if message.text == "📝 Новая задача":
        msg = bot.send_message(message.chat.id, "введите задание и дедлайн в следуюхем формате: задание|дедлайн")
        bot.register_next_step_handler(msg, before_create, username)
        randomStic(bot, chat_id)
        # bot.send_message(message.chat.id, f"задача создана")

    elif message.text == "✏️ Обновить":
        msg = bot.send_message(message.chat.id,
                               "введите обновленное задание и дедлайн в следуюхем формате: номер задачи|задание|дедлайн")
        bot.register_next_step_handler(msg, before_update, username)
        randomStic(bot, chat_id)
        # bot.send_message(message.chat.id, f"задача обновлена")


    elif message.text == "👀 Мои задачи":
        tasks = [x["id"] for x in actual_tasks(username)]
        msg = bot.send_message(message.chat.id,f"введите номер задачи, если хотите посмотреть все задачи, введите: 'все'\n\nактуальные задачи: {tasks}")
        bot.register_next_step_handler(msg, show_tasks, username, chat_id, bot)
        randomStic(bot, chat_id)


    elif message.text == "✅ Завершить":
        msg = bot.send_message(message.chat.id, "введите номер задачи, которую нужно завершить")
        bot.register_next_step_handler(msg, FFT.CompletedTask, username)
        randomStic(bot, chat_id)

    elif message.text == "📋 Завершенные":
        comTasks = FFT.watchCompleted(username)
        for task in comTasks:
            task_info = f"ID: {task['id']}\nТекст: {task['text']}\nДедлайн: {task['deadline']}"
            bot.send_message(message.chat.id, task_info)
        randomStic(bot, chat_id)


bot.infinity_polling()
