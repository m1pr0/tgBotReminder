import sqlite3
import datetime
from validationFunctions import *


def CreateTask(text, deadline, user):
    connection = None
    try:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO tasks (text, deadline, user)
            VALUES (?, ?, ?)
        ''', (text, deadline, user))

        # Добавляем лог об создании
        new_id = cursor.lastrowid
        log_message = f"create"
        cursor.execute('''
                    INSERT INTO logs (log, task_id)
                    VALUES (?, ?)
                ''', (log_message, new_id))

        connection.commit()
        print(f"Задача {new_id} успешно создана")

        connection.commit()

    except Exception as e:
        print(f"ошибка: {str(e)}")

    finally:
        if connection:
            connection.close()


def wath_tasks(task_number="все", user=None):
    """
    Безопасный просмотр задач
    """
    # ВАЛИДАЦИЯ ВХОДНЫХ ДАННЫХ
    validated_task_number = validate_task_input(task_number)
    if validated_task_number is None:
        return []  # Невалидный ввод - возвращаем пустой список

    connection = None
    try:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        if validated_task_number == "все":
            # Выбираем только незавершенные задачи
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
        else:
            # validated_task_number - ГАРАНТИРОВАННО число или "все"
            cursor.execute('''
                SELECT t.*,
                       CASE 
                         WHEN EXISTS (
                           SELECT 1 FROM logs l 
                           WHERE l.task_id = t.id AND l.log = 'Completed'
                         ) THEN 1 
                         ELSE 0 
                       END as is_completed
                FROM tasks t 
                WHERE t.id = ? AND t.user = ?
            ''', (validated_task_number, user))

        tasks = cursor.fetchall()

        # Преобразуем в список словарей для удобства
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, task)) for task in tasks]

        # Для конкретной задачи проверяем статус завершения
        if validated_task_number != "все":
            if result and result[0].get('is_completed', 0) == 1:
                print(f"Задача {validated_task_number} завершена")
                return []  # Возвращаем пустой список для завершенных задач
            elif result:
                return result  # Возвращаем задачу если она не завершена
            else:
                return []  # Задача не найдена

        return result

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return []  # ⭐ Возвращаем пустой список при ошибке
    finally:
        if connection:
            connection.close()


@validate_task_access
def UpdateTask(task_id, text=None, deadline=None, user=None):
    # Дополнительная проверка на сервере
    if not isinstance(task_id, int):
        raise TypeError("task_id должен быть целым числом")

    connection = None
    try:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        # Сначала проверяем существование задачи
        cursor.execute('SELECT user FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()

        if not task:
            raise ValueError(f"Задача с ID {task_id} не найдена")

        # Проверяем права доступа (двойная проверка)
        if task[0] != user:
            raise PermissionError("Доступ запрещен")

        # Получаем текущие данные
        cursor.execute('SELECT text, deadline FROM tasks WHERE id = ?', (task_id,))
        current_data = cursor.fetchone()

        # Используем текущие значения если новые не переданы
        new_text = text if text is not None else current_data[0]
        new_deadline = deadline if deadline is not None else current_data[1]

        # Выполняем обновление
        cursor.execute('''
            UPDATE tasks 
            SET text = ?, deadline = ?
            WHERE id = ?
        ''', (new_text, new_deadline, task_id))

        # Логируем действие
        log_message = f"update"
        cursor.execute('''
            INSERT INTO logs (log, task_id)
            VALUES (?, ?)
        ''', (log_message, task_id))

        connection.commit()
        print(f"✅ Задача {task_id} успешно обновлена")
        return True

    except (ValueError, PermissionError, TypeError) as e:
        print(f"❌ Ошибка валидации: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Ошибка БД: {str(e)}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()


def CompletedTask(message, user=None):
    connection = None
    try:
        # 1. ВАЛИДАЦИЯ: Извлекаем task_id из message
        if not hasattr(message, 'text') or not message.text:
            print("❌ Не получен текст сообщения")
            return False

        task_id_str = message.text.strip()
        if not task_id_str:
            print("❌ Пустой ввод")
            return False

        # 2. ВАЛИДАЦИЯ: Проверяем, что это число
        if not task_id_str.isdigit():
            print("❌ ID задачи должен быть числом")
            return False

        # 3. ВАЛИДАЦИЯ: Преобразуем и проверяем диапазон
        task_id = int(task_id_str)
        if task_id <= 0 or task_id > 1_000_000:
            print("❌ Некорректный ID задачи")
            return False

        # 4. ВАЛИДАЦИЯ: Проверяем права доступа
        if not task_belongs_to_user(task_id, user):
            print("❌ Доступ к задаче запрещен")
            return False

        # 5. ОСНОВНАЯ ЛОГИКА (после всех проверок)
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        # Проверяем существование задачи
        cursor.execute('SELECT text, deadline, user FROM tasks WHERE id = ?', (task_id,))
        current_data = cursor.fetchone()

        if not current_data:
            print(f"❌ Задача с ID {task_id} не найдена")
            return False

        # Обновляем задачу
        current_text = current_data[0]
        new_text = current_text
        new_deadline = datetime.datetime.now()
        new_user = user if user is not None else current_data[2]

        cursor.execute('''
            UPDATE tasks 
            SET text = ?, deadline = ?, user = ?
            WHERE id = ?
        ''', (new_text, new_deadline, new_user, task_id))

        # Добавляем лог
        log_message = 'Completed'
        cursor.execute('''
            INSERT INTO logs (log, task_id)
            VALUES (?, ?)
        ''', (log_message, task_id))

        connection.commit()
        print(f"✅ Задача {task_id} отмечена как выполненная")
        return True

    except Exception as e:
        print(f"❌ Ошибка при выполнении задачи: {str(e)}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()


def watchCompleted(user):
    connection = None
    try:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        # Ищем задачи, у которых есть лог 'Completed' для указанного пользователя
        cursor.execute('''
            SELECT t.* 
            FROM tasks t
            JOIN logs l ON t.id = l.task_id
            WHERE l.log = ? AND t.user = ?
            ORDER BY t.id
        ''', ('Completed', user))

        tasks = cursor.fetchall()

        # Преобразуем в список словарей для удобства
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, task)) for task in tasks]

        return result

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return []
    finally:
        if connection:
            connection.close()
