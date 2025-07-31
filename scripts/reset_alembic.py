#!/usr/bin/env python3
"""
Скрипт для очистки состояния Alembic в MySQL базе данных.
Читает параметры подключения из переменной окружения SDB_DB_MYSQL_DSN.
"""
import asyncio
import os
import sys
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Добавляем корень проекта в путь, чтобы можно было импортировать python-dotenv, если он в venv
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    import aiomysql
    from dotenv import load_dotenv, find_dotenv
except ImportError as e:
    print(f"✗ Ошибка импорта необходимых библиотек: {e}")
    print("Пожалуйста, установите aiomysql и python-dotenv: pip install aiomysql python-dotenv")
    sys.exit(1)

# Загрузка переменных окружения из .env файла
env_file = find_dotenv(filename=".env", usecwd=True, raise_error_if_not_found=False)
if env_file:
    print(f"ℹ️ Загрузка переменных окружения из: {env_file}")
    load_dotenv(env_file)
else:
    print("⚠️  .env файл не найден. Скрипт будет полагаться на системные переменные окружения.")

async def reset_alembic_state():
    """Очищает таблицу alembic_version из MySQL"""
    
    mysql_dsn = os.getenv("SDB_DB_MYSQL_DSN")
    
    if not mysql_dsn:
        print("✗ Ошибка: Переменная окружения SDB_DB_MYSQL_DSN не установлена.")
        print("  Пожалуйста, установите ее в вашем .env файле или системных переменных.")
        print("  Пример: SDB_DB_MYSQL_DSN=\"mysql+aiomysql://user:pass@host:port/dbname?charset=utf8mb4\"")
        return

    print(f"ℹ️ Используется DSN из SDB_DB_MYSQL_DSN: mysql+aiomysql://<user>:<pass>@<host>:<port>/<dbname>...")

    try:
        # Парсинг DSN для aiomysql.connect, так как он не всегда принимает DSN напрямую
        # (хотя SQLAlchemy create_engine его парсит).
        # Формат DSN для SQLAlchemy: mysql+driver://user:password@host:port/database?params
        # Нам нужно извлечь user, password, host, port, database.
        
        # Убираем схему и драйвер, если они есть, для urlparse
        parsed_url_str = mysql_dsn
        if parsed_url_str.startswith("mysql+aiomysql://"):
            parsed_url_str = parsed_url_str[len("mysql+aiomysql://"):]
        elif parsed_url_str.startswith("mysql://"): # На случай, если кто-то укажет без драйвера
             parsed_url_str = parsed_url_str[len("mysql://"):]

        # Добавляем временную схему, если ее нет, чтобы urlparse корректно работал
        if "://" not in parsed_url_str:
            parsed_url_str = f"temp://{parsed_url_str}"

        parsed_url = urlparse(parsed_url_str)
        
        db_user = parsed_url.username
        db_password = parsed_url.password
        db_host = parsed_url.hostname
        db_port = parsed_url.port or 3306 # Стандартный порт MySQL
        db_name = parsed_url.path.lstrip('/') if parsed_url.path else None
        
        query_params = parse_qs(parsed_url.query)
        db_charset = query_params.get('charset', ['utf8mb4'])[0] # Дефолт utf8mb4

        if not all([db_user, db_host, db_name]):
            print("✗ Ошибка: Не удалось корректно распарсить DSN. Убедитесь, что он содержит user, host и имя базы данных.")
            print(f"  Распарсено: user='{db_user}', host='{db_host}', port='{db_port}', dbname='{db_name}'")
            return

        connection_params = {
            'host': db_host,
            'port': int(db_port),
            'user': db_user,
            'db': db_name,
            'charset': db_charset
        }
        if db_password: # Пароль может отсутствовать
            connection_params['password'] = db_password
        
        print(f"ℹ️ Подключение к MySQL: host={db_host}, port={db_port}, user={db_user}, db={db_name}, charset={db_charset}")

        connection = await aiomysql.connect(**connection_params) # type: ignore
        
        async with connection.cursor() as cursor:
            # Удаляем таблицу alembic_version если она существует
            await cursor.execute("DROP TABLE IF EXISTS alembic_version")
            print("✓ Таблица alembic_version удалена из MySQL.")
            
        # await connection.commit() # DROP TABLE обычно автокоммитится в MySQL, но для явности можно оставить
        connection.close()
        print("✓ Состояние Alembic для MySQL сброшено.")
        
    except aiomysql.Error as e_mysql: # Ловим специфичные ошибки aiomysql
        print(f"✗ Ошибка aiomysql: Код {e_mysql.args[0]}, Сообщение: {e_mysql.args[1] if len(e_mysql.args) > 1 else str(e_mysql)}")
    except Exception as e:
        print(f"✗ Непредвиденная ошибка при сбросе состояния MySQL: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(reset_alembic_state())