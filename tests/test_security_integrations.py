#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграций безопасности
"""

import asyncio
import sys
import pytest
from pathlib import Path

# Добавляем корень проекта в sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.security_integrations import SecurityIntegrations

@pytest.mark.asyncio
async def test_security_integrations():
    """Тестирование интеграций безопасности"""
    print("🔒 Тестирование интеграций безопасности...")
    
    async with SecurityIntegrations() as si:
        # 1. Проверяем информацию о системе
        print("\n📊 Информация о системе:")
        system_info = si.get_system_info()
        print(f"  ОС: {system_info['os']}")
        print(f"  Root: {system_info['is_root']}")
        print(f"  Контейнер: {system_info['is_container']}")
        print(f"  Доступные инструменты: {system_info['available_tools']}")
        
        # 2. Тестируем nmap
        print("\n🔍 Тестирование Nmap:")
        nmap_result = await si.nmap_scan("localhost", "quick")
        print(f"  Результат: {nmap_result}")
        
        # 3. Тестируем OpenSSL
        print("\n🔐 Тестирование OpenSSL:")
        openssl_result = await si.openssl_scan("google.com", 443)
        print(f"  Результат: {openssl_result}")
        
        # 4. Тестируем комплексный аудит
        print("\n🔍 Комплексный аудит:")
        audit_result = await si.comprehensive_audit("localhost")
        print(f"  Результат: {audit_result}")

if __name__ == "__main__":
    asyncio.run(test_security_integrations()) 