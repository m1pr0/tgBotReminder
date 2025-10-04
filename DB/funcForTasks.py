import sqlite3
import datetime



def CreateTask(text, deadline, user):

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
    connection.close()



def UpdateTask(task_id, text=None, deadline=None, user=None):
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

    connection.commit()
    print(f"Задача {task_id} успешно обновлена")

    connection.commit()
    connection.close()




def CompletedTask(task_id=None, text="задача была удалена или выполнена", deadline=datetime.datetime.now(), user=None):
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
    connection.close()



