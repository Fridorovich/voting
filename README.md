# SQR Voting System

## Требования
- Python 3.11+
- Poetry
- SQLite (установите сами)

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Fridorovich/voting.git
    ```
2. Установите зависимости:
   ```bash
   poetry install
   ```
3. Создайте файл .env:
    ```txt
    DATABASE_URL=sqlite:///./sqr_voting.db
    SECRET_KEY=your-secret-key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```
4. Примените миграции:
   ```bash
   alembic upgrade head
   ```
5. Запустите сервер:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Документация - ```txt http://127.0.0.1:8000/docs```