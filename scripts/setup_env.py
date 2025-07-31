#!/usr/bin/env python3
"""
Скрипт для настройки .env файла с чувствительными данными SwiftDevBot
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Создает .env файл с шаблоном чувствительных данных"""
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        print(f"⚠️  Файл {env_file} уже существует!")
        response = input("Хотите перезаписать его? (y/N): ").lower()
        if response != 'y':
            print("Операция отменена.")
            return
    
    # Запрашиваем данные у пользователя
    print("🔐 Настройка чувствительных данных SwiftDevBot")
    print("=" * 50)
    
    bot_token = input("Введите токен Telegram бота: ").strip()
    if not bot_token:
        print("❌ Токен бота обязателен!")
        return
    
    super_admin_ids = input("Введите Telegram ID супер-администраторов (через запятую): ").strip()
    if not super_admin_ids:
        print("❌ ID супер-администраторов обязательны!")
        return
    
    # Дополнительные настройки (опционально)
    print("\n📝 Дополнительные настройки (можно оставить пустыми):")
    
    db_pg_dsn = input("PostgreSQL DSN (если используете): ").strip()
    db_mysql_dsn = input("MySQL DSN (если используете): ").strip()
    redis_url = input("Redis URL (если используете Redis кэш): ").strip()
    web_external_host = input("Внешний хост веб-сервера: ").strip()
    web_external_port = input("Внешний порт веб-сервера: ").strip()
    
    # Создаем содержимое .env файла
    env_content = f"""# .env - Чувствительные данные SwiftDevBot
# ⚠️ НЕ КОММИТЬТЕ ЭТОТ ФАЙЛ В GIT!

# Telegram Bot Token (обязательно)
BOT_TOKEN={bot_token}

# Супер-администраторы (Telegram ID через запятую)
SUPER_ADMIN_IDS={super_admin_ids}

# База данных (опционально, если не используете SQLite)
"""
    
    if db_pg_dsn:
        env_content += f"DB_PG_DSN={db_pg_dsn}\n"
    else:
        env_content += "# DB_PG_DSN=postgresql://user:password@localhost:5432/swiftdevbot\n"
    
    if db_mysql_dsn:
        env_content += f"DB_MYSQL_DSN={db_mysql_dsn}\n"
    else:
        env_content += "# DB_MYSQL_DSN=mysql://user:password@localhost:3306/swiftdevbot\n"
    
    env_content += "\n# Redis (опционально, если используете Redis кэш)\n"
    if redis_url:
        env_content += f"REDIS_URL={redis_url}\n"
    else:
        env_content += "# REDIS_URL=redis://localhost:6379/0\n"
    
    env_content += "\n# Веб-сервер (опционально)\n"
    if web_external_host:
        env_content += f"WEB_SERVER_EXTERNAL_HOST={web_external_host}\n"
    else:
        env_content += "# WEB_SERVER_EXTERNAL_HOST=your-domain.com\n"
    
    if web_external_port:
        env_content += f"WEB_SERVER_EXTERNAL_PORT={web_external_port}\n"
    else:
        env_content += "# WEB_SERVER_EXTERNAL_PORT=8080\n"
    
    env_content += """
# Дополнительные токены для интеграций (опционально)
# YOUTUBE_API_KEY=your_youtube_api_key
# OPENAI_API_KEY=your_openai_api_key
"""
    
    # Записываем файл
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"\n✅ Файл {env_file} успешно создан!")
        print("🔒 Чувствительные данные сохранены в .env файле")
        print("📝 Теперь вы можете настроить остальные параметры в config.yaml")
        
    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}")
        return

def main():
    """Главная функция"""
    print("🚀 SwiftDevBot - Настройка чувствительных данных")
    print("=" * 50)
    
    create_env_file()

if __name__ == "__main__":
    main() 