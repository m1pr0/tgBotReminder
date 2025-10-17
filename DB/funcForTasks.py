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
        log_message = f"Задача создана"
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

        if task_number == "все":
            cursor.execute('SELECT * FROM tasks WHERE user = ? ORDER BY id', (user,))
        else:
            cursor.execute('SELECT * FROM tasks WHERE id = ? AND user = ?', (task_number, user))

        tasks = cursor.fetchall()

        # Преобразуем в список словарей для удобства
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, task)) for task in tasks]

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
        log_message = f"Задача обновлена: текст='{new_text}', дедлайн='{new_deadline}', пользователь='{new_user}'"
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
        text = "задача была удалена или выполнена"
        deadline = datetime.datetime.now()

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
            connection.rollback()  # Откатываем изменения при ошибке
        return False
    finally:
        if connection:
            connection.close()
    return True


