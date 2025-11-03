import random
import sqlite3
import datetime
from DB import funcForTasks as FFT
from validationFunctions import *
from config import stickers


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

        # ОТЛАДОЧНАЯ ИНФОРМАЦИЯ
        print(f"🔍 Проверка доступа: task_id={task_id}, user={user}")

        # 6. Проверка прав доступа
        belongs = task_belongs_to_user(task_id, user)
        print(f"🔍 Результат проверки: {belongs}")

        if not belongs:
            # Дополнительная диагностика
            connection = sqlite3.connect('my_database.db')
            cursor = connection.cursor()
            cursor.execute('SELECT id, user FROM tasks WHERE id = ?', (task_id,))
            task_info = cursor.fetchone()
            connection.close()

            if task_info:
                print(f"🔍 Задача найдена: id={task_info[0]}, user={task_info[1]}")
            else:
                print(f"🔍 Задача с ID {task_id} не найдена в БД")

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


def randomStic(bot, chat_id):
    stickerPull = stickers
    random_sticker = random.choice(stickerPull)
    bot.send_sticker(chat_id, random_sticker)


# Возвращает список актуальных задач пользователя (задачи без статуса 'Completed' в logs)
def actual_tasks(user):
    connection = None
    try:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        # Выбираем только незавершенные задачи пользователя
        cursor.execute('''
            SELECT t.* 
            FROM tasks t
            WHERE t.user = ? 
            AND t.id NOT IN (
                SELECT DISTINCT task_id 
                FROM logs 
                WHERE log = 'Completed'
            )
            ORDER BY t.id
        ''', (user,))

        tasks = cursor.fetchall()

        # Преобразуем в список словарей для удобства
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, task)) for task in tasks]

        return result

    except Exception as e:
        print(f"❌ Ошибка получения актуальных задач: {str(e)}")
        return []  # Возвращаем пустой список при ошибке
    finally:
        if connection:
            connection.close()
