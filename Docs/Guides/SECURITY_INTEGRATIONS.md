# 🔒 Интеграции безопасности SwiftDevBot-Lite

## Обзор

Модуль интеграций безопасности предоставляет возможность взаимодействия с внешними сервисами безопасности для комплексного аудита и мониторинга.

## Поддерживаемые сервисы

### 🌐 Внешние сервисы

#### 1. **VirusTotal**
- **Описание**: Сканирование файлов и URL на вирусы
- **API**: https://www.virustotal.com/vtapi/v2
- **Функции**:
  - Сканирование файлов
  - Сканирование URL
  - Проверка хешей файлов

#### 2. **Shodan**
- **Описание**: Поисковая система для интернет-устройств
- **API**: https://api.shodan.io
- **Функции**:
  - Информация о хостах
  - Поиск устройств
  - Анализ открытых портов

#### 3. **AbuseIPDB**
- **Описание**: База данных вредоносных IP-адресов
- **API**: https://api.abuseipdb.com/api/v2
- **Функции**:
  - Проверка IP на вредоносность
  - Отправка жалоб на IP
  - Анализ репутации

#### 4. **SecurityTrails**
- **Описание**: Информация о доменах и DNS
- **API**: https://api.securitytrails.com/v1
- **Функции**:
  - Информация о доменах
  - Поиск поддоменов
  - DNS записи

### 🔧 Локальные сканеры

#### 1. **Nmap**
- **Описание**: Сканер портов и сетевой разведки
- **Функции**:
  - Базовое сканирование (`-sS -sV -O`)
  - Полное сканирование (`-sS -sV -O -A --script=vuln`)
  - Быстрое сканирование (`-F`)

#### 2. **SSLyze**
- **Описание**: Сканер SSL/TLS уязвимостей
- **Функции**:
  - Анализ SSL сертификатов
  - Проверка уязвимостей
  - Тестирование шифрования

## Установка и настройка

### 1. Установка зависимостей

```bash
# Активируем виртуальное окружение
source .venv/bin/activate

# Устанавливаем зависимости
pip install aiohttp
```

### 2. Настройка API ключей

#### VirusTotal
1. Зарегистрируйтесь на https://www.virustotal.com
2. Получите API ключ в настройках
3. Настройте ключ:
```bash
python sdb.py security integrations config --service virustotal --api-key YOUR_API_KEY
```

#### Shodan
1. Зарегистрируйтесь на https://account.shodan.io
2. Получите API ключ
3. Настройте ключ:
```bash
python sdb.py security integrations config --service shodan --api-key YOUR_API_KEY
```

#### AbuseIPDB
1. Зарегистрируйтесь на https://www.abuseipdb.com
2. Получите API ключ
3. Настройте ключ:
```bash
python sdb.py security integrations config --service abuseipdb --api-key YOUR_API_KEY
```

#### SecurityTrails
1. Зарегистрируйтесь на https://securitytrails.com
2. Получите API ключ
3. Настройте ключ:
```bash
python sdb.py security integrations config --service securitytrails --api-key YOUR_API_KEY
```

### 3. Установка локальных сканеров

#### Nmap
```bash
# Ubuntu/Debian
sudo apt-get install nmap

# CentOS/RHEL
sudo yum install nmap

# macOS
brew install nmap
```

#### SSLyze
```bash
# Установка через pip
pip install sslyze

# Или через систему пакетов
sudo apt-get install sslyze
```

## Использование

### 1. Управление конфигурацией

```bash
# Просмотр текущей конфигурации
python sdb.py security integrations config

# Настройка API ключа
python sdb.py security integrations config --service virustotal --api-key YOUR_KEY

# Тестирование интеграций
python sdb.py security integrations test
```

### 2. Сканирование через внешние сервисы

#### VirusTotal
```bash
# Сканирование файла
python sdb.py security integrations virustotal --target /path/to/file

# Сканирование URL
python sdb.py security integrations virustotal --target https://example.com
```

#### Shodan
```bash
# Информация о хосте
python sdb.py security integrations shodan --target 8.8.8.8
```

#### AbuseIPDB
```bash
# Проверка IP
python sdb.py security integrations abuseipdb --target 192.168.1.1
```

#### SecurityTrails
```bash
# Информация о домене
python sdb.py security integrations securitytrails --target example.com
```

### 3. Локальное сканирование

#### Nmap
```bash
# Базовое сканирование
python sdb.py security integrations nmap --target 192.168.1.1

# Полное сканирование
python sdb.py security integrations nmap --target 192.168.1.1 --scan-type full

# Быстрое сканирование
python sdb.py security integrations nmap --target 192.168.1.1 --scan-type quick
```

#### SSLyze
```bash
# SSL сканирование
python sdb.py security integrations sslyze --target example.com
```

### 4. Комплексный аудит

```bash
# Комплексный аудит безопасности
python sdb.py security integrations comprehensive --target example.com
```

## Примеры использования

### Пример 1: Проверка подозрительного файла

```bash
# 1. Сканируем файл через VirusTotal
python sdb.py security integrations virustotal --target suspicious_file.exe

# 2. Проверяем домен источника через SecurityTrails
python sdb.py security integrations securitytrails --target malicious-domain.com

# 3. Проверяем IP через AbuseIPDB
python sdb.py security integrations abuseipdb --target 192.168.1.100
```

### Пример 2: Аудит веб-сервера

```bash
# 1. Сканируем порты с помощью Nmap
python sdb.py security integrations nmap --target web-server.com --scan-type full

# 2. Проверяем SSL сертификат
python sdb.py security integrations sslyze --target web-server.com

# 3. Получаем информацию о хосте через Shodan
python sdb.py security integrations shodan --target web-server.com

# 4. Комплексный аудит
python sdb.py security integrations comprehensive --target web-server.com
```

### Пример 3: Мониторинг сети

```bash
# Создаем скрипт для регулярного мониторинга
#!/bin/bash

# Сканируем сеть
python sdb.py security integrations nmap --target 192.168.1.0/24 --scan-type quick

# Проверяем подозрительные IP
for ip in $(cat suspicious_ips.txt); do
    python sdb.py security integrations abuseipdb --target $ip
    python sdb.py security integrations shodan --target $ip
done
```

## Конфигурация

### Файл конфигурации

Конфигурация хранится в `config/security_integrations.json`:

```json
{
  "virustotal": {
    "enabled": true,
    "api_key": "your_api_key_here",
    "base_url": "https://www.virustotal.com/vtapi/v2"
  },
  "shodan": {
    "enabled": true,
    "api_key": "your_api_key_here",
    "base_url": "https://api.shodan.io"
  },
  "abuseipdb": {
    "enabled": true,
    "api_key": "your_api_key_here",
    "base_url": "https://api.abuseipdb.com/api/v2"
  },
  "securitytrails": {
    "enabled": true,
    "api_key": "your_api_key_here",
    "base_url": "https://api.securitytrails.com/v1"
  },
  "local_scanners": {
    "nmap": true,
    "sslyze": true,
    "openvas": false
  }
}
```

### Переменные окружения

Можно использовать переменные окружения для API ключей:

```bash
export VIRUSTOTAL_API_KEY="your_key"
export SHODAN_API_KEY="your_key"
export ABUSEIPDB_API_KEY="your_key"
export SECURITYTRAILS_API_KEY="your_key"
```

## Ограничения и лимиты

### VirusTotal
- Лимит: 4 запроса в минуту для бесплатного аккаунта
- Размер файла: до 32 МБ
- Поддерживаемые форматы: все основные

### Shodan
- Лимит: 1 запрос в секунду для бесплатного аккаунта
- Ограничения на поисковые запросы

### AbuseIPDB
- Лимит: 1000 запросов в день для бесплатного аккаунта
- Требуется регистрация для отправки жалоб

### SecurityTrails
- Лимит: 50 запросов в день для бесплатного аккаунта
- Ограниченная информация о доменах

## Безопасность

### Рекомендации

1. **Хранение API ключей**:
   - Используйте переменные окружения
   - Не коммитьте ключи в репозиторий
   - Регулярно ротируйте ключи

2. **Ограничение доступа**:
   - Используйте минимальные права доступа
   - Мониторьте использование API

3. **Логирование**:
   - Включите логирование всех запросов
   - Мониторьте подозрительную активность

### Лучшие практики

1. **Регулярные проверки**:
   - Настройте автоматические проверки
   - Используйте разные сервисы для перекрестной проверки

2. **Анализ результатов**:
   - Не полагайтесь только на один сервис
   - Проверяйте ложные срабатывания

3. **Обновление**:
   - Регулярно обновляйте локальные сканеры
   - Следите за изменениями в API

## Устранение неполадок

### Частые проблемы

1. **Ошибка "API key not found"**:
   - Проверьте правильность API ключа
   - Убедитесь, что сервис включен в конфигурации

2. **Ошибка "Rate limit exceeded"**:
   - Увеличьте интервалы между запросами
   - Рассмотрите платный аккаунт

3. **Ошибка "Scanner not found"**:
   - Установите необходимые сканеры
   - Проверьте PATH переменную

### Отладка

```bash
# Включение подробного логирования
export DEBUG=1
python sdb.py security integrations test

# Проверка конфигурации
python sdb.py security integrations config
```

## Разработка

### Добавление нового сервиса

1. Создайте новый класс в `modules/security_integrations.py`
2. Добавьте конфигурацию в `config/security_integrations.json`
3. Добавьте CLI команды в `cli/security.py`
4. Обновите документацию

### Пример добавления сервиса

```python
# В modules/security_integrations.py
async def new_service_scan(self, target: str) -> Dict[str, Any]:
    """Сканирование через новый сервис"""
    if not self.config["new_service"]["enabled"]:
        return {"error": "NewService не настроен"}
    
    try:
        # Реализация сканирования
        pass
    except Exception as e:
        logger.error(f"Ошибка сканирования в NewService: {e}")
        return {"error": str(e)}
```

## Лицензии и условия использования

- **VirusTotal**: https://www.virustotal.com/gui/terms-of-service
- **Shodan**: https://account.shodan.io/terms
- **AbuseIPDB**: https://www.abuseipdb.com/terms
- **SecurityTrails**: https://securitytrails.com/terms

## Поддержка

Для получения поддержки:
1. Проверьте документацию
2. Посмотрите логи ошибок
3. Создайте issue в репозитории проекта 