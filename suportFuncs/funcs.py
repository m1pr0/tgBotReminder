import telebot
import sqlite3



from DB import funcForTasks as FFT







#функция нужна в молмент создания задания для обработки сообщения пользователя
# (вся информация передана в одном сообщении) и использования  register_next_step_handler
def before_create(message, user):

    try:

        task = message.text.split("|")[0].strip()
        deadline = message.text.split("|")[1].strip()
        FFT.CreateTask(task, deadline, user)

    except Exception as e:
        print(f"ошибка: {str(e)}")



# функция для подсчета количества записей в таблице tasks по пользователю
def tasks_count(username):
    with sqlite3.connect('my_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE user = ?', (username,))
        return cursor.fetchone()[0]




#функция нужна для вывода данных, которые возвращает wath_tasks
def show_tasks(task_number, user, chat_id, bot):

    tasks = FFT.wath_tasks(task_number, user)

    for task in tasks:
        bot.send_message(chat_id, f"{task['id']}: {task['text']} (до {task['deadline']})")




