import sqlite3
import datetime


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
    connection = None
    try:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        if task_number.lower() == "все" or task_number.lower() == "dct":
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
            # Проверяем конкретную задачу и ее статус
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
            ''', (task_number, user))

        tasks = cursor.fetchall()

        # Преобразуем в список словарей для удобства
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, task)) for task in tasks]

        # Для конкретной задачи проверяем статус завершения
        if task_number.lower() != "все" and task_number.lower() != "dct":
            if result and result[0].get('is_completed', 0) == 1:
                print(f"Задача {task_number} завершена")
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


def UpdateTask(task_id, text=None, deadline=None, user=None):
    connection = None
    try:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        cursor.execute('SELECT text, deadline, user FROM tasks WHERE id = ?', (task_id,))
        current_data = cursor.fetchone()

        if not current_data:
            raise ValueError(f"Задача с ID {task_id} не найдена")

        # Используем текущие значения если новые не переданы
        new_text = text if text is not None else current_data[0]
        new_deadline = deadline if deadline is not None else current_data[1]
        new_user = user if user is not None else current_data[2]

        cursor.execute('''
                UPDATE tasks 
                SET text = ?, deadline = ?, user = ?
                WHERE id = ?
            ''', (new_text, new_deadline, new_user, task_id))

        # Добавляем лог об обновлении
        log_message = f"update {datetime.datetime.now()}"
        cursor.execute('''
                    INSERT INTO logs (log, task_id)
                    VALUES (?, ?)
                ''', (log_message, task_id))

        print(f"Задача {task_id} успешно обновлена")

        connection.commit()


    except Exception as e:
        print(f"ошибка: {str(e)}")

    finally:
        if connection:
            connection.close()


def CompletedTask(message, user=None):
    connection = None
    try:
        task_id = int(message.text.strip())

        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        cursor.execute('SELECT text, deadline, user FROM tasks WHERE id = ?', (task_id,))
        current_data = cursor.fetchone()

        if not current_data:
            raise ValueError(f"Задача с ID {task_id} не найдена")

        # Добавляем "***" по краям текущего текста вместо замены
        current_text = current_data[0]
        new_text = current_text
        new_deadline = datetime.datetime.now()
        new_user = user if user is not None else current_data[2]

        cursor.execute('''
            UPDATE tasks 
            SET text = ?, deadline = ?, user = ?
            WHERE id = ?
        ''', (new_text, new_deadline, new_user, task_id))

        log_message = 'Completed'
        cursor.execute('''
            INSERT INTO logs (log, task_id)
            VALUES (?, ?)
        ''', (log_message, task_id))

        connection.commit()
        print(f"Задача {task_id} отмечена как выполненная")

    except ValueError as e:
        print(f"Ошибка валидации: {str(e)}")
        return False
    except Exception as e:
        print(f"Ошибка при выполнении задачи: {str(e)}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()
    return True


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
