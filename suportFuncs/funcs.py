# import telebot
import random
import sqlite3
import datetime
from DB import funcForTasks as FFT


# функция нужна в молмент создания задания для обработки сообщения пользователя
# (вся информация передана в одном сообщении) и использования  register_next_step_handler
def before_create(message, user):
    try:
        task = message.text.split("|")[0].strip()
        deadline = message.text.split("|")[1].strip()
        FFT.CreateTask(task, deadline, user)

    except Exception as e:
        print(f"ошибка: {str(e)}")



# тоже самое что и before_create только для обновления задачи
def before_update(message, user):
    try:
        task_id = message.text.split("|")[0].strip()
        task = message.text.split("|")[1].strip()
        deadline = message.text.split("|")[2].strip()
        FFT.UpdateTask(task_id, task, deadline, user)

    except Exception as e:
        print(f"ошибка: {str(e)}")



# функция для подсчета количества записей в таблице tasks по пользователю
def tasks_count(username):
    with sqlite3.connect('my_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE user = ?', (username,))
        return cursor.fetchone()[0]


# функция нужна для вывода данных, которые возвращает wath_tasks
def show_tasks(message, user, chat_id, bot):
    task_number = message.text.strip()

    # Преобразуем в число, если это не "все"
    if task_number.lower() not in ['все', "ВСЕ", "Все", "dct", "Dct", "DCT"]:
        try:
            task_number = int(task_number)
        except ValueError:
            bot.send_message(chat_id, "Пожалуйста, введите число или 'все'")
            return

    tasks = FFT.wath_tasks(task_number, user)

    if not tasks:
        bot.send_message(chat_id, "Задачи не найдены")
        return

    for task in tasks:
        if task['text'][0] != '*':
            bot.send_message(chat_id, f"ID: {task['id']}\nЗадание: {task['text']}\nДедлайн: {task['deadline']}")


# просто функция для вывода сообщений, скорее всего будет использоваться для вывода ошибок
def botMes(bot, chat_id, message):
    bot.send_message(chat_id, str(datetime.datetime.now()) + ',' + message)



def randomStic(bot, chat_id):
    stickerPull = ["CAACAgQAAxkBAAETVxho-UxSImgVGwWD-tneI0wo3HGI5AAC9A4AAqbxcR70SZSRrqM8yDYE",
                   "CAACAgQAAxkBAAETVxpo-Ux8S7QrcS5m0OOaeOJ3HDnQ3AACIA8AAqbxcR6lYs4uCYaxhTYE",
                   "CAACAgQAAxkBAAETVxxo-UyTyXDyPBvIyP4HMxDfDlVkRQACBhYAAqbxcR4lN_xMd39fmTYE",
                   "CAACAgQAAxkBAAETVx5o-Uyl7X8GA-hH3xno3texusHVJwACDA8AAqbxcR4C181RIl_-BDYE",
                   "CAACAgQAAxkBAAETVyBo-Uy0_OhdfJDkrBpZUhDRaGwczQACEw8AAqbxcR6ep3Xwe2oHejYE"]
    random_sticker = random.choice(stickerPull)
    bot.send_sticker(chat_id, random_sticker)


# функция для оправки сообщения изходя из лога в таблице logs
# def statusByLog():
