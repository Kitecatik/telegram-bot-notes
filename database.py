import asyncpg
from config import DB_USER, DB_PASS, DB_HOST, DB_NAME

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            host=DB_HOST
        )
        await self.create_tables()

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    text TEXT NOT NULL
                )
            ''')

    # CREATE: Создать заметку
    async def add_note(self, user_id: int, text: str):
        async with self.pool.acquire() as conn:
            await conn.execute('INSERT INTO notes (user_id, text) VALUES ($1, $2)', user_id, text)

    # READ: Получить все заметки пользователя
    async def get_notes(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetch('SELECT id, text FROM notes WHERE user_id = $1 ORDER BY id ASC', user_id)

    # UPDATE: Обновить заметку
    async def update_note(self, note_id: int, user_id: int, text: str):
        async with self.pool.acquire() as conn:
            await conn.execute('UPDATE notes SET text = $1 WHERE id = $2 AND user_id = $3', text, note_id, user_id)

    # DELETE: Удалить заметку
    async def delete_note(self, note_id: int, user_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM notes WHERE id = $1 AND user_id = $2', note_id, user_id)

# Создаем глобальный объект БД
db = Database()