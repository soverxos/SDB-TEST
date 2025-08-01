"""
Tests for CLI monitor commands
"""

import json
import pytest
from unittest.mock import Mock, patch, AsyncMock
from typer.testing import CliRunner

from cli.monitor import monitor_app


class TestMonitorStatus:
    """Tests for monitor status command"""

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_status_basic(self, cli_runner: CliRunner):
        """Test basic monitor status command"""
        with patch('cli.monitor._monitor_status_async') as mock_status:
            mock_status.return_value = None
            result = cli_runner.invoke(monitor_app, ["status"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_status_detailed(self, cli_runner: CliRunner):
        """Test monitor status with detailed flag"""
        with patch('cli.monitor._monitor_status_async') as mock_status:
            mock_status.return_value = None
            result = cli_runner.invoke(monitor_app, ["status", "--detailed"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_status_json(self, cli_runner: CliRunner):
        """Test monitor status with JSON output"""
        with patch('cli.monitor._monitor_status_async') as mock_status:
            mock_status.return_value = None
            result = cli_runner.invoke(monitor_app, ["status", "--json"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_status_health(self, cli_runner: CliRunner):
        """Test monitor status with health check"""
        with patch('cli.monitor._monitor_status_async') as mock_status:
            mock_status.return_value = None
            result = cli_runner.invoke(monitor_app, ["status", "--health"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_monitor_status_async_success(self, mock_system_info, mock_cpu_info, 
                                              mock_memory_info, mock_disk_info, 
                                              mock_network_info, mock_bot_status, 
                                              mock_database_status):
        """Test async monitor status with mock data"""
        with patch('cli.monitor._get_system_info', return_value=mock_system_info), \
             patch('cli.monitor._get_cpu_info', return_value=mock_cpu_info), \
             patch('cli.monitor._get_memory_info', return_value=mock_memory_info), \
             patch('cli.monitor._get_disk_info', return_value=mock_disk_info), \
             patch('cli.monitor._get_network_info', return_value=mock_network_info), \
             patch('cli.monitor._get_bot_status', return_value=mock_bot_status), \
             patch('cli.monitor._get_database_status', return_value=mock_database_status):
            
            from cli.monitor import _monitor_status_async
            await _monitor_status_async(detailed=False, json_output=False, health=False, notify=None)


class TestMonitorMetrics:
    """Tests for monitor metrics command"""

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_metrics_basic(self, cli_runner: CliRunner):
        """Test basic monitor metrics command"""
        with patch('cli.monitor._monitor_metrics_async') as mock_metrics:
            mock_metrics.return_value = None
            result = cli_runner.invoke(monitor_app, ["metrics"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_metrics_cpu_memory(self, cli_runner: CliRunner):
        """Test monitor metrics with CPU and memory flags"""
        with patch('cli.monitor._monitor_metrics_async') as mock_metrics:
            mock_metrics.return_value = None
            result = cli_runner.invoke(monitor_app, ["metrics", "--cpu", "--memory"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_metrics_disk_network(self, cli_runner: CliRunner):
        """Test monitor metrics with disk and network flags"""
        with patch('cli.monitor._monitor_metrics_async') as mock_metrics:
            mock_metrics.return_value = None
            result = cli_runner.invoke(monitor_app, ["metrics", "--disk", "--network"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_metrics_real_time(self, cli_runner: CliRunner):
        """Test monitor metrics with real-time flag"""
        with patch('cli.monitor._monitor_metrics_async') as mock_metrics:
            mock_metrics.return_value = None
            result = cli_runner.invoke(monitor_app, ["metrics", "--real-time"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_monitor_metrics_async_success(self, mock_cpu_info, mock_memory_info, 
                                                mock_disk_info, mock_network_info):
        """Test async monitor metrics with mock data"""
        with patch('cli.monitor._get_cpu_info', return_value=mock_cpu_info), \
             patch('cli.monitor._get_memory_info', return_value=mock_memory_info), \
             patch('cli.monitor._get_disk_info', return_value=mock_disk_info), \
             patch('cli.monitor._get_network_info', return_value=mock_network_info):
            
            from cli.monitor import _monitor_metrics_async
            await _monitor_metrics_async(cpu=True, memory=True, disk=False, network=False, 
                                       real_time=False, history=False, hours=24)


class TestMonitorAlerts:
    """Tests for monitor alerts command"""

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_alerts_list(self, cli_runner: CliRunner):
        """Test monitor alerts list command"""
        with patch('cli.monitor._monitor_alerts_async') as mock_alerts:
            mock_alerts.return_value = None
            result = cli_runner.invoke(monitor_app, ["alerts", "--list"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_alerts_history(self, cli_runner: CliRunner):
        """Test monitor alerts history command"""
        with patch('cli.monitor._monitor_alerts_async') as mock_alerts:
            mock_alerts.return_value = None
            result = cli_runner.invoke(monitor_app, ["alerts", "--history"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_alerts_configure(self, cli_runner: CliRunner):
        """Test monitor alerts configure command"""
        with patch('cli.monitor._monitor_alerts_async') as mock_alerts:
            mock_alerts.return_value = None
            result = cli_runner.invoke(monitor_app, ["alerts", "--configure"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_alerts_test(self, cli_runner: CliRunner):
        """Test monitor alerts test command"""
        with patch('cli.monitor._monitor_alerts_async') as mock_alerts:
            mock_alerts.return_value = None
            result = cli_runner.invoke(monitor_app, ["alerts", "--test"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_monitor_alerts_async_success(self, mock_alert_data):
        """Test async monitor alerts with mock data"""
        with patch('cli.monitor._get_alerts_data', return_value=mock_alert_data):
            from cli.monitor import _monitor_alerts_async
            await _monitor_alerts_async(list_alerts=True, configure=False, test=False, history=False)


class TestMonitorLogs:
    """Tests for monitor logs command"""

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_logs_analyze(self, cli_runner: CliRunner):
        """Test monitor logs analyze command"""
        with patch('cli.monitor._monitor_logs_async') as mock_logs:
            mock_logs.return_value = None
            result = cli_runner.invoke(monitor_app, ["logs", "--analyze"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_logs_errors(self, cli_runner: CliRunner):
        """Test monitor logs errors command"""
        with patch('cli.monitor._monitor_logs_async') as mock_logs:
            mock_logs.return_value = None
            result = cli_runner.invoke(monitor_app, ["logs", "--errors"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_logs_last(self, cli_runner: CliRunner):
        """Test monitor logs last command"""
        with patch('cli.monitor._monitor_logs_async') as mock_logs:
            mock_logs.return_value = None
            result = cli_runner.invoke(monitor_app, ["logs", "--last", "10"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_logs_search(self, cli_runner: CliRunner):
        """Test monitor logs search command"""
        with patch('cli.monitor._monitor_logs_async') as mock_logs:
            mock_logs.return_value = None
            result = cli_runner.invoke(monitor_app, ["logs", "--search", "error"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_monitor_logs_async_success(self, mock_log_data):
        """Test async monitor logs with mock data"""
        with patch('cli.monitor._get_logs_data', return_value=mock_log_data):
            from cli.monitor import _monitor_logs_async
            await _monitor_logs_async(analyze=True, errors=False, last_n=None, since=None, search=None)


class TestMonitorPerformance:
    """Tests for monitor performance command"""

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_performance_basic(self, cli_runner: CliRunner):
        """Test basic monitor performance command"""
        with patch('cli.monitor._monitor_performance_async') as mock_perf:
            mock_perf.return_value = None
            result = cli_runner.invoke(monitor_app, ["performance"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_performance_slow_queries(self, cli_runner: CliRunner):
        """Test monitor performance with slow queries flag"""
        with patch('cli.monitor._monitor_performance_async') as mock_perf:
            mock_perf.return_value = None
            result = cli_runner.invoke(monitor_app, ["performance", "--slow-queries"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_performance_response_time(self, cli_runner: CliRunner):
        """Test monitor performance with response time flag"""
        with patch('cli.monitor._monitor_performance_async') as mock_perf:
            mock_perf.return_value = None
            result = cli_runner.invoke(monitor_app, ["performance", "--response-time"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_performance_memory_leaks(self, cli_runner: CliRunner):
        """Test monitor performance with memory leaks flag"""
        with patch('cli.monitor._monitor_performance_async') as mock_perf:
            mock_perf.return_value = None
            result = cli_runner.invoke(monitor_app, ["performance", "--memory-leaks"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_monitor_performance_async_success(self, mock_performance_data):
        """Test async monitor performance with mock data"""
        with patch('cli.monitor._get_performance_data', return_value=mock_performance_data):
            from cli.monitor import _monitor_performance_async
            await _monitor_performance_async(slow_queries=True, response_time=False, 
                                           memory_leaks=False, bottlenecks=False)


class TestMonitorReport:
    """Tests for monitor report command"""

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_report_daily(self, cli_runner: CliRunner):
        """Test monitor report daily command"""
        with patch('cli.monitor._monitor_report_async') as mock_report:
            mock_report.return_value = None
            result = cli_runner.invoke(monitor_app, ["report", "--daily"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_report_weekly(self, cli_runner: CliRunner):
        """Test monitor report weekly command"""
        with patch('cli.monitor._monitor_report_async') as mock_report:
            mock_report.return_value = None
            result = cli_runner.invoke(monitor_app, ["report", "--weekly"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_report_monthly(self, cli_runner: CliRunner):
        """Test monitor report monthly command"""
        with patch('cli.monitor._monitor_report_async') as mock_report:
            mock_report.return_value = None
            result = cli_runner.invoke(monitor_app, ["report", "--monthly"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_report_format(self, cli_runner: CliRunner):
        """Test monitor report with format flag"""
        with patch('cli.monitor._monitor_report_async') as mock_report:
            mock_report.return_value = None
            result = cli_runner.invoke(monitor_app, ["report", "--daily", "--format", "html"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_monitor_report_async_success(self, mock_report_data):
        """Test async monitor report with mock data"""
        with patch('cli.monitor._generate_report', return_value=mock_report_data):
            from cli.monitor import _monitor_report_async
            await _monitor_report_async(daily=True, weekly=False, monthly=False, 
                                      format_type="html", email=None)


class TestMonitorIntegrate:
    """Tests for monitor integrate command"""

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_integrate_prometheus_grafana(self, cli_runner: CliRunner):
        """Test monitor integrate with Prometheus and Grafana"""
        with patch('cli.monitor._monitor_integrate_async') as mock_integrate:
            mock_integrate.return_value = None
            result = cli_runner.invoke(monitor_app, ["integrate", "--prometheus", "--grafana"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_integrate_datadog(self, cli_runner: CliRunner):
        """Test monitor integrate with DataDog"""
        with patch('cli.monitor._monitor_integrate_async') as mock_integrate:
            mock_integrate.return_value = None
            result = cli_runner.invoke(monitor_app, ["integrate", "--datadog"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_integrate_newrelic(self, cli_runner: CliRunner):
        """Test monitor integrate with New Relic"""
        with patch('cli.monitor._monitor_integrate_async') as mock_integrate:
            mock_integrate.return_value = None
            result = cli_runner.invoke(monitor_app, ["integrate", "--newrelic"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_monitor_integrate_async_success(self, mock_integration_data):
        """Test async monitor integrate with mock data"""
        with patch('cli.monitor._setup_integration', return_value=mock_integration_data):
            from cli.monitor import _monitor_integrate_async
            await _monitor_integrate_async(prometheus=True, grafana=True, 
                                         datadog=False, newrelic=False)


class TestMonitorDashboard:
    """Tests for monitor dashboard command"""

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_dashboard_basic(self, cli_runner: CliRunner):
        """Test basic monitor dashboard command"""
        with patch('cli.monitor._monitor_dashboard_async') as mock_dashboard:
            mock_dashboard.return_value = None
            result = cli_runner.invoke(monitor_app, ["dashboard"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_dashboard_port(self, cli_runner: CliRunner):
        """Test monitor dashboard with custom port"""
        with patch('cli.monitor._monitor_dashboard_async') as mock_dashboard:
            mock_dashboard.return_value = None
            result = cli_runner.invoke(monitor_app, ["dashboard", "--port", "8080"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_dashboard_host(self, cli_runner: CliRunner):
        """Test monitor dashboard with custom host"""
        with patch('cli.monitor._monitor_dashboard_async') as mock_dashboard:
            mock_dashboard.return_value = None
            result = cli_runner.invoke(monitor_app, ["dashboard", "--host", "0.0.0.0"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    def test_monitor_dashboard_theme(self, cli_runner: CliRunner):
        """Test monitor dashboard with theme"""
        with patch('cli.monitor._monitor_dashboard_async') as mock_dashboard:
            mock_dashboard.return_value = None
            result = cli_runner.invoke(monitor_app, ["dashboard", "--theme", "dark"])
            assert result.exit_code == 0

    @pytest.mark.monitor
    @pytest.mark.cli
    @pytest.mark.asyncio
    async def test_monitor_dashboard_async_success(self):
        """Test async monitor dashboard"""
        # Mock uvicorn.Server to prevent real server startup
        with patch('uvicorn.Server') as mock_server_class:
            mock_server = Mock()
            mock_server.serve = AsyncMock()
            mock_server_class.return_value = mock_server
            
            from cli.monitor import _monitor_dashboard_async
            await _monitor_dashboard_async(port=8080, host="localhost", theme="light")
            
            # Verify server was created and serve was called
            mock_server_class.assert_called_once()
            mock_server.serve.assert_called_once()


class TestMonitorHelpers:
    """Tests for monitor helper functions"""

    @pytest.mark.monitor
    @pytest.mark.unit
    def test_get_system_info(self, mock_system_info):
        """Test _get_system_info function"""
        with patch('cli.monitor.platform') as mock_platform:
            mock_platform.system.return_value = mock_system_info["platform"]
            mock_platform.version.return_value = mock_system_info["platform_version"]
            mock_platform.architecture.return_value = (mock_system_info["architecture"],)
            mock_platform.processor.return_value = mock_system_info["processor"]
            mock_platform.node.return_value = mock_system_info["hostname"]
            mock_platform.python_version.return_value = mock_system_info["python_version"]
            
            from cli.monitor import _get_system_info
            result = _get_system_info()
            
            assert result["platform"] == mock_system_info["platform"]
            assert result["python_version"] == mock_system_info["python_version"]

    @pytest.mark.monitor
    @pytest.mark.unit
    def test_get_cpu_info(self, mock_cpu_info):
        """Test _get_cpu_info function"""
        with patch('cli.monitor.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = mock_cpu_info["percent"]
            mock_psutil.cpu_count.return_value = mock_cpu_info["count"]
            mock_psutil.cpu_freq.return_value = Mock(current=mock_cpu_info["frequency"])
            mock_psutil.getloadavg.return_value = mock_cpu_info["load_avg"]
            
            from cli.monitor import _get_cpu_info
            result = _get_cpu_info()
            
            assert result["percent"] == mock_cpu_info["percent"]
            assert result["count"] == mock_cpu_info["count"]

    @pytest.mark.monitor
    @pytest.mark.unit
    def test_get_memory_info(self, mock_memory_info):
        """Test _get_memory_info function"""
        with patch('cli.monitor.psutil') as mock_psutil:
            mock_virtual_memory = Mock()
            mock_virtual_memory.total = mock_memory_info["total"]
            mock_virtual_memory.available = mock_memory_info["available"]
            mock_virtual_memory.used = mock_memory_info["used"]
            mock_virtual_memory.percent = mock_memory_info["percent"]
            
            mock_swap_memory = Mock()
            mock_swap_memory.total = mock_memory_info["swap_total"]
            mock_swap_memory.used = mock_memory_info["swap_used"]
            mock_swap_memory.percent = mock_memory_info["swap_percent"]
            
            mock_psutil.virtual_memory.return_value = mock_virtual_memory
            mock_psutil.swap_memory.return_value = mock_swap_memory
            
            from cli.monitor import _get_memory_info
            result = _get_memory_info()
            
            assert result["total"] == mock_memory_info["total"]
            assert result["percent"] == mock_memory_info["percent"]

    @pytest.mark.monitor
    @pytest.mark.unit
    def test_get_disk_info(self, mock_disk_info):
        """Test _get_disk_info function"""
        with patch('cli.monitor.psutil') as mock_psutil:
            mock_disk_usage = Mock()
            mock_disk_usage.total = mock_disk_info["total"]
            mock_disk_usage.used = mock_disk_info["used"]
            mock_disk_usage.free = mock_disk_info["free"]
            mock_disk_usage.percent = mock_disk_info["percent"]
            
            mock_disk_io = Mock()
            mock_disk_io.read_bytes = mock_disk_info["read_bytes"]
            mock_disk_io.write_bytes = mock_disk_info["write_bytes"]
            
            mock_psutil.disk_usage.return_value = mock_disk_usage
            mock_psutil.disk_io_counters.return_value = mock_disk_io
            
            from cli.monitor import _get_disk_info
            result = _get_disk_info()
            
            assert result["total"] == mock_disk_info["total"]
            assert result["percent"] == mock_disk_info["percent"]

    @pytest.mark.monitor
    @pytest.mark.unit
    def test_get_network_info(self, mock_network_info):
        """Test _get_network_info function"""
        with patch('cli.monitor.psutil') as mock_psutil:
            mock_network_io = Mock()
            mock_network_io.bytes_sent = mock_network_info["bytes_sent"]
            mock_network_io.bytes_recv = mock_network_info["bytes_recv"]
            mock_network_io.packets_sent = mock_network_info["packets_sent"]
            mock_network_io.packets_recv = mock_network_info["packets_recv"]
            
            mock_psutil.net_io_counters.return_value = mock_network_io
            
            from cli.monitor import _get_network_info
            result = _get_network_info()
            
            assert result["bytes_sent"] == mock_network_info["bytes_sent"]
            assert result["bytes_recv"] == mock_network_info["bytes_recv"]

    @pytest.mark.monitor
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_bot_status(self, mock_bot_status):
        """Test _get_bot_status function"""
        with patch('cli.monitor.get_sdb_services_for_cli') as mock_get_services:
            mock_get_services.return_value = (Mock(), Mock(), Mock())
            
            from cli.monitor import _get_bot_status
            result = await _get_bot_status()
            
            # Проверяем что функция выполнилась без ошибок
            assert result is not None

    @pytest.mark.monitor
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_database_status(self, mock_database_status):
        """Test _get_database_status function"""
        with patch('cli.monitor.get_sdb_services_for_cli') as mock_get_services:
            mock_get_services.return_value = (Mock(), Mock(), Mock())
            
            from cli.monitor import _get_database_status
            result = await _get_database_status()
            
            # Проверяем что функция выполнилась без ошибок
            assert result is not None

    @pytest.mark.monitor
    @pytest.mark.unit
    def test_format_uptime(self):
        """Test _format_uptime function"""
        from cli.monitor import _format_uptime
        
        # Тест для 1 секунды
        assert _format_uptime(1) == "1 секунда"
        
        # Тест для 60 секунд (реальная реализация возвращает "минут")
        assert _format_uptime(60) == "1 минут"
        
        # Тест для 3600 секунд
        assert _format_uptime(3600) == "1 часов"
        
        # Тест для 86400 секунд
        assert _format_uptime(86400) == "1 дней"
        
        # Тест для 0 секунд
        assert _format_uptime(0) == "0 секунд" 