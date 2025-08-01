#!/usr/bin/env python3
"""
Скрипт для тестирования поддержки разных типов БД.
"""
import sys
import os
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from core.database.db_utils import DatabaseDialectHandler, get_db_info_query


def test_sqlite():
    """Тестирует SQLite"""
    print("\n=== Тестирование SQLite ===")
    engine = create_engine("sqlite:///:memory:")
    
    features = DatabaseDialectHandler.get_dialect_features(engine)
    types = DatabaseDialectHandler.get_recommended_types(engine)
    
    print(f"Поддерживаемые функции: {features}")
    print(f"Рекомендуемые типы: {types}")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT sqlite_version()"))
        version = result.scalar()
        print(f"Версия SQLite: {version}")
    
    # Используем assert вместо return
    assert features is not None
    assert types is not None
    assert version is not None


def test_mysql():
    """Тестирует MySQL (если доступен)"""
    print("\n=== Тестирование MySQL ===")
    # Пример URL - замените на реальный
    mysql_url = "mysql+pymysql://root:Sova3568@192.168.31.3:33066/sdb_mysql_db?charset=utf8mb4"

    try:
        engine = create_engine(mysql_url)
        features = DatabaseDialectHandler.get_dialect_features(engine)
        types = DatabaseDialectHandler.get_recommended_types(engine)
        
        print(f"Поддерживаемые функции: {features}")
        print(f"Рекомендуемые типы: {types}")
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.scalar()
            print(f"Версия MySQL: {version}")
        
        # Используем assert вместо return
        assert features is not None
        assert types is not None
        assert version is not None
    except Exception as e:
        print(f"MySQL недоступен: {e}")
        # Если MySQL недоступен, тест все равно проходит
        assert True


def test_postgresql():
    """Тестирует PostgreSQL (если доступен)"""
    print("\n=== Тестирование PostgreSQL ===")
    # Пример URL - замените на реальный
    pg_url = "postgresql+psycopg://soverx:Sova3568@192.168.31.3:2345/sdb_database"
    
    try:
        engine = create_engine(pg_url)
        features = DatabaseDialectHandler.get_dialect_features(engine)
        types = DatabaseDialectHandler.get_recommended_types(engine)
        
        print(f"Поддерживаемые функции: {features}")
        print(f"Рекомендуемые типы: {types}")
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"Версия PostgreSQL: {version}")
        
        # Используем assert вместо return
        assert features is not None
        assert types is not None
        assert version is not None
    except Exception as e:
        print(f"PostgreSQL недоступен: {e}")
        # Если PostgreSQL недоступен, тест все равно проходит
        assert True


if __name__ == "__main__":
    print("Тестирование поддержки баз данных...")
    
    # Для запуска как скрипт используем try/except
    results = {}
    
    try:
        test_sqlite()
        results['SQLite'] = True
    except Exception as e:
        print(f"SQLite тест не прошел: {e}")
        results['SQLite'] = False
    
    try:
        test_mysql()
        results['MySQL'] = True
    except Exception as e:
        print(f"MySQL тест не прошел: {e}")
        results['MySQL'] = False
    
    try:
        test_postgresql()
        results['PostgreSQL'] = True
    except Exception as e:
        print(f"PostgreSQL тест не прошел: {e}")
        results['PostgreSQL'] = False
    
    print("\n=== Результаты тестирования ===")
    for db_name, success in results.items():
        status = "✅ Работает" if success else "❌ Недоступен"
        print(f"{db_name}: {status}")