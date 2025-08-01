"""
Pytest configuration and fixtures for SwiftDevBot-Lite tests
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio
from typer.testing import CliRunner

# Добавляем корень проекта в sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импортируем основные модули для тестирования
try:
    from cli.monitor import monitor_app
    from cli.utils import utils_app
    from cli.config import config_app
    from cli.db import db_app
    from cli.module import module_app
    from cli.user import user_app
    from cli.backup import backup_app
    from cli.system import system_app
    from cli.bot import bot_app
    from cli.run import run_command
    from cli.process import stop_command, status_command, restart_command
except ImportError as e:
    print(f"Warning: Could not import CLI modules: {e}")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def cli_runner():
    """Fixture for CLI testing with Typer."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_config():
    """Test configuration data."""
    return {
        "bot": {
            "token": "test_token_123456789",
            "webhook_url": "https://example.com/webhook",
            "polling": True
        },
        "database": {
            "type": "sqlite",
            "path": ":memory:"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    mock_settings = Mock()
    mock_settings.bot.token = "test_token"
    mock_settings.bot.webhook_url = "https://example.com/webhook"
    mock_settings.database.type = "sqlite"
    mock_settings.database.path = ":memory:"
    mock_settings.logging.level = "INFO"
    return mock_settings


@pytest.fixture
def mock_db_manager():
    """Mock database manager for testing."""
    mock_db = Mock()
    mock_db.is_connected.return_value = True
    mock_db.get_database_size.return_value = 1024 * 1024  # 1MB
    mock_db.get_tables_count.return_value = 10
    mock_db.get_database_path.return_value = "/test/path/db.sqlite"
    return mock_db


@pytest.fixture
def mock_services():
    """Mock services for testing."""
    services = {
        "settings": Mock(),
        "db_manager": Mock(),
        "rbac_service": Mock()
    }
    return services


@pytest.fixture
def test_file_content():
    """Test file content for file operations."""
    return {
        "json": '{"name": "test", "value": 123, "items": ["a", "b", "c"]}',
        "yaml": "name: test\nvalue: 123\nitems:\n  - a\n  - b\n  - c",
        "csv": "name,value,type\ntest,123,string\nsample,456,number",
        "xml": """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <name>test</name>
    <value>123</value>
    <items>
        <item>a</item>
        <item>b</item>
        <item>c</item>
    </items>
</root>"""
    }


@pytest.fixture
def test_encryption_data():
    """Test data for encryption/decryption tests."""
    return {
        "plaintext": "This is a secret message for testing encryption",
        "password": "test_password_123",
        "algorithm": "aes"
    }


@pytest.fixture
def mock_system_info():
    """Mock system information for testing."""
    return {
        "platform": "Linux",
        "platform_version": "5.15.0",
        "architecture": "64bit",
        "processor": "x86_64",
        "hostname": "test-host",
        "python_version": "3.12.3"
    }


@pytest.fixture
def mock_cpu_info():
    """Mock CPU information for testing."""
    return {
        "percent": 25.5,
        "count": 4,
        "frequency": 2400.0,
        "load_avg": [1.2, 0.8, 0.5]
    }


@pytest.fixture
def mock_memory_info():
    """Mock memory information for testing."""
    return {
        "total": 8589934592,  # 8GB
        "available": 4294967296,  # 4GB
        "used": 4294967296,  # 4GB
        "percent": 50.0,
        "swap_total": 2147483648,  # 2GB
        "swap_used": 1073741824,  # 1GB
        "swap_percent": 50.0
    }


@pytest.fixture
def mock_disk_info():
    """Mock disk information for testing."""
    return {
        "total": 107374182400,  # 100GB
        "used": 21474836480,  # 20GB
        "free": 85899345920,  # 80GB
        "percent": 20.0,
        "read_bytes": 1073741824,  # 1GB
        "write_bytes": 2147483648  # 2GB
    }


@pytest.fixture
def mock_network_info():
    """Mock network information for testing."""
    return {
        "bytes_sent": 1073741824,  # 1GB
        "bytes_recv": 2147483648,  # 2GB
        "packets_sent": 1000000,
        "packets_recv": 2000000
    }


@pytest.fixture
def mock_bot_status():
    """Mock bot status for testing."""
    return {
        "status": "running",
        "uptime": 3600,  # 1 hour
        "messages_processed": 1000,
        "users_active": 50,
        "errors_count": 5
    }


@pytest.fixture
def mock_database_status():
    """Mock database status for testing."""
    return {
        "status": "connected",
        "type": "sqlite",
        "size": 1048576,  # 1MB
        "path": "/test/path/database.db",
        "tables_count": 10,
        "connections": 5
    }


@pytest.fixture
def mock_alert_data():
    """Mock alert data for testing."""
    return {
        "alerts": [
            {
                "id": 1,
                "type": "warning",
                "message": "High CPU usage",
                "timestamp": "2024-01-15T10:30:00Z",
                "resolved": False
            },
            {
                "id": 2,
                "type": "critical",
                "message": "Database connection failed",
                "timestamp": "2024-01-15T10:25:00Z",
                "resolved": True
            }
        ],
        "rules": [
            {
                "id": 1,
                "name": "CPU Alert",
                "condition": "cpu > 80",
                "action": "email",
                "enabled": True
            }
        ]
    }


@pytest.fixture
def mock_log_data():
    """Mock log data for testing."""
    return {
        "logs": [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "level": "INFO",
                "message": "Bot started successfully",
                "module": "bot"
            },
            {
                "timestamp": "2024-01-15T10:29:00Z",
                "level": "ERROR",
                "message": "Database connection failed",
                "module": "database"
            }
        ],
        "statistics": {
            "total": 1000,
            "errors": 10,
            "warnings": 50,
            "info": 940
        }
    }


@pytest.fixture
def mock_performance_data():
    """Mock performance data for testing."""
    return {
        "slow_queries": [
            {
                "query": "SELECT * FROM messages WHERE user_id = ?",
                "duration": 2.5,
                "count": 5
            }
        ],
        "response_times": {
            "average": 120,
            "p95": 450,
            "p99": 1200,
            "max": 2800
        },
        "memory_usage": {
            "current": 512,
            "peak": 1024,
            "leaks_detected": False
        }
    }


@pytest.fixture
def mock_report_data():
    """Mock report data for testing."""
    return {
        "period": "daily",
        "metrics": {
            "cpu_avg": 25.5,
            "memory_avg": 50.0,
            "disk_usage": 20.0,
            "requests_total": 10000,
            "errors_total": 100
        },
        "recommendations": [
            "Optimize database queries",
            "Increase memory allocation",
            "Monitor disk usage"
        ]
    }


@pytest.fixture
def mock_integration_data():
    """Mock integration data for testing."""
    return {
        "prometheus": {
            "enabled": True,
            "endpoint": "localhost:9090",
            "metrics_exported": 50
        },
        "grafana": {
            "enabled": True,
            "dashboard_url": "http://localhost:3000",
            "alerts_configured": 10
        },
        "datadog": {
            "enabled": False,
            "api_key": None,
            "metrics_sent": 0
        }
    }


@pytest.fixture
def mock_diagnostic_data():
    """Mock diagnostic data for testing."""
    return {
        "system": {
            "os": "Linux",
            "python_version": "3.12.3",
            "memory_available": "4GB",
            "disk_free": "80GB",
            "cpu_cores": 4
        },
        "network": {
            "internet_available": True,
            "telegram_api_available": True,
            "webhook_configured": False,
            "port_8000_free": True
        },
        "database": {
            "connected": True,
            "type": "sqlite",
            "tables_created": True,
            "indexes_optimized": True,
            "size": "1MB",
            "integrity_checked": True,
            "tables_count": 10
        },
        "security": {
            "tokens_protected": True,
            "ssl_configured": False,
            "firewall_active": False,
            "logging_enabled": True
        }
    }


@pytest.fixture
def mock_check_data():
    """Mock check data for testing."""
    return {
        "files": {
            "sdb_py": True,
            "init_files": True,
            "main_files": True
        },
        "database": {
            "connection": False,
            "tables": True,
            "indexes": True
        },
        "config": {
            "env_file": True,
            "core_settings": False,
            "main_settings": False
        },
        "permissions": {
            "project_dir": True,
            "data_dir": True,
            "logs_dir": False,
            "backup_dir": True
        }
    }


@pytest.fixture
def mock_cleanup_data():
    """Mock cleanup data for testing."""
    return {
        "temp_files": {
            "files_removed": 5,
            "space_freed": 1024 * 1024  # 1MB
        },
        "cache": {
            "modules_cleared": 3,
            "space_freed": 512 * 1024  # 512KB
        },
        "logs": {
            "files_removed": 10,
            "space_freed": 2 * 1024 * 1024  # 2MB
        },
        "backups": {
            "files_removed": 2,
            "space_freed": 5 * 1024 * 1024  # 5MB
        }
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "user_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "is_bot": False,
        "language_code": "en",
        "is_premium": False,
        "added_to_attachment_menu": False,
        "allows_write_to_pm": True
    }


@pytest.fixture
def sample_module_data():
    """Sample module data for testing."""
    return {
        "name": "test_module",
        "version": "1.0.0",
        "description": "Test module for testing",
        "author": "Test Author",
        "dependencies": ["requests"],
        "enabled": True,
        "config": {
            "setting1": "value1",
            "setting2": "value2"
        }
    }


@pytest.fixture
def sample_backup_data():
    """Sample backup data for testing."""
    return {
        "id": "backup_20240115_103000",
        "timestamp": "2024-01-15T10:30:00Z",
        "type": "full",
        "size": 10485760,  # 10MB
        "files_count": 100,
        "status": "completed",
        "path": "/backups/backup_20240115_103000.zip"
    }


@pytest.fixture
def mock_telegram_api():
    """Mock Telegram API responses."""
    return {
        "get_me": {
            "ok": True,
            "result": {
                "id": 123456789,
                "is_bot": True,
                "first_name": "TestBot",
                "username": "test_bot",
                "can_join_groups": True,
                "can_read_all_group_messages": False,
                "supports_inline_queries": False
            }
        },
        "send_message": {
            "ok": True,
            "result": {
                "message_id": 1,
                "from": {
                    "id": 123456789,
                    "is_bot": True,
                    "first_name": "TestBot",
                    "username": "test_bot"
                },
                "chat": {
                    "id": 987654321,
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "test_user",
                    "type": "private"
                },
                "date": 1642234567,
                "text": "Test message"
            }
        }
    }


# Маркеры для категоризации тестов
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "cli: mark test as CLI test"
    )
    config.addinivalue_line(
        "markers", "monitor: mark test as monitor command test"
    )
    config.addinivalue_line(
        "markers", "utils: mark test as utils command test"
    )
    config.addinivalue_line(
        "markers", "config: mark test as config command test"
    )
    config.addinivalue_line(
        "markers", "db: mark test as database command test"
    )
    config.addinivalue_line(
        "markers", "module: mark test as module command test"
    )
    config.addinivalue_line(
        "markers", "user: mark test as user command test"
    )
    config.addinivalue_line(
        "markers", "backup: mark test as backup command test"
    )
    config.addinivalue_line(
        "markers", "system: mark test as system command test"
    )
    config.addinivalue_line(
        "markers", "bot: mark test as bot command test"
    )
    config.addinivalue_line(
        "markers", "core: mark test as core functionality test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running test"
    ) 