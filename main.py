from config import TOKEN
import telebot
from telebot import types
from DB import createDatabase
from DB import funcForTasks as FFT
from suportFuncs import before_create, show_tasks

createDatabase()









markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("записать новый дедлайн")
item2 = types.KeyboardButton("посмотреть мои дедлайны")
item3 = types.KeyboardButton("удалить дедлайн")

markup.add(item1, item2, item3)




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

    if message.text == "записать новый дедлайн":
        msg = bot.send_message(message.chat.id, "введите задание и дедлайн в следуюхем формате: задание|дедлайн")
        bot.register_next_step_handler(msg, before_create, username)

    elif message.text == "посмотреть мои дедлайны":
        msg = bot.send_message(message.chat.id, "введите номер задачи, если хотите посмотреть все задачи, введите: 'все'")
        bot.register_next_step_handler(msg, show_tasks, username, chat_id, bot)

    elif message.text == "удалить дедлайн":
        msg = bot.send_message(message.chat.id, "введите номер задачи, которую нужно удалить")
        bot.register_next_step_handler(msg, FFT.CompletedTask, username)

















bot.infinity_polling()