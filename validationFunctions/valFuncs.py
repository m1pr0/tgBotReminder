import sqlite3
from functools import wraps


# Валидирует ввод для номера задачи Возвращает: число (int) или "все", или None если невалидный ввод
def validate_task_input(task_input):
    if not task_input or not isinstance(task_input, (str, int)):
        return None

    # Если это специальное ключевое слово
    if isinstance(task_input, str) and task_input.lower() in ['все', 'dct']:
        return "все"

    # Пытаемся преобразовать в число
    try:
        if isinstance(task_input, str):
            # Убираем пробелы и проверяем, что это цифры
            cleaned = task_input.strip()
            if not cleaned.isdigit():
                return None

            task_id = int(cleaned)
        else:
            task_id = int(task_input)

        # Проверяем диапазон
        if 1 <= task_id <= 1_000_000:
            return task_id
        else:
            return None

    except (ValueError, TypeError):
        return None

    # требует пояснения !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def validate_task_access(func):
    @wraps(func)
    def wrapper(task_id, *args, **kwargs):
        # Проверяем тип task_id
        if not isinstance(task_id, int):
            raise TypeError("ID задачи должен быть числом")

        # Проверяем диапазон
        if task_id <= 0 or task_id > 1_000_000:
            raise ValueError("Некорректный ID задачи")

        # Получаем username из аргументов
        username = kwargs.get('user') or args[0] if args else None

        if username and not task_belongs_to_user(task_id, username):
            raise PermissionError("Доступ к задаче запрещен")

        return func(task_id, *args, **kwargs)

    return wrapper

def task_belongs_to_user(task_id, username):
    if not isinstance(task_id, int):
        return False

    connection = None
    try:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        cursor.execute(
            'SELECT user FROM tasks WHERE id = ?',
            (task_id,)
        )

        result = cursor.fetchone()
        return result is not None and result[0] == username

    except Exception as e:
        print(f"Ошибка проверки прав доступа: {e}")
        return False
    finally:
        if connection:
            connection.close()

