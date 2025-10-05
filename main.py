from config import TOKEN
import telebot
from telebot import types
from DB import createDatabase
from DB import funcForTasks as FFT

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
    if message.text == "записать новый дедлайн":







bot.infinity_polling()