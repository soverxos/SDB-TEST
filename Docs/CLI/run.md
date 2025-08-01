# 🚀 Запуск системы (run)

## Обзор

Модуль `run` предоставляет инструменты для запуска SwiftDevBot в различных режимах, включая разработку, продакшн, отладку и тестирование. Поддерживает запуск всех компонентов системы.

## Основные команды

### `python sdb run`

Запускает SwiftDevBot в стандартном режиме.

**Опции:**
- `--mode production/development/debug` - режим работы
- `--daemon` - запуск в фоновом режиме
- `--config FILE` - файл конфигурации
- `--log-level LEVEL` - уровень логирования

**Примеры:**

```bash
# Запустить в продакшн режиме
python sdb run

# Запустить в режиме разработки
python sdb run --mode development

# Запустить в фоновом режиме
python sdb run --daemon

# Запустить с кастомной конфигурацией
python sdb run --config custom_config.yaml
```

**Результат:**
```
🚀 Запуск SwiftDevBot-Lite...

📋 Проверка системы:
   ✅ Python версия: 3.11.0
   ✅ Зависимости: Установлены
   ✅ Конфигурация: Загружена
   ✅ База данных: Подключена

📱 Telegram Bot:
   ✅ Токен: Проверен
   ✅ Подключение: Успешно
   ✅ Статус: Запущен (PID: 1234)
   📊 Режим: production



🌐 Web Server:
   ✅ Порт: 8000
   ✅ Статус: Запущен (PID: 1236)
   📊 Режим: production

📊 Общая статистика:
   🟢 Все компоненты запущены успешно
   ⏱️ Время запуска: 3.2 секунды
   📈 Готов к работе
```

### `python sdb run dev`

Запускает систему в режиме разработки.

**Опции:**
- `--hot-reload` - автоматическая перезагрузка при изменениях
- `--debug` - включить отладку
- `--port PORT` - порт для веб-сервера
- `--log-level DEBUG` - уровень логирования

**Примеры:**

```bash
# Запустить в режиме разработки
python sdb run dev

# С автоматической перезагрузкой
python sdb run dev --hot-reload

# С отладкой
python sdb run dev --debug

# На другом порту
python sdb run dev --port 8080
```

**Результат:**
```
🔧 Запуск SwiftDevBot-Lite в режиме разработки...

📋 Настройки разработки:
   ✅ Режим: development
   ✅ Отладка: Включена
   ✅ Hot reload: Включен
   ✅ Логирование: DEBUG

📱 Telegram Bot (dev):
   ✅ Токен: Проверен
   ✅ Подключение: Успешно
   ✅ Статус: Запущен (PID: 1234)
   📊 Режим: development



🌐 Web Server (dev):
   ✅ Порт: 8000
   ✅ Статус: Запущен (PID: 1236)
   📊 Режим: development

📊 Отладочная информация:
   🟢 Все компоненты запущены
   🔍 Отладка активна
   🔄 Hot reload активен
   📈 Готов к разработке
```

### `python sdb run debug`

Запускает систему в режиме отладки.

**Опции:**
- `--breakpoint` - установить точки останова
- `--profile` - профилирование производительности
- `--trace` - трассировка вызовов
- `--verbose` - подробный вывод

**Примеры:**

```bash
# Запустить в режиме отладки
python sdb run debug

# С точками останова
python sdb run debug --breakpoint

# С профилированием
python sdb run debug --profile

# С трассировкой
python sdb run debug --trace
```

**Результат:**
```
🐛 Запуск SwiftDevBot-Lite в режиме отладки...

📋 Настройки отладки:
   ✅ Режим: debug
   ✅ Отладчик: Включен
   ✅ Точки останова: Активны
   ✅ Трассировка: Включена

📱 Telegram Bot (debug):
   ✅ Токен: Проверен
   ✅ Подключение: Успешно
   ✅ Статус: Запущен (PID: 1234)
   📊 Режим: debug



🌐 Web Server (debug):
   ✅ Порт: 8000
   ✅ Статус: Запущен (PID: 1236)
   📊 Режим: debug

📊 Отладочная информация:
   🟢 Все компоненты запущены
   🐛 Отладчик активен
   📊 Профилирование: Включено
   📈 Готов к отладке
```

