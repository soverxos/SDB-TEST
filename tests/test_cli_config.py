"""
Tests for CLI config commands
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typer.testing import CliRunner

from cli.config import config_app


class TestConfigShow:
    """Tests for config show command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_show_basic(self, cli_runner: CliRunner):
        """Test basic config show command"""
        with patch('cli.config._config_show_async') as mock_show:
            mock_show.return_value = None
            result = cli_runner.invoke(config_app, ["show"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_show_section(self, cli_runner: CliRunner):
        """Test config show with section"""
        with patch('cli.config._config_show_async') as mock_show:
            mock_show.return_value = None
            result = cli_runner.invoke(config_app, ["show", "--section", "bot"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_show_json(self, cli_runner: CliRunner):
        """Test config show with JSON output"""
        with patch('cli.config._config_show_async') as mock_show:
            mock_show.return_value = None
            result = cli_runner.invoke(config_app, ["show", "--json"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_config_show_async_success(self, test_config):
        """Test async config show with mock data"""
        with patch('cli.config.get_sdb_services_for_cli') as mock_get_services:
            mock_settings = Mock()
            mock_settings.dict.return_value = test_config
            mock_get_services.return_value = (mock_settings, Mock(), Mock())
            
            from cli.config import _config_show_async
            await _config_show_async(section=None, json_output=False)


class TestConfigSet:
    """Tests for config set command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_set_basic(self, cli_runner: CliRunner):
        """Test basic config set command"""
        with patch('cli.config._config_set_async') as mock_set:
            mock_set.return_value = None
            result = cli_runner.invoke(config_app, ["set", "bot.token", "new_token"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_set_with_type(self, cli_runner: CliRunner):
        """Test config set with type"""
        with patch('cli.config._config_set_async') as mock_set:
            mock_set.return_value = None
            result = cli_runner.invoke(config_app, ["set", "database.port", "5432", "--type", "int"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_config_set_async_success(self, test_config):
        """Test async config set with mock data"""
        with patch('cli.config.get_sdb_services_for_cli') as mock_get_services:
            mock_settings = Mock()
            mock_settings.dict.return_value = test_config
            mock_get_services.return_value = (mock_settings, Mock(), Mock())
            
            from cli.config import _config_set_async
            await _config_set_async(key="bot.token", value="new_token", value_type=None)


class TestConfigGet:
    """Tests for config get command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_get_basic(self, cli_runner: CliRunner):
        """Test basic config get command"""
        with patch('cli.config._config_get_async') as mock_get:
            mock_get.return_value = None
            result = cli_runner.invoke(config_app, ["get", "bot.token"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_get_json(self, cli_runner: CliRunner):
        """Test config get with JSON output"""
        with patch('cli.config._config_get_async') as mock_get:
            mock_get.return_value = None
            result = cli_runner.invoke(config_app, ["get", "bot.token", "--json"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_config_get_async_success(self, test_config):
        """Test async config get with mock data"""
        with patch('cli.config.get_sdb_services_for_cli') as mock_get_services:
            mock_settings = Mock()
            mock_settings.dict.return_value = test_config
            mock_get_services.return_value = (mock_settings, Mock(), Mock())
            
            from cli.config import _config_get_async
            await _config_get_async(key="bot.token", json_output=False)


class TestConfigReset:
    """Tests for config reset command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_reset_basic(self, cli_runner: CliRunner):
        """Test basic config reset command"""
        with patch('cli.config._config_reset_async') as mock_reset:
            mock_reset.return_value = None
            result = cli_runner.invoke(config_app, ["reset"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_reset_section(self, cli_runner: CliRunner):
        """Test config reset with section"""
        with patch('cli.config._config_reset_async') as mock_reset:
            mock_reset.return_value = None
            result = cli_runner.invoke(config_app, ["reset", "--section", "bot"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_reset_force(self, cli_runner: CliRunner):
        """Test config reset with force flag"""
        with patch('cli.config._config_reset_async') as mock_reset:
            mock_reset.return_value = None
            result = cli_runner.invoke(config_app, ["reset", "--force"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_config_reset_async_success(self, test_config):
        """Test async config reset with mock data"""
        with patch('cli.config.get_sdb_services_for_cli') as mock_get_services:
            mock_settings = Mock()
            mock_settings.dict.return_value = test_config
            mock_get_services.return_value = (mock_settings, Mock(), Mock())
            
            from cli.config import _config_reset_async
            await _config_reset_async(section=None, force=False)


class TestConfigValidate:
    """Tests for config validate command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_validate_basic(self, cli_runner: CliRunner):
        """Test basic config validate command"""
        with patch('cli.config._config_validate_async') as mock_validate:
            mock_validate.return_value = None
            result = cli_runner.invoke(config_app, ["validate"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_validate_strict(self, cli_runner: CliRunner):
        """Test config validate with strict flag"""
        with patch('cli.config._config_validate_async') as mock_validate:
            mock_validate.return_value = None
            result = cli_runner.invoke(config_app, ["validate", "--strict"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_config_validate_async_success(self, test_config):
        """Test async config validate with mock data"""
        with patch('cli.config.get_sdb_services_for_cli') as mock_get_services:
            mock_settings = Mock()
            mock_settings.dict.return_value = test_config
            mock_get_services.return_value = (mock_settings, Mock(), Mock())
            
            from cli.config import _config_validate_async
            await _config_validate_async(strict=False)


class TestConfigExport:
    """Tests for config export command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_export_basic(self, cli_runner: CliRunner):
        """Test basic config export command"""
        with patch('cli.config._config_export_async') as mock_export:
            mock_export.return_value = None
            result = cli_runner.invoke(config_app, ["export", "config_backup.yaml"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_export_format(self, cli_runner: CliRunner):
        """Test config export with format"""
        with patch('cli.config._config_export_async') as mock_export:
            mock_export.return_value = None
            result = cli_runner.invoke(config_app, ["export", "config_backup.json", "--format", "json"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_export_section(self, cli_runner: CliRunner):
        """Test config export with section"""
        with patch('cli.config._config_export_async') as mock_export:
            mock_export.return_value = None
            result = cli_runner.invoke(config_app, ["export", "bot_config.yaml", "--section", "bot"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_config_export_async_success(self, test_config):
        """Test async config export with mock data"""
        with patch('cli.config.get_sdb_services_for_cli') as mock_get_services:
            mock_settings = Mock()
            mock_settings.dict.return_value = test_config
            mock_get_services.return_value = (mock_settings, Mock(), Mock())
            
            from cli.config import _config_export_async
            await _config_export_async(output_file="test_config.yaml", format_type="yaml", section=None)


class TestConfigImport:
    """Tests for config import command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_import_basic(self, cli_runner: CliRunner):
        """Test basic config import command"""
        with patch('cli.config._config_import_async') as mock_import:
            mock_import.return_value = None
            result = cli_runner.invoke(config_app, ["import", "config_backup.yaml"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_import_merge(self, cli_runner: CliRunner):
        """Test config import with merge flag"""
        with patch('cli.config._config_import_async') as mock_import:
            mock_import.return_value = None
            result = cli_runner.invoke(config_app, ["import", "config_backup.yaml", "--merge"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_import_force(self, cli_runner: CliRunner):
        """Test config import with force flag"""
        with patch('cli.config._config_import_async') as mock_import:
            mock_import.return_value = None
            result = cli_runner.invoke(config_app, ["import", "config_backup.yaml", "--force"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_config_import_async_success(self, test_config):
        """Test async config import with mock data"""
        with patch('cli.config.get_sdb_services_for_cli') as mock_get_services:
            mock_settings = Mock()
            mock_settings.dict.return_value = test_config
            mock_get_services.return_value = (mock_settings, Mock(), Mock())
            
            from cli.config import _config_import_async
            await _config_import_async(input_file="test_config.yaml", merge=False, force=False)


class TestConfigDiff:
    """Tests for config diff command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_diff_basic(self, cli_runner: CliRunner):
        """Test basic config diff command"""
        with patch('cli.config._config_diff_async') as mock_diff:
            mock_diff.return_value = None
            result = cli_runner.invoke(config_app, ["diff", "config1.yaml", "config2.yaml"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_diff_format(self, cli_runner: CliRunner):
        """Test config diff with format"""
        with patch('cli.config._config_diff_async') as mock_diff:
            mock_diff.return_value = None
            result = cli_runner.invoke(config_app, ["diff", "config1.yaml", "config2.yaml", "--format", "json"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_config_diff_async_success(self, test_config):
        """Test async config diff with mock data"""
        with patch('cli.config._load_config_file', return_value=test_config):
            from cli.config import _config_diff_async
            await _config_diff_async(file1="config1.yaml", file2="config2.yaml", format_type="yaml")


class TestConfigHelpers:
    """Tests for config helper functions"""

    @pytest.mark.config
    @pytest.mark.unit
    def test_load_config_file_yaml(self, temp_dir, test_config):
        """Test _load_config_file function with YAML"""
        config_file = temp_dir / "test_config.yaml"
        
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)
        
        from cli.config import _load_config_file
        result = _load_config_file(config_file)
        assert result == test_config

    @pytest.mark.config
    @pytest.mark.unit
    def test_load_config_file_json(self, temp_dir, test_config):
        """Test _load_config_file function with JSON"""
        config_file = temp_dir / "test_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        from cli.config import _load_config_file
        result = _load_config_file(config_file)
        assert result == test_config

    @pytest.mark.config
    @pytest.mark.unit
    def test_save_config_file_yaml(self, temp_dir, test_config):
        """Test _save_config_file function with YAML"""
        config_file = temp_dir / "test_config.yaml"
        
        from cli.config import _save_config_file
        result = _save_config_file(config_file, test_config)
        assert result is True
        assert config_file.exists()

    @pytest.mark.config
    @pytest.mark.unit
    def test_save_config_file_json(self, temp_dir, test_config):
        """Test _save_config_file function with JSON"""
        config_file = temp_dir / "test_config.json"
        
        from cli.config import _save_config_file
        result = _save_config_file(config_file, test_config, format_type="json")
        assert result is True
        assert config_file.exists()

    @pytest.mark.config
    @pytest.mark.unit
    def test_validate_config_structure(self, test_config):
        """Test _validate_config_structure function"""
        from cli.config import _validate_config_structure
        
        # Тест с валидной конфигурацией
        result = _validate_config_structure(test_config)
        assert result["valid"] is True
        
        # Тест с невалидной конфигурацией
        invalid_config = {"invalid": "config"}
        result = _validate_config_structure(invalid_config)
        assert result["valid"] is False

    @pytest.mark.config
    @pytest.mark.unit
    def test_get_nested_value(self, test_config):
        """Test _get_nested_value function"""
        from cli.config import _get_nested_value
        
        # Тест получения значения
        result = _get_nested_value(test_config, "bot.token")
        assert result == "test_token_123456789"
        
        # Тест получения несуществующего значения
        result = _get_nested_value(test_config, "bot.nonexistent")
        assert result is None

    @pytest.mark.config
    @pytest.mark.unit
    def test_set_nested_value(self, test_config):
        """Test _set_nested_value function"""
        from cli.config import _set_nested_value
        
        # Тест установки значения
        config_copy = test_config.copy()
        _set_nested_value(config_copy, "bot.token", "new_token")
        assert config_copy["bot"]["token"] == "new_token"
        
        # Тест установки нового значения
        _set_nested_value(config_copy, "bot.new_setting", "value")
        assert config_copy["bot"]["new_setting"] == "value"

    @pytest.mark.config
    @pytest.mark.unit
    def test_convert_value_type(self):
        """Test _convert_value_type function"""
        from cli.config import _convert_value_type
        
        # Тест конвертации в int
        result = _convert_value_type("123", "int")
        assert result == 123
        
        # Тест конвертации в float
        result = _convert_value_type("123.45", "float")
        assert result == 123.45
        
        # Тест конвертации в bool
        result = _convert_value_type("true", "bool")
        assert result is True
        
        # Тест конвертации в str
        result = _convert_value_type(123, "str")
        assert result == "123"
        
        # Тест без указания типа
        result = _convert_value_type("test", None)
        assert result == "test" 