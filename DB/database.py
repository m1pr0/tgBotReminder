import sqlite3

def createDatabase():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT(200) NOT NULL,
                deadline TEXT NOT NULL,
                user TEXT NOT NULL
            )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log TEXT NOT NULL,
            task_id INTEGER NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    ''')

    connection.commit()  # Сохраняем изменения
    connection.close()