### `python sdb run test`

Запускает систему в тестовом режиме.

**Опции:**
- `--coverage` - включить покрытие кода
- `--unit` - только модульные тесты
- `--integration` - только интеграционные тесты
- `--output FILE` - файл для результатов

**Примеры:**

```bash
# Запустить тесты
python sdb run test

# С покрытием кода
python sdb run test --coverage

# Только модульные тесты
python sdb run test --unit

# Только интеграционные тесты
python sdb run test --integration
```

**Результат:**
```
🧪 Запуск SwiftDevBot-Lite в тестовом режиме...

📋 Настройки тестирования:
   ✅ Режим: test
   ✅ Покрытие: Включено
   ✅ Модульные тесты: Активны
   ✅ Интеграционные тесты: Активны

📱 Telegram Bot (test):
   ✅ Токен: Тестовый
   ✅ Подключение: Успешно
   ✅ Статус: Запущен (PID: 1234)
   📊 Режим: test



🌐 Web Server (test):
   ✅ Порт: 8001
   ✅ Статус: Запущен (PID: 1236)
   📊 Режим: test

📊 Тестовая информация:
   🟢 Все компоненты запущены
   🧪 Тесты активны
   📊 Покрытие: 85%
   📈 Готов к тестированию
```

### `python sdb run production`

Запускает систему в продакшн режиме.

**Опции:**
- `--workers N` - количество воркеров
- `--max-connections N` - максимальное количество соединений
- `--timeout SECONDS` - таймаут соединений
- `--ssl` - включить SSL

**Примеры:**

```bash
# Запустить в продакшн режиме
python sdb run production

# С несколькими воркерами
python sdb run production --workers 4

# С SSL
python sdb run production --ssl

# С настройками производительности
python sdb run production --max-connections 1000
```

**Результат:**
```
🏭 Запуск SwiftDevBot-Lite в продакшн режиме...

📋 Продакшн настройки:
   ✅ Режим: production
   ✅ Воркеры: 4
   ✅ SSL: Включен
   ✅ Макс. соединений: 1000

📱 Telegram Bot (production):
   ✅ Токен: Проверен
   ✅ Подключение: Успешно
   ✅ Статус: Запущен (PID: 1234)
   📊 Режим: production



🌐 Web Server (production):
   ✅ Порт: 443 (SSL)
   ✅ Статус: Запущен (PID: 1236)
   📊 Режим: production

📊 Продакшн информация:
   🟢 Все компоненты запущены
   🔒 SSL активен
   📈 Высокая производительность
   🚀 Готов к продакшн работе
```

## Расширенные команды (в разработке)

### `python sdb run cluster`

Запускает систему в кластерном режиме.

**Опции:**
- `--nodes N` - количество узлов
- `--load-balancer` - включить балансировщик нагрузки
- `--auto-scale` - автоматическое масштабирование
- `--monitor` - мониторинг кластера

**Примеры:**

```bash
# Запустить кластер
python sdb run cluster

# С несколькими узлами
python sdb run cluster --nodes 3

# С балансировщиком нагрузки
python sdb run cluster --load-balancer

# С авто-масштабированием
python sdb run cluster --auto-scale
```

### `python sdb run docker`

Запускает систему в Docker контейнере.

**Опции:**
- `--image IMAGE` - образ Docker
- `--port PORT` - порт для проброса
- `--volume PATH` - монтирование томов
- `--env KEY=VALUE` - переменные окружения

**Примеры:**

