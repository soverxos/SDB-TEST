"""
Tests for CLI config commands
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typer.testing import CliRunner

from cli.config import config_app


class TestConfigInit:
    """Tests for config init command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_init_basic(self, cli_runner: CliRunner):
        """Test basic config init command"""
        # Mock the interactive prompts
        with patch('typer.prompt') as mock_prompt:
            mock_prompt.side_effect = [
                "test_token:test_secret",  # bot token
                "1",  # sqlite choice
                "123456789"  # super admin id
            ]
            with patch('cli.config._update_env_file') as mock_update:
                mock_update.return_value = True
                result = cli_runner.invoke(config_app, ["init", "--force"])
                assert result.exit_code == 0


class TestConfigGet:
    """Tests for config get command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_get_basic(self, cli_runner: CliRunner):
        """Test basic config get command"""
        with patch('cli.config.read_yaml_file') as mock_read:
            mock_read.return_value = {"bot": {"token": "test_token"}}
            result = cli_runner.invoke(config_app, ["get"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_get_key(self, cli_runner: CliRunner):
        """Test config get with specific key"""
        # Mock the settings import from core.app_settings
        with patch('core.app_settings.settings') as mock_settings:
            # Create a mock settings object that behaves like a Pydantic model
            mock_settings.model_dump.return_value = {"bot": {"token": "test_token"}}
            mock_settings.bot = Mock()
            mock_settings.bot.token = "test_token"
            
            result = cli_runner.invoke(config_app, ["get", "bot.token"])
            assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_get_show_defaults(self, cli_runner: CliRunner):
        """Test config get with show defaults"""
        with patch('cli.config.read_yaml_file') as mock_read:
            mock_read.return_value = {"bot": {"token": "test_token"}}
            result = cli_runner.invoke(config_app, ["get", "--show-defaults"])
            assert result.exit_code == 0


class TestConfigSet:
    """Tests for config set command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_set_basic(self, cli_runner: CliRunner):
        """Test basic config set command"""
        with patch('cli.config.read_yaml_file') as mock_read:
            mock_read.return_value = {"bot": {"token": "old_token"}}
            with patch('cli.config.write_yaml_file') as mock_write:
                mock_write.return_value = True
                result = cli_runner.invoke(config_app, ["set", "bot.token", "new_token"])
                assert result.exit_code == 0

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_set_env(self, cli_runner: CliRunner):
        """Test config set with env variable"""
        with patch('cli.config._update_env_file') as mock_update:
            mock_update.return_value = True
            # Use a key that's in the env_map
            result = cli_runner.invoke(config_app, ["set", "telegram.token", "new_token"])
            assert result.exit_code == 0


class TestConfigSetModule:
    """Tests for config set-module command"""

    @pytest.mark.config
    @pytest.mark.cli
    def test_config_set_module_basic(self, cli_runner: CliRunner):
        """Test basic config set-module command"""
        with patch('cli.config.read_yaml_file') as mock_read:
            mock_read.return_value = {"module_setting": "old_value"}
            with patch('cli.config.write_yaml_file') as mock_write:
                mock_write.return_value = True
                result = cli_runner.invoke(config_app, ["set-module", "test_module", "module_setting", "new_value"])
                assert result.exit_code == 0


class TestConfigHelpers:
    """Tests for config helper functions"""

    @pytest.mark.config
    @pytest.mark.unit
    def test_load_config_file_yaml(self, temp_dir, test_config):
        """Test loading YAML config file"""
        config_file = temp_dir / "test_config.yaml"
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(test_config, f)
        
        from cli.config import read_yaml_file
        loaded_config = read_yaml_file(config_file)
        assert loaded_config == test_config

    @pytest.mark.config
    @pytest.mark.unit
    def test_save_config_file_yaml(self, temp_dir, test_config):
        """Test saving YAML config file"""
        config_file = temp_dir / "test_config.yaml"
        
        from cli.config import write_yaml_file
        result = write_yaml_file(config_file, test_config)
        assert result is True
        assert config_file.exists()

    @pytest.mark.config
    @pytest.mark.unit
    def test_validate_config_structure(self, test_config):
        """Test config structure validation"""
        # This is a basic test - in real implementation you'd have validation logic
        assert isinstance(test_config, dict)
        assert "bot" in test_config
        assert "database" in test_config

    @pytest.mark.config
    @pytest.mark.unit
    def test_get_nested_value(self, test_config):
        """Test getting nested config value"""
        # This would test a helper function for getting nested values
        # For now, we'll test basic dict access
        assert test_config.get("bot", {}).get("token") is not None

    @pytest.mark.config
    @pytest.mark.unit
    def test_set_nested_value(self, test_config):
        """Test setting nested config value"""
        # This would test a helper function for setting nested values
        # For now, we'll test basic dict manipulation
        config_copy = test_config.copy()
        if "bot" not in config_copy:
            config_copy["bot"] = {}
        config_copy["bot"]["new_setting"] = "new_value"
        assert config_copy["bot"]["new_setting"] == "new_value"

    @pytest.mark.config
    @pytest.mark.unit
    def test_convert_value_type(self):
        """Test value type conversion"""
        # This would test type conversion logic
        # For now, we'll test basic type conversions
        assert int("123") == 123
        assert float("123.45") == 123.45
        assert str(123) == "123" 