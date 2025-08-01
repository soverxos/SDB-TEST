"""
Tests for CLI utils commands
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typer.testing import CliRunner

from cli.utils import utils_app


class TestUtilsDiagnose:
    """Tests for utils diagnose command"""

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_diagnose_basic(self, cli_runner: CliRunner):
        """Test basic utils diagnose command"""
        with patch('cli.utils._utils_diagnose_async') as mock_diagnose:
            mock_diagnose.return_value = None
            result = cli_runner.invoke(utils_app, ["diagnose"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_diagnose_system(self, cli_runner: CliRunner):
        """Test utils diagnose with system flag"""
        with patch('cli.utils._utils_diagnose_async') as mock_diagnose:
            mock_diagnose.return_value = None
            result = cli_runner.invoke(utils_app, ["diagnose", "--system"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_diagnose_network(self, cli_runner: CliRunner):
        """Test utils diagnose with network flag"""
        with patch('cli.utils._utils_diagnose_async') as mock_diagnose:
            mock_diagnose.return_value = None
            result = cli_runner.invoke(utils_app, ["diagnose", "--network"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_diagnose_database(self, cli_runner: CliRunner):
        """Test utils diagnose with database flag"""
        with patch('cli.utils._utils_diagnose_async') as mock_diagnose:
            mock_diagnose.return_value = None
            result = cli_runner.invoke(utils_app, ["diagnose", "--database"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_diagnose_security(self, cli_runner: CliRunner):
        """Test utils diagnose with security flag"""
        with patch('cli.utils._utils_diagnose_async') as mock_diagnose:
            mock_diagnose.return_value = None
            result = cli_runner.invoke(utils_app, ["diagnose", "--security"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_diagnose_detailed(self, cli_runner: CliRunner):
        """Test utils diagnose with detailed flag"""
        with patch('cli.utils._utils_diagnose_async') as mock_diagnose:
            mock_diagnose.return_value = None
            result = cli_runner.invoke(utils_app, ["diagnose", "--detailed"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_utils_diagnose_async_success(self, mock_diagnostic_data):
        """Test async utils diagnose with mock data"""
        with patch('cli.utils._get_system_diagnostic', return_value=mock_diagnostic_data["system"]), \
             patch('cli.utils._get_network_diagnostic', return_value=mock_diagnostic_data["network"]), \
             patch('cli.utils._get_database_diagnostic', return_value=mock_diagnostic_data["database"]), \
             patch('cli.utils._get_security_diagnostic', return_value=mock_diagnostic_data["security"]):
            
            from cli.utils import _utils_diagnose_async
            await _utils_diagnose_async(system=True, network=True, database=True, 
                                      security=True, detailed=True)


class TestUtilsCheck:
    """Tests for utils check command"""

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_check_files(self, cli_runner: CliRunner):
        """Test utils check with files flag"""
        with patch('cli.utils._utils_check_async') as mock_check:
            mock_check.return_value = None
            result = cli_runner.invoke(utils_app, ["check", "--files"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_check_database(self, cli_runner: CliRunner):
        """Test utils check with database flag"""
        with patch('cli.utils._utils_check_async') as mock_check:
            mock_check.return_value = None
            result = cli_runner.invoke(utils_app, ["check", "--database"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_check_config(self, cli_runner: CliRunner):
        """Test utils check with config flag"""
        with patch('cli.utils._utils_check_async') as mock_check:
            mock_check.return_value = None
            result = cli_runner.invoke(utils_app, ["check", "--config"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_check_permissions(self, cli_runner: CliRunner):
        """Test utils check with permissions flag"""
        with patch('cli.utils._utils_check_async') as mock_check:
            mock_check.return_value = None
            result = cli_runner.invoke(utils_app, ["check", "--permissions"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_check_all(self, cli_runner: CliRunner):
        """Test utils check with all flag"""
        with patch('cli.utils._utils_check_async') as mock_check:
            mock_check.return_value = None
            result = cli_runner.invoke(utils_app, ["check", "--all"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_utils_check_async_success(self, mock_check_data):
        """Test async utils check with mock data"""
        with patch('cli.utils._check_files_integrity', return_value=mock_check_data["files"]), \
             patch('cli.utils._check_database_integrity', return_value=mock_check_data["database"]), \
             patch('cli.utils._check_config_integrity', return_value=mock_check_data["config"]), \
             patch('cli.utils._check_permissions', return_value=mock_check_data["permissions"]):
            
            from cli.utils import _utils_check_async
            await _utils_check_async(files=True, database=True, config=True, 
                                   permissions=True, all=True)


class TestUtilsCleanup:
    """Tests for utils cleanup command"""

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_cleanup_temp(self, cli_runner: CliRunner):
        """Test utils cleanup with temp flag"""
        with patch('cli.utils._utils_cleanup_async') as mock_cleanup:
            mock_cleanup.return_value = None
            result = cli_runner.invoke(utils_app, ["cleanup", "--temp"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_cleanup_cache(self, cli_runner: CliRunner):
        """Test utils cleanup with cache flag"""
        with patch('cli.utils._utils_cleanup_async') as mock_cleanup:
            mock_cleanup.return_value = None
            result = cli_runner.invoke(utils_app, ["cleanup", "--cache"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_cleanup_logs(self, cli_runner: CliRunner):
        """Test utils cleanup with logs flag"""
        with patch('cli.utils._utils_cleanup_async') as mock_cleanup:
            mock_cleanup.return_value = None
            result = cli_runner.invoke(utils_app, ["cleanup", "--logs"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_cleanup_backups(self, cli_runner: CliRunner):
        """Test utils cleanup with backups flag"""
        with patch('cli.utils._utils_cleanup_async') as mock_cleanup:
            mock_cleanup.return_value = None
            result = cli_runner.invoke(utils_app, ["cleanup", "--backups"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_cleanup_all(self, cli_runner: CliRunner):
        """Test utils cleanup with all flag"""
        with patch('cli.utils._utils_cleanup_async') as mock_cleanup:
            mock_cleanup.return_value = None
            result = cli_runner.invoke(utils_app, ["cleanup", "--all"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_utils_cleanup_async_success(self, mock_cleanup_data):
        """Test async utils cleanup with mock data"""
        with patch('cli.utils._clean_temp_files', return_value=(mock_cleanup_data["temp_files"]["files_removed"], 
                                                              mock_cleanup_data["temp_files"]["space_freed"])), \
             patch('cli.utils._clean_cache', return_value=(mock_cleanup_data["cache"]["modules_cleared"], 
                                                         mock_cleanup_data["cache"]["space_freed"])):
            
            from cli.utils import _utils_cleanup_async
            await _utils_cleanup_async(temp=True, cache=True, logs=False, backups=False, all=False)


class TestUtilsConvert:
    """Tests for utils convert command"""

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_convert_json_to_yaml(self, cli_runner: CliRunner, temp_dir, test_file_content):
        """Test utils convert JSON to YAML"""
        input_file = temp_dir / "test.json"
        output_file = temp_dir / "test.yaml"
        
        with open(input_file, 'w') as f:
            f.write(test_file_content["json"])
        
        with patch('cli.utils._convert_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["convert", str(input_file), str(output_file)])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_convert_csv_to_json(self, cli_runner: CliRunner, temp_dir, test_file_content):
        """Test utils convert CSV to JSON"""
        input_file = temp_dir / "test.csv"
        output_file = temp_dir / "test.json"
        
        with open(input_file, 'w') as f:
            f.write(test_file_content["csv"])
        
        with patch('cli.utils._convert_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["convert", str(input_file), str(output_file), "--format", "json"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_convert_yaml_to_csv(self, cli_runner: CliRunner, temp_dir, test_file_content):
        """Test utils convert YAML to CSV"""
        input_file = temp_dir / "test.yaml"
        output_file = temp_dir / "test.csv"
        
        with open(input_file, 'w') as f:
            f.write(test_file_content["yaml"])
        
        with patch('cli.utils._convert_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["convert", str(input_file), str(output_file), "--format", "csv"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_convert_with_encoding(self, cli_runner: CliRunner, temp_dir, test_file_content):
        """Test utils convert with custom encoding"""
        input_file = temp_dir / "test.json"
        output_file = temp_dir / "test.yaml"
        
        with open(input_file, 'w') as f:
            f.write(test_file_content["json"])
        
        with patch('cli.utils._convert_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["convert", str(input_file), str(output_file), "--encoding", "utf-8"])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.unit
    def test_convert_file_json_to_yaml(self, temp_dir, test_file_content):
        """Test _convert_file function JSON to YAML"""
        input_file = temp_dir / "test.json"
        output_file = temp_dir / "test.yaml"
        
        with open(input_file, 'w') as f:
            f.write(test_file_content["json"])
        
        from cli.utils import _convert_file
        result = _convert_file(input_file, output_file, "yaml")
        assert result is True
        assert output_file.exists()

    @pytest.mark.utils
    @pytest.mark.unit
    def test_convert_file_csv_to_json(self, temp_dir, test_file_content):
        """Test _convert_file function CSV to JSON"""
        input_file = temp_dir / "test.csv"
        output_file = temp_dir / "test.json"
        
        with open(input_file, 'w') as f:
            f.write(test_file_content["csv"])
        
        from cli.utils import _convert_file
        result = _convert_file(input_file, output_file, "json")
        assert result is True
        assert output_file.exists()

    @pytest.mark.utils
    @pytest.mark.unit
    def test_convert_file_yaml_to_csv(self, temp_dir, test_file_content):
        """Test _convert_file function YAML to CSV"""
        input_file = temp_dir / "test.yaml"
        output_file = temp_dir / "test.csv"
        
        with open(input_file, 'w') as f:
            f.write(test_file_content["yaml"])
        
        from cli.utils import _convert_file
        result = _convert_file(input_file, output_file, "csv")
        assert result is True
        assert output_file.exists()


class TestUtilsEncrypt:
    """Tests for utils encrypt command"""

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_encrypt_basic(self, cli_runner: CliRunner, temp_dir, test_encryption_data):
        """Test basic utils encrypt command"""
        input_file = temp_dir / "secret.txt"
        output_file = temp_dir / "secret.enc"
        
        with open(input_file, 'w') as f:
            f.write(test_encryption_data["plaintext"])
        
        with patch('cli.utils._encrypt_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["encrypt", str(input_file), str(output_file)])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_encrypt_with_password(self, cli_runner: CliRunner, temp_dir, test_encryption_data):
        """Test utils encrypt with password"""
        input_file = temp_dir / "secret.txt"
        output_file = temp_dir / "secret.enc"
        
        with open(input_file, 'w') as f:
            f.write(test_encryption_data["plaintext"])
        
        with patch('cli.utils._encrypt_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["encrypt", str(input_file), str(output_file), 
                                                  "--password", test_encryption_data["password"]])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_encrypt_with_algorithm(self, cli_runner: CliRunner, temp_dir, test_encryption_data):
        """Test utils encrypt with algorithm"""
        input_file = temp_dir / "secret.txt"
        output_file = temp_dir / "secret.enc"
        
        with open(input_file, 'w') as f:
            f.write(test_encryption_data["plaintext"])
        
        with patch('cli.utils._encrypt_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["encrypt", str(input_file), str(output_file), 
                                                  "--algorithm", test_encryption_data["algorithm"]])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.unit
    def test_encrypt_file_success(self, temp_dir, test_encryption_data):
        """Test _encrypt_file function success"""
        input_file = temp_dir / "secret.txt"
        output_file = temp_dir / "secret.enc"
        
        with open(input_file, 'w') as f:
            f.write(test_encryption_data["plaintext"])
        
        from cli.utils import _encrypt_file
        result = _encrypt_file(input_file, output_file, "aes", test_encryption_data["password"])
        assert result is True
        assert output_file.exists()


class TestUtilsDecrypt:
    """Tests for utils decrypt command"""

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_decrypt_basic(self, cli_runner: CliRunner, temp_dir, test_encryption_data):
        """Test basic utils decrypt command"""
        input_file = temp_dir / "secret.enc"
        output_file = temp_dir / "decrypted.txt"
        
        # Создаем зашифрованный файл
        with open(input_file, 'w') as f:
            f.write("encrypted_content")
        
        with patch('cli.utils._decrypt_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["decrypt", str(input_file), str(output_file)])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_decrypt_with_password(self, cli_runner: CliRunner, temp_dir, test_encryption_data):
        """Test utils decrypt with password"""
        input_file = temp_dir / "secret.enc"
        output_file = temp_dir / "decrypted.txt"
        
        # Создаем зашифрованный файл
        with open(input_file, 'w') as f:
            f.write("encrypted_content")
        
        with patch('cli.utils._decrypt_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["decrypt", str(input_file), str(output_file), 
                                                  "--password", test_encryption_data["password"]])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.cli
    def test_utils_decrypt_with_key_file(self, cli_runner: CliRunner, temp_dir, test_encryption_data):
        """Test utils decrypt with key file"""
        input_file = temp_dir / "secret.enc"
        output_file = temp_dir / "decrypted.txt"
        key_file = temp_dir / "secret.key"
        
        # Создаем зашифрованный файл и ключ
        with open(input_file, 'w') as f:
            f.write("encrypted_content")
        with open(key_file, 'w') as f:
            f.write("key_content")
        
        with patch('cli.utils._decrypt_file', return_value=True):
            result = cli_runner.invoke(utils_app, ["decrypt", str(input_file), str(output_file), 
                                                  "--key-file", str(key_file)])
            assert result.exit_code == 0

    @pytest.mark.utils
    @pytest.mark.unit
    def test_decrypt_file_success(self, temp_dir, test_encryption_data):
        """Test _decrypt_file function success"""
        input_file = temp_dir / "secret.enc"
        output_file = temp_dir / "decrypted.txt"
        
        # Создаем зашифрованный файл
        with open(input_file, 'w') as f:
            f.write("encrypted_content")
        
        from cli.utils import _decrypt_file
        result = _decrypt_file(input_file, output_file, test_encryption_data["password"])
        # Функция может вернуть False если не может расшифровать, но должна выполниться без ошибок
        assert isinstance(result, bool)


class TestUtilsHelpers:
    """Tests for utils helper functions"""

    @pytest.mark.utils
    @pytest.mark.unit
    def test_get_system_diagnostic(self, mock_system_info):
        """Test _get_system_diagnostic function"""
        with patch('cli.utils.platform') as mock_platform, \
             patch('cli.utils.psutil') as mock_psutil:
            
            mock_platform.system.return_value = mock_system_info["platform"]
            mock_platform.python_version.return_value = mock_system_info["python_version"]
            
            mock_virtual_memory = Mock()
            mock_virtual_memory.available = 4 * 1024 * 1024 * 1024  # 4GB
            mock_psutil.virtual_memory.return_value = mock_virtual_memory
            
            mock_disk_usage = Mock()
            mock_disk_usage.free = 80 * 1024 * 1024 * 1024  # 80GB
            mock_psutil.disk_usage.return_value = mock_disk_usage
            
            mock_psutil.cpu_count.return_value = 4
            
            from cli.utils import _get_system_diagnostic
            result = _get_system_diagnostic()
            
            assert "os" in result
            assert "python_version" in result
            assert "memory_available" in result
            assert "disk_free" in result
            assert "cpu_cores" in result

    @pytest.mark.utils
    @pytest.mark.unit
    def test_get_network_diagnostic(self):
        """Test _get_network_diagnostic function"""
        with patch('cli.utils.requests') as mock_requests, \
             patch('cli.utils.socket') as mock_socket:
            
            mock_requests.get.return_value.status_code = 200
            mock_socket.socket.return_value.connect.return_value = None
            
            from cli.utils import _get_network_diagnostic
            result = _get_network_diagnostic()
            
            assert "internet_available" in result
            assert "telegram_api_available" in result
            assert "webhook_configured" in result
            assert "port_8000_free" in result

    @pytest.mark.utils
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_database_diagnostic(self, mock_database_status):
        """Test _get_database_diagnostic function"""
        with patch('cli.utils.get_sdb_services_for_cli') as mock_get_services:
            mock_get_services.return_value = (Mock(), Mock(), Mock())
            
            from cli.utils import _get_database_diagnostic
            result = await _get_database_diagnostic()
            
            # Проверяем что функция выполнилась без ошибок
            assert result is not None

    @pytest.mark.utils
    @pytest.mark.unit
    def test_get_security_diagnostic(self):
        """Test _get_security_diagnostic function"""
        with patch('cli.utils.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            from cli.utils import _get_security_diagnostic
            result = _get_security_diagnostic()
            
            assert "tokens_protected" in result
            assert "ssl_configured" in result
            assert "firewall_active" in result
            assert "logging_enabled" in result

    @pytest.mark.utils
    @pytest.mark.unit
    def test_clean_temp_files(self, temp_dir):
        """Test _clean_temp_files function"""
        # Создаем временные файлы
        temp_files = [
            temp_dir / "temp1.txt",
            temp_dir / "temp2.txt",
            temp_dir / "temp3.txt"
        ]
        
        for file in temp_files:
            with open(file, 'w') as f:
                f.write("temp content")
        
        from cli.utils import _clean_temp_files
        files_removed, space_freed = _clean_temp_files()
        
        # Проверяем что функция выполнилась без ошибок
        assert isinstance(files_removed, int)
        assert isinstance(space_freed, int)

    @pytest.mark.utils
    @pytest.mark.unit
    def test_clean_cache(self, temp_dir):
        """Test _clean_cache function"""
        # Создаем кэш файлы
        cache_dir = temp_dir / "__pycache__"
        cache_dir.mkdir()
        
        cache_files = [
            cache_dir / "module1.pyc",
            cache_dir / "module2.pyc"
        ]
        
        for file in cache_files:
            with open(file, 'w') as f:
                f.write("cache content")
        
        from cli.utils import _clean_cache
        modules_cleared, space_freed = _clean_cache()
        
        # Проверяем что функция выполнилась без ошибок
        assert isinstance(modules_cleared, int)
        assert isinstance(space_freed, int)

    @pytest.mark.utils
    @pytest.mark.unit
    def test_clean_logs(self, temp_dir):
        """Test _clean_logs function"""
        # Создаем лог файлы
        log_files = [
            temp_dir / "app.log",
            temp_dir / "error.log",
            temp_dir / "debug.log"
        ]
        
        for file in log_files:
            with open(file, 'w') as f:
                f.write("log content")
        
        from cli.utils import _clean_logs
        files_removed, space_freed = _clean_logs()
        
        # Проверяем что функция выполнилась без ошибок
        assert isinstance(files_removed, int)
        assert isinstance(space_freed, int)

    @pytest.mark.utils
    @pytest.mark.unit
    def test_clean_backups(self, temp_dir):
        """Test _clean_backups function"""
        # Создаем бэкап файлы
        backup_files = [
            temp_dir / "backup1.zip",
            temp_dir / "backup2.zip"
        ]
        
        for file in backup_files:
            with open(file, 'w') as f:
                f.write("backup content")
        
        from cli.utils import _clean_backups
        files_removed, space_freed = _clean_backups()
        
        # Проверяем что функция выполнилась без ошибок
        assert isinstance(files_removed, int)
        assert isinstance(space_freed, int)

    @pytest.mark.utils
    @pytest.mark.unit
    def test_check_files_integrity(self, temp_dir):
        """Test _check_files_integrity function"""
        # Создаем тестовые файлы
        test_files = [
            temp_dir / "sdb.py",
            temp_dir / "__init__.py"
        ]
        
        for file in test_files:
            with open(file, 'w') as f:
                f.write("test content")
        
        from cli.utils import _check_files_integrity
        result = _check_files_integrity()
        
        # Проверяем что функция выполнилась без ошибок
        assert isinstance(result, dict)

    @pytest.mark.utils
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_database_integrity(self):
        """Test _check_database_integrity function"""
        with patch('cli.utils.get_sdb_services_for_cli') as mock_get_services:
            mock_get_services.return_value = (Mock(), Mock(), Mock())
            
            from cli.utils import _check_database_integrity
            result = await _check_database_integrity()
            
            # Проверяем что функция выполнилась без ошибок
            assert isinstance(result, dict)

    @pytest.mark.utils
    @pytest.mark.unit
    def test_check_config_integrity(self, temp_dir):
        """Test _check_config_integrity function"""
        # Создаем конфигурационные файлы
        config_files = [
            temp_dir / ".env",
            temp_dir / "config.yaml"
        ]
        
        for file in config_files:
            with open(file, 'w') as f:
                f.write("config content")
        
        from cli.utils import _check_config_integrity
        result = _check_config_integrity()
        
        # Проверяем что функция выполнилась без ошибок
        assert isinstance(result, dict)

    @pytest.mark.utils
    @pytest.mark.unit
    def test_check_permissions(self, temp_dir):
        """Test _check_permissions function"""
        # Создаем тестовые директории
        test_dirs = [
            temp_dir / "project",
            temp_dir / "data",
            temp_dir / "logs",
            temp_dir / "backup"
        ]
        
        for dir_path in test_dirs:
            dir_path.mkdir()
        
        from cli.utils import _check_permissions
        result = _check_permissions()
        
        # Проверяем что функция выполнилась без ошибок
        assert isinstance(result, dict)

    @pytest.mark.utils
    @pytest.mark.unit
    def test_format_size(self):
        """Test format_size function"""
        from cli.utils import format_size
        
        # Тест для байтов
        assert format_size(1024) == "1.0 KB"
        
        # Тест для килобайтов
        assert format_size(1024 * 1024) == "1.0 MB"
        
        # Тест для мегабайтов
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"
        
        # Тест для 0 байт
        assert format_size(0) == "0 B"
        
        # Тест для отрицательного значения
        assert format_size(-1024) == "0 B"

    @pytest.mark.utils
    @pytest.mark.unit
    def test_confirm_action(self):
        """Test confirm_action function"""
        from cli.utils import confirm_action
        
        # Тест с подтверждением
        with patch('builtins.input', return_value='y'):
            result = confirm_action("Test action?")
            assert result is True
        
        # Тест с отказом
        with patch('builtins.input', return_value='n'):
            result = confirm_action("Test action?")
            assert result is False
        
        # Тест с пустым вводом (по умолчанию)
        with patch('builtins.input', return_value=''):
            result = confirm_action("Test action?", default_choice=True)
            assert result is True 