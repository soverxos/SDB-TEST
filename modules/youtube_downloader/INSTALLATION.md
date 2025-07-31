# 🚀 Инструкция по интеграции YouTube Downloader модуля

## 📋 Шаги интеграции

### 1. Установка зависимостей

```bash
cd /root/SwiftDevBot
pip install yt-dlp>=2023.7.6 aiofiles>=23.0.0
```

### 2. Установка FFmpeg (если не установлен)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Применение миграции базы данных

```bash
./sdb.py db upgrade
```

### 4. Активация модуля

```bash
./sdb.py module enable youtube_downloader
```

### 5. Настройка разрешений

```bash
# Дать базовые разрешения пользователям
./sdb.py role add-permission user_role youtube_downloader.access_user_features
./sdb.py role add-permission user_role youtube_downloader.download_video
./sdb.py role add-permission user_role youtube_downloader.download_audio
./sdb.py role add-permission user_role youtube_downloader.view_history

# Дать админские права администраторам
./sdb.py role add-permission admin_role youtube_downloader.admin_manage
```

### 6. Создание папки для загрузок

```bash
mkdir -p /root/SwiftDevBot/project_data/youtube_downloads
chmod 755 /root/SwiftDevBot/project_data/youtube_downloads
```

### 7. Настройка конфигурации (опционально)

Отредактируйте файл `modules/youtube_downloader/module_settings.yaml`:

```yaml
# Настройки загрузок
download_directory: "project_data/youtube_downloads"
auto_cleanup_days: 7
max_concurrent_downloads: 3

# Настройки по умолчанию
default_video_quality: "720p"
default_audio_quality: "192"

# Уведомления
notify_on_completion: true
notify_admin_on_errors: true

# Лимиты
max_downloads_per_user_per_day: 10
max_file_size_mb: 100
```

### 8. Перезапуск бота

```bash
./sdb.py restart
```

## 📝 Проверка работы

### 1. Проверка статуса модуля

```bash
./sdb.py module status youtube_downloader
```

### 2. Проверка разрешений

```bash
./sdb.py role list-permissions user_role | grep youtube
```

### 3. Проверка таблицы в БД

```bash
./sdb.py db shell
SELECT name FROM sqlite_master WHERE type='table' AND name='youtube_downloads';
.exit
```

## 🔧 Использование

### Команды для пользователей

1. `/youtube` - Открыть меню YouTube загрузчика
2. Или через меню модулей → "📺 YouTube Загрузчик"

### Процесс загрузки

1. **Выбор типа**: Видео или аудио
2. **Ввод URL**: Любая YouTube ссылка
3. **Выбор качества**: Доступные варианты
4. **Подтверждение**: Информация о видео
5. **Загрузка**: Процесс в фоне
6. **Результат**: Файл отправляется в чат

## 🛠️ Диагностика проблем

### Проверка логов

```bash
tail -f project_data/Logs/bot.log | grep -i youtube
```

### Проверка зависимостей

```bash
python -c "import yt_dlp; print('yt-dlp version:', yt_dlp.version.__version__)"
python -c "import aiofiles; print('aiofiles OK')"
ffmpeg -version | head -1
```

### Проверка разрешений файлов

```bash
ls -la project_data/youtube_downloads/
```

### Тест простой загрузки

```bash
python -c "
import yt_dlp
ydl_opts = {'quiet': True}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ', download=False)
    print('✅ Тест прошел успешно:', info['title'])
"
```

## 🔄 Обновление модуля

### 1. Обновление зависимостей

```bash
pip install -U yt-dlp aiofiles
```

### 2. Применение новых миграций

```bash
./sdb.py db upgrade
```

### 3. Перезапуск

```bash
./sdb.py restart
```

## 🎯 Возможные проблемы и решения

### "Модуль не загружается"

1. Проверьте синтаксис Python файлов
2. Убедитесь в наличии всех зависимостей
3. Проверьте логи на ошибки импорта

### "База данных не обновляется"

1. Проверьте, что миграция применена: `./sdb.py db current`
2. Если нет, примените вручную: `./sdb.py db upgrade`

### "FFmpeg не найден"

1. Установите FFmpeg в системе
2. Проверьте PATH: `which ffmpeg`
3. Перезапустите бота после установки

### "Файлы не скачиваются"

1. Проверьте права на папку загрузок
2. Убедитесь в доступности YouTube
3. Проверьте логи на ошибки yt-dlp

### "Ошибки разрешений"

1. Проверьте права пользователя: `./sdb.py user info USERNAME`
2. Добавьте нужные разрешения: `./sdb.py user add-permission USERNAME PERMISSION`

---

**💡 Совет**: После интеграции рекомендуется протестировать модуль с простым коротким видео для проверки всех компонентов.
