import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

usuarios = [
    ('rafael.faggin', '123456'),
    ('eduardo.mendes', '123456'),
    ('marcus.menezes', '123456'),
]

for username, senha in usuarios:
    hash = generate_password_hash(senha)
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hash))

conn.commit()
conn.close()
print('Usuários criados!')