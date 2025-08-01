# modules/security_integrations.py
"""
Модуль интеграций с внешними сервисами безопасности
"""

import asyncio
import aiohttp
import json
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from datetime import datetime, timedelta
import ssl
import socket
import subprocess
import platform
import os
import shutil

logger = logging.getLogger(__name__)

class SecurityIntegrations:
    """Класс для интеграций с внешними сервисами безопасности"""
    
    def __init__(self):
        self.config = self._load_config()
        self.session = None
        self.system_info = self._detect_system()
    
    def _detect_system(self) -> Dict[str, Any]:
        """Определение системы и доступных инструментов"""
        system_info = {
            "os": platform.system().lower(),
            "is_root": os.geteuid() == 0,
            "is_container": self._is_container(),
            "available_tools": {}
        }
        
        # Проверяем доступные инструменты
        tools_to_check = ["nmap", "sslyze", "openssl", "curl", "wget"]
        for tool in tools_to_check:
            system_info["available_tools"][tool] = shutil.which(tool) is not None
        
        return system_info
    
    def _is_container(self) -> bool:
        """Определение, запущены ли мы в контейнере"""
        try:
            with open("/proc/1/cgroup", "r") as f:
                return any("docker" in line or "kubepods" in line for line in f)
        except:
            return False
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации интеграций"""
        config_file = Path("config/security_integrations.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка загрузки конфигурации: {e}")
        
        return {
            "virustotal": {
                "enabled": False,
                "api_key": "",
                "base_url": "https://www.virustotal.com/vtapi/v2"
            },
            "shodan": {
                "enabled": False,
                "api_key": "",
                "base_url": "https://api.shodan.io"
            },
            "abuseipdb": {
                "enabled": False,
                "api_key": "",
                "base_url": "https://api.abuseipdb.com/api/v2"
            },
            "securitytrails": {
                "enabled": False,
                "api_key": "",
                "base_url": "https://api.securitytrails.com/v1"
            },
            "local_scanners": {
                "nmap": True,
                "sslyze": True,
                "openvas": False
            },
            "scan_options": {
                "privileged_mode": False,
                "timeout": 300,
                "max_retries": 3
            }
        }
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
    
    # === VIRUSTOTAL INTEGRATION ===
    
    async def virustotal_scan_file(self, file_path: str) -> Dict[str, Any]:
        """Сканирование файла через VirusTotal"""
        if not self.config["virustotal"]["enabled"]:
            return {"error": "VirusTotal не настроен"}
        
        try:
            # Читаем файл
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Вычисляем SHA-256 хеш
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Проверяем хеш в VirusTotal
            result = await self._virustotal_check_hash(file_hash)
            
            if result.get("response_code") == 0:
                # Файл не найден, загружаем его
                result = await self._virustotal_upload_file(file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка сканирования файла в VirusTotal: {e}")
            return {"error": str(e)}
    
    async def _virustotal_check_hash(self, file_hash: str) -> Dict[str, Any]:
        """Проверка хеша файла в VirusTotal"""
        url = f"{self.config['virustotal']['base_url']}/file/report"
        params = {
            "apikey": self.config["virustotal"]["api_key"],
            "resource": file_hash
        }
        
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def _virustotal_upload_file(self, file_path: str) -> Dict[str, Any]:
        """Загрузка файла в VirusTotal для сканирования"""
        url = f"{self.config['virustotal']['base_url']}/file/scan"
        
        with open(file_path, 'rb') as f:
            files = {"file": f}
            data = {"apikey": self.config["virustotal"]["api_key"]}
            
            async with self.session.post(url, data=data, files=files) as response:
                return await response.json()
    
    async def virustotal_scan_url(self, url: str) -> Dict[str, Any]:
        """Сканирование URL через VirusTotal"""
        if not self.config["virustotal"]["enabled"]:
            return {"error": "VirusTotal не настроен"}
        
        try:
            vt_url = f"{self.config['virustotal']['base_url']}/url/report"
            params = {
                "apikey": self.config["virustotal"]["api_key"],
                "resource": url
            }
            
            async with self.session.get(vt_url, params=params) as response:
                return await response.json()
                
        except Exception as e:
            logger.error(f"Ошибка сканирования URL в VirusTotal: {e}")
            return {"error": str(e)}
    
    # === SHODAN INTEGRATION ===
    
    async def shodan_host_info(self, ip: str) -> Dict[str, Any]:
        """Получение информации о хосте через Shodan"""
        if not self.config["shodan"]["enabled"]:
            return {"error": "Shodan не настроен"}
        
        try:
            url = f"{self.config['shodan']['base_url']}/shodan/host/{ip}"
            params = {"key": self.config["shodan"]["api_key"]}
            
            async with self.session.get(url, params=params) as response:
                return await response.json()
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о хосте в Shodan: {e}")
            return {"error": str(e)}
    
    async def shodan_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Поиск в Shodan"""
        if not self.config["shodan"]["enabled"]:
            return {"error": "Shodan не настроен"}
        
        try:
            url = f"{self.config['shodan']['base_url']}/shodan/host/search"
            params = {
                "key": self.config["shodan"]["api_key"],
                "query": query,
                "limit": limit
            }
            
            async with self.session.get(url, params=params) as response:
                return await response.json()
                
        except Exception as e:
            logger.error(f"Ошибка поиска в Shodan: {e}")
            return {"error": str(e)}
    
    # === ABUSEIPDB INTEGRATION ===
    
    async def abuseipdb_check_ip(self, ip: str) -> Dict[str, Any]:
        """Проверка IP в AbuseIPDB"""
        if not self.config["abuseipdb"]["enabled"]:
            return {"error": "AbuseIPDB не настроен"}
        
        try:
            url = f"{self.config['abuseipdb']['base_url']}/check"
            params = {
                "ipAddress": ip,
                "maxAgeInDays": 90
            }
            headers = {
                "Key": self.config["abuseipdb"]["api_key"],
                "Accept": "application/json"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                return await response.json()
                
        except Exception as e:
            logger.error(f"Ошибка проверки IP в AbuseIPDB: {e}")
            return {"error": str(e)}
    
    async def abuseipdb_report_ip(self, ip: str, categories: List[str], comment: str = "") -> Dict[str, Any]:
        """Отправка жалобы на IP в AbuseIPDB"""
        if not self.config["abuseipdb"]["enabled"]:
            return {"error": "AbuseIPDB не настроен"}
        
        try:
            url = f"{self.config['abuseipdb']['base_url']}/report"
            data = {
                "ip": ip,
                "categories": ",".join(categories),
                "comment": comment
            }
            headers = {
                "Key": self.config["abuseipdb"]["api_key"],
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with self.session.post(url, data=data, headers=headers) as response:
                return await response.json()
                
        except Exception as e:
            logger.error(f"Ошибка отправки жалобы в AbuseIPDB: {e}")
            return {"error": str(e)}
    
    # === SECURITYTRAILS INTEGRATION ===
    
    async def securitytrails_domain_info(self, domain: str) -> Dict[str, Any]:
        """Получение информации о домене через SecurityTrails"""
        if not self.config["securitytrails"]["enabled"]:
            return {"error": "SecurityTrails не настроен"}
        
        try:
            url = f"{self.config['securitytrails']['base_url']}/domain/{domain}/general"
            headers = {
                "APIKEY": self.config["securitytrails"]["api_key"]
            }
            
            async with self.session.get(url, headers=headers) as response:
                return await response.json()
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о домене в SecurityTrails: {e}")
            return {"error": str(e)}
    
    async def securitytrails_subdomains(self, domain: str) -> Dict[str, Any]:
        """Получение поддоменов через SecurityTrails"""
        if not self.config["securitytrails"]["enabled"]:
            return {"error": "SecurityTrails не настроен"}
        
        try:
            url = f"{self.config['securitytrails']['base_url']}/domain/{domain}/subdomains"
            headers = {
                "APIKEY": self.config["securitytrails"]["api_key"]
            }
            
            async with self.session.get(url, headers=headers) as response:
                return await response.json()
                
        except Exception as e:
            logger.error(f"Ошибка получения поддоменов в SecurityTrails: {e}")
            return {"error": str(e)}
    
    # === LOCAL SECURITY SCANNERS ===
    
    async def nmap_scan(self, target: str, scan_type: str = "basic") -> Dict[str, Any]:
        """Сканирование с помощью Nmap"""
        if not self.config["local_scanners"]["nmap"]:
            return {"error": "Nmap не настроен"}
        
        if not self.system_info["available_tools"]["nmap"]:
            return {"error": "Nmap не установлен в системе"}
        
        try:
            # Определяем параметры сканирования в зависимости от прав
            if scan_type == "basic":
                if self.system_info["is_root"] and not self.system_info["is_container"]:
                    args = ["nmap", "-sS", "-sV", "-O", target]
                else:
                    args = ["nmap", "-sV", target]
            elif scan_type == "full":
                if self.system_info["is_root"] and not self.system_info["is_container"]:
                    args = ["nmap", "-sS", "-sV", "-O", "-A", "--script=vuln", target]
                else:
                    args = ["nmap", "-sV", "-A", target]
            elif scan_type == "quick":
                args = ["nmap", "-F", target]
            else:
                return {"error": f"Неизвестный тип сканирования: {scan_type}"}
            
            # Выполняем сканирование
            result = subprocess.run(args, capture_output=True, text=True, timeout=self.config["scan_options"]["timeout"])
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "scan_type": scan_type,
                "target": target,
                "privileged": self.system_info["is_root"] and not self.system_info["is_container"]
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Сканирование Nmap превысило лимит времени"}
        except Exception as e:
            logger.error(f"Ошибка сканирования Nmap: {e}")
            return {"error": str(e), "error_details": f"Exception: {type(e).__name__}: {e}"}
    
    async def sslyze_scan(self, target: str, port: int = 443) -> Dict[str, Any]:
        """Сканирование SSL с помощью SSLyze"""
        if not self.config["local_scanners"]["sslyze"]:
            return {"error": "SSLyze не настроен"}
        
        if not self.system_info["available_tools"]["sslyze"]:
            return {"error": "SSLyze не установлен в системе"}
        
        try:
            # Выполняем сканирование
            args = ["sslyze", "--regular", f"{target}:{port}"]
            result = subprocess.run(args, capture_output=True, text=True, timeout=60)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "target": f"{target}:{port}"
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Сканирование SSLyze превысило лимит времени"}
        except Exception as e:
            logger.error(f"Ошибка сканирования SSLyze: {e}")
            return {"error": str(e)}
    
    async def openssl_scan(self, target: str, port: int = 443) -> Dict[str, Any]:
        """Сканирование SSL с помощью OpenSSL"""
        if not self.system_info["available_tools"]["openssl"]:
            return {"error": "OpenSSL не установлен в системе"}
        
        try:
            # Проверяем SSL сертификат
            cmd = f"echo | openssl s_client -servername {target} -connect {target}:{port} 2>/dev/null | openssl x509 -noout -dates"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "target": f"{target}:{port}"
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Сканирование OpenSSL превысило лимит времени"}
        except Exception as e:
            logger.error(f"Ошибка сканирования OpenSSL: {e}")
            return {"error": str(e)}
    
    # === SYSTEM INFORMATION ===
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            "os": self.system_info["os"],
            "is_root": self.system_info["is_root"],
            "is_container": self.system_info["is_container"],
            "available_tools": self.system_info["available_tools"],
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Получение рекомендаций для улучшения безопасности"""
        recommendations = []
        
        if self.system_info["is_container"]:
            recommendations.append("⚠️ Запущено в контейнере - некоторые функции могут быть ограничены")
        
        if not self.system_info["is_root"]:
            recommendations.append("⚠️ Не запущено от root - некоторые сканеры могут работать ограниченно")
        
        if not self.system_info["available_tools"]["nmap"]:
            recommendations.append("📦 Установите nmap для полного сетевого сканирования")
        
        if not self.system_info["available_tools"]["sslyze"]:
            recommendations.append("📦 Установите sslyze для анализа SSL/TLS")
        
        if not self.system_info["available_tools"]["openssl"]:
            recommendations.append("📦 Установите openssl для базового SSL анализа")
        
        return recommendations
    
    # === COMPREHENSIVE SECURITY AUDIT ===
    
    async def comprehensive_audit(self, target: str) -> Dict[str, Any]:
        """Комплексный аудит безопасности"""
        audit_results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "system_info": self.get_system_info(),
            "results": {}
        }
        
        try:
            # 1. Проверка в AbuseIPDB
            if self.config["abuseipdb"]["enabled"]:
                audit_results["results"]["abuseipdb"] = await self.abuseipdb_check_ip(target)
            
            # 2. Информация о хосте в Shodan
            if self.config["shodan"]["enabled"]:
                audit_results["results"]["shodan"] = await self.shodan_host_info(target)
            
            # 3. Nmap сканирование
            if self.config["local_scanners"]["nmap"] and self.system_info["available_tools"]["nmap"]:
                audit_results["results"]["nmap"] = await self.nmap_scan(target, "basic")
            
            # 4. SSL сканирование
            if self.config["local_scanners"]["sslyze"] and self.system_info["available_tools"]["sslyze"]:
                audit_results["results"]["sslyze"] = await self.sslyze_scan(target)
            elif self.system_info["available_tools"]["openssl"]:
                audit_results["results"]["openssl"] = await self.openssl_scan(target)
            
            # 5. Проверка DNS и доменной информации
            if "." in target and self.config["securitytrails"]["enabled"]:
                audit_results["results"]["securitytrails"] = await self.securitytrails_domain_info(target)
            
            return audit_results
            
        except Exception as e:
            logger.error(f"Ошибка комплексного аудита: {e}")
            return {"error": str(e)}
    
    # === UTILITY METHODS ===
    
    def get_config(self) -> Dict[str, Any]:
        """Получение конфигурации"""
        return self.config
    
    def update_config(self, new_config: Dict[str, Any]):
        """Обновление конфигурации"""
        self.config.update(new_config)
        self._save_config()
    
    def _save_config(self):
        """Сохранение конфигурации"""
        config_file = Path("config/security_integrations.json")
        config_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")

# Экспорт для использования в CLI
security_integrations = SecurityIntegrations() 