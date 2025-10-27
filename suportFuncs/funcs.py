# import telebot
import random
import sqlite3
import datetime
from DB import funcForTasks as FFT
from validationFunctions import *


# функция нужна в момент создания задания для обработки сообщения пользователя
# (вся информация передана в одном сообщении) и использования register_next_step_handler
def before_create(message, user):
    try:
        task = message.text.split("|")[0].strip()
        deadline = message.text.split("|")[1].strip()
        FFT.CreateTask(task, deadline, user)

    except Exception as e:
        print(f"ошибка: {str(e)}")


# то же самое, что и before_create только для обновления задачи
@validate_task_access
def before_update(message, user):
    try:
        # 1. Проверка формата
        parts = message.text.split("|")
        if len(parts) != 3:
            raise ValueError("❌ Неверный формат. Используйте: номер|задача|дедлайн")

        # 2. Валидация ID задачи (самое важное!)
        task_id_str = parts[0].strip()
        if not task_id_str.isdigit():
            raise ValueError("❌ ID задачи должен быть числом")

        task_id = int(task_id_str)  # Преобразуем в int

        # 3. Дополнительные проверки
        if task_id <= 0:
            raise ValueError("❌ ID задачи должен быть положительным числом")
        if task_id > 1_000_000:  # Разумный предел
            raise ValueError("❌ Слишком большой ID задачи")

        # 4. Валидация текста задачи
        task_text = parts[1].strip()
        if not task_text:
            raise ValueError("❌ Текст задачи не может быть пустым")
        if len(task_text) > 200:
            raise ValueError("❌ Текст задачи слишком длинный")

        # 5. Валидация дедлайна
        deadline = parts[2].strip()
        if not deadline:
            raise ValueError("❌ Дедлайн не может быть пустым")

        # 6. Проверка прав доступа
        if not task_belongs_to_user(task_id, user):
            raise PermissionError("❌ У вас нет прав на эту задачу")

        # 7. Только теперь выполняем операцию
        success = FFT.UpdateTask(task_id, task_text, deadline, user)

        if success:
            print("✅ Задача обновлена")
        else:
            print("❌ Ошибка при обновлении задачи")

    except ValueError as e:
        print(str(e))
    except PermissionError as e:
        print(str(e))
    except Exception as e:
        print(f"Ошибка в safe_before_update: {e}")


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