```bash
# Запустить в Docker
python sdb run docker

# С кастомным образом
python sdb run docker --image swiftdevbot:latest

# С пробросом портов
python sdb run docker --port 8000:8000

# С переменными окружения
python sdb run docker --env DEBUG=true
```

### `python sdb run k8s`

Запускает систему в Kubernetes.

**Опции:**
- `--namespace NAMESPACE` - пространство имен
- `--replicas N` - количество реплик
- `--service TYPE` - тип сервиса
- `--ingress` - включить Ingress

**Примеры:**

```bash
# Запустить в Kubernetes
python sdb run k8s

# В определенном namespace
python sdb run k8s --namespace production

# С несколькими репликами
python sdb run k8s --replicas 3

# С Ingress
python sdb run k8s --ingress
```

### `python sdb run microservice`

Запускает систему в микросервисном режиме.

**Опции:**
- `--service SERVICE` - конкретный сервис
- `--discovery` - включить service discovery
- `--circuit-breaker` - включить circuit breaker
- `--metrics` - включить метрики

**Примеры:**

```bash
# Запустить микросервисы
python sdb run microservice

# Конкретный сервис
python sdb run microservice --service telegram-bot

# С service discovery
python sdb run microservice --discovery

# С circuit breaker
python sdb run microservice --circuit-breaker
```

### `python sdb run serverless`

Запускает систему в serverless режиме.

**Опции:**
- `--provider aws/azure/gcp` - облачный провайдер
- `--function FUNCTION` - конкретная функция
- `--memory MB` - объем памяти
- `--timeout SECONDS` - таймаут выполнения

**Примеры:**

```bash
# Запустить в serverless режиме
python sdb run serverless

# На AWS Lambda
python sdb run serverless --provider aws

# Конкретная функция
python sdb run serverless --function telegram-webhook

# С настройками памяти
python sdb run serverless --memory 512
```

### `python sdb run benchmark`

Запускает бенчмарки системы.

**Опции:**
- `--duration SECONDS` - продолжительность тестов
- `--concurrent N` - количество одновременных запросов
- `--output FILE` - файл для результатов
- `--compare` - сравнить с предыдущими результатами

**Примеры:**

```bash
# Запустить бенчмарки
python sdb run benchmark

# Длительный тест
python sdb run benchmark --duration 300

# С высокой нагрузкой
python sdb run benchmark --concurrent 1000

# Сохранение результатов
python sdb run benchmark --output benchmark_results.json
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb run production --max-connections 0` - блокировка всех соединений
- `python sdb run debug --breakpoint` - остановка системы в точках останова
- `python sdb run test --coverage` - может замедлить систему

### ⚠️ Опасные команды:
- `python sdb run dev --hot-reload` - автоматическая перезагрузка
- `python sdb run debug --trace` - трассировка может замедлить систему
- `python sdb run benchmark --concurrent 10000` - высокая нагрузка

### ✅ Безопасные команды:
- `python sdb run` - стандартный запуск
- `python sdb run dev` - режим разработки
- `python sdb run test` - тестовый режим

## Устранение проблем

### Проблема: "Система не запускается"
```bash
# Проверить зависимости
python sdb system status

# Запустить в режиме отладки
python sdb run debug

# Проверить логи
python sdb system logs
```

### Проблема: "Высокая нагрузка"
```bash
# Запустить с ограничениями
python sdb run production --max-connections 100

# Мониторинг процессов
python sdb process monitor

# Оптимизация
python sdb process optimize --auto
```

### Проблема: "Ошибки в продакшн"
```bash
# Запустить в режиме отладки
python sdb run debug --verbose

# Проверить конфигурацию
python sdb config show

# Тестирование
python sdb run test --integration
```

## Рекомендации

1. **Режимы**: Используйте правильный режим для задачи
2. **Мониторинг**: Следите за производительностью
3. **Тестирование**: Всегда тестируйте перед продакшн
4. **Безопасность**: Используйте SSL в продакшн
5. **Масштабирование**: Планируйте рост нагрузки 