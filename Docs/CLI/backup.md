# 💾 Управление бэкапами (backup)

## Обзор

Модуль `backup` предоставляет полный набор команд для создания, управления и восстановления резервных копий SwiftDevBot. Поддерживает как обычные бэкапы, так и "умные" бэкапы с хешированием.

## Основные команды

### `python sdb backup create`

Создает новый бэкап данных и/или базы данных.

**Опции:**
- `--name NAME` - пользовательское имя для бэкапа
- `--db/--no-db` - включить/исключить базу данных (по умолчанию включено)
- `--data-dir DIR` - директории для бэкапа (по умолчанию: config)
- `--compress/--no-compress` - сжимать ли бэкап (по умолчанию включено)
- `--path PATH` - путь для сохранения бэкапа
- `--exclude PATHS` - исключить файлы/папки из бэкапа

**Примеры:**

```bash
# Создать полный бэкап
python sdb backup create

# Создать бэкап с пользовательским именем
python sdb backup create --name "before_update_2024_01_15"

# Создать бэкап только базы данных
python sdb backup create --no-data-dir

# Создать бэкап только данных (без БД)
python sdb backup create --no-db

# Создать бэкап в определенную папку
python sdb backup create --path /tmp/my_backup

# Создать бэкап с исключением логов
python sdb backup create --exclude logs temp cache
```

**Результат:**
```
✅ Бэкап создан: db_sqlite_data_20240115_143022
📁 Расположение: /root/SDB/SwiftDevBot-Lite/backup/db_sqlite_data_20240115_143022/
📊 Размер: 45.2MB
⏱️ Время создания: 2.3 секунды
```

### `python sdb backup list`

Показывает список доступных бэкапов.

**Опции:**
- `--detailed` - показать подробную информацию
- `--sort-by DATE/SIZE/NAME` - сортировка по дате/размеру/имени

**Примеры:**

```bash
# Показать все бэкапы
python sdb backup list

# Показать с подробной информацией
python sdb backup list --detailed

# Сортировать по дате
python sdb backup list --sort-by DATE
```

**Результат:**
```
📋 Доступные бэкапы:

🟢 db_sqlite_data_20240115_143022
   📅 Создан: 2024-01-15 14:30:22
   📊 Размер: 45.2MB
   📁 Тип: Полный бэкап (БД + данные)

🟢 before_update_2024_01_15
   📅 Создан: 2024-01-15 10:15:30
   📊 Размер: 42.1MB
   📁 Тип: Полный бэкап (БД + данные)

🟡 data_only_20240115_090000
   📅 Создан: 2024-01-15 09:00:00
   📊 Размер: 15.3MB
   📁 Тип: Только данные (без БД)
```

### `python sdb backup restore`

**⚠️ ОПАСНО!** Восстанавливает систему из бэкапа.

**Опции:**
- `backup_name` - имя бэкапа для восстановления
- `--dry-run` - показать что будет сделано без выполнения
- `--force` - принудительное восстановление

**Примеры:**

```bash
# Показать что будет восстановлено (безопасно)
python sdb backup restore backup_name --dry-run

# Восстановить из бэкапа
python sdb backup restore db_sqlite_data_20240115_143022

# Принудительное восстановление
python sdb backup restore backup_name --force
```

**Результат:**
```
⚠️ ВНИМАНИЕ: Восстановление перезапишет текущие данные!

📋 Что будет восстановлено:
   🗄️ База данных: users, roles, permissions
   📁 Файлы: config/, modules/, logs/
   📊 Размер: 45.2MB

❓ Вы уверены, что хотите восстановить из 'db_sqlite_data_20240115_143022'? [y/N]: y

✅ Восстановление завершено успешно!
📊 Восстановлено: 1250 записей в БД, 45 файлов
⏱️ Время восстановления: 1.8 секунды
```

## Расширенные команды (в разработке)

### `python sdb backup schedule`

Настраивает автоматическое расписание бэкапов.

**Опции:**
- `--cron EXPRESSION` - cron выражение для расписания
- `--daily` - ежедневные бэкапы
- `--weekly` - еженедельные бэкапы
- `--monthly` - ежемесячные бэкапы

**Примеры:**

```bash
# Ежедневные бэкапы в 2:00
python sdb backup schedule --cron "0 2 * * *"

# Еженедельные бэкапы по воскресеньям
python sdb backup schedule --cron "0 2 * * 0"

# Ежемесячные бэкапы в первое число месяца
python sdb backup schedule --cron "0 2 1 * *"
```

### `python sdb backup verify`

Проверяет целостность бэкапов.

**Опции:**
- `backup_name` - имя бэкапа для проверки
- `--all` - проверить все бэкапы

**Примеры:**

```bash
# Проверить конкретный бэкап
python sdb backup verify db_sqlite_data_20240115_143022

# Проверить все бэкапы
python sdb backup verify --all
```

### `python sdb backup cleanup`

Очищает старые бэкапы.

**Опции:**
- `--old` - удалить старые бэкапы
- `--keep N` - оставить последние N бэкапов
- `--before DATE` - удалить бэкапы до даты
- `--dry-run` - показать что будет удалено

**Примеры:**

```bash
# Показать что будет удалено
python sdb backup cleanup --keep 7 --dry-run

# Оставить только последние 7 бэкапов
python sdb backup cleanup --keep 7

# Удалить бэкапы старше 30 дней
python sdb backup cleanup --before "30 days ago"
```

### `python sdb backup encrypt`

Шифрует бэкапы для безопасности.

**Опции:**
- `--password` - установить пароль
- `--algorithm ALGORITHM` - алгоритм шифрования
- `--key-file FILE` - файл с ключом

**Примеры:**

```bash
# Зашифровать бэкап с паролем
python sdb backup encrypt --password

# Использовать определенный алгоритм
python sdb backup encrypt --algorithm AES256
```

### `python sdb backup sync`

Синхронизирует бэкапы с удаленным хранилищем.

**Опции:**
- `--remote URL` - URL удаленного хранилища
- `--cloud s3/gcs/azure` - облачное хранилище
- `--encrypt` - шифрование при передаче
- `--compress` - сжатие для экономии места

**Примеры:**

```bash
# Синхронизировать с AWS S3
python sdb backup sync --cloud s3 --encrypt

# Синхронизировать с Google Cloud Storage
python sdb backup sync --cloud gcs --compress
```

### `python sdb backup test-restore`

Тестирует восстановление из бэкапа.

**Опции:**
- `backup_name` - имя бэкапа для тестирования

**Примеры:**

```bash
# Протестировать восстановление
python sdb backup test-restore db_sqlite_data_20240115_143022
```

## Структура бэкапа

```
backup/
├── db_sqlite_data_20240115_143022/
│   ├── database/
│   │   └── swiftdevbot.db
│   ├── files/
│   │   ├── config/
│   │   ├── modules/
│   │   └── logs/
│   ├── metadata.json
│   └── checksum.md5
└── before_update_2024_01_15/
    ├── database/
    ├── files/
    ├── metadata.json
    └── checksum.md5
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb backup restore` - перезаписывает текущие данные
- `python sdb backup cleanup --all` - удаляет все бэкапы

### ⚠️ Опасные команды:
- `python sdb backup create --no-db` - без бэкапа БД
- `python sdb backup cleanup --old` - удаляет старые бэкапы
- `python sdb backup encrypt --password` - может сломать доступ

### ✅ Безопасные команды:
- `python sdb backup list` - только показывает
- `python sdb backup create` - создает копию
- `python sdb backup verify` - только проверяет

## Рекомендации

1. **Регулярные бэкапы**: Создавайте бэкапы перед важными изменениями
2. **Тестирование**: Всегда тестируйте восстановление из бэкапа
3. **Хранение**: Храните бэкапы в разных местах
4. **Шифрование**: Используйте шифрование для конфиденциальных данных
5. **Очистка**: Регулярно удаляйте старые бэкапы для экономии места

## Устранение проблем

### Проблема: "Недостаточно места"
```bash
# Проверить свободное место
df -h

# Очистить старые бэкапы
python sdb backup cleanup --keep 5
```

### Проблема: "Ошибка доступа"
```bash
# Проверить права доступа
ls -la backup/

# Исправить права
chmod 755 backup/
```

### Проблема: "Бэкап поврежден"
```bash
# Проверить целостность
python sdb backup verify backup_name

# Попробовать другой бэкап
python sdb backup list
``` 