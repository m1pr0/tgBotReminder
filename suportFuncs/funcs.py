from DB import funcForTasks as FFT







#функция нужна в молмент создания задания для обработки сообщения пользователя
# (вся информация передана в одном сообщении) и использования  register_next_step_handler
def before_create(message, user):

    try:

        task = message.text.split("|")[0].strip()
        deadline = message.text.split("|")[1].strip()

        if "|" not in message:
            return "вы не правильно ввели задание и дедлайе, используйте: задание|деддайн"

        elif task != "" and deadline != "":
            return "вы не ввели ничего(("

        else:
            FFT.CreateTask(task, deadline, user)

    except Exception as e:
        return f"ошибка: {str(e)}"