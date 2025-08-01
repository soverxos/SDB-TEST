# 👥 Управление пользователями (user)

## Обзор

Модуль `user` предоставляет инструменты для управления пользователями SwiftDevBot, включая создание, редактирование, удаление, настройку прав доступа и мониторинг активности пользователей.

## Основные команды

### `python sdb user list`

Показывает список всех пользователей.

**Опции:**
- `--role admin/user/moderator` - фильтр по роли
- `--status active/inactive/all` - статус пользователей
- `--detailed` - подробная информация
- `--json` - вывод в формате JSON

**Примеры:**

```bash
# Показать всех пользователей
python sdb user list

# Показать только администраторов
python sdb user list --role admin

# Подробная информация
python sdb user list --detailed
```

**Результат:**
```
👥 Пользователи SwiftDevBot-Lite

📱 Telegram пользователи:
   🟢 @admin_user (ID: 123456789)
      📊 Роль: Администратор
      📊 Статус: Активен
      📊 Регистрация: 2024-01-01
      📊 Последняя активность: 2024-01-15 14:30:22

   🟢 @moderator_user (ID: 987654321)
      📊 Роль: Модератор
      📊 Статус: Активен
      📊 Регистрация: 2024-01-05
      📊 Последняя активность: 2024-01-15 13:45:10

   🟢 @regular_user (ID: 555666777)
      📊 Роль: Пользователь
      📊 Статус: Активен
      📊 Регистрация: 2024-01-10
      📊 Последняя активность: 2024-01-15 12:20:15



📊 Общая статистика:
   🟢 Активных пользователей: 3
   🔴 Неактивных пользователей: 0
   📊 Всего пользователей: 3
   📊 Администраторов: 1
   📊 Модераторов: 1
   📊 Обычных пользователей: 1
```

### `python sdb user create`

Создает нового пользователя.

**Опции:**
- `USERNAME` - имя пользователя
- `--role admin/user/moderator` - роль пользователя
- `--email EMAIL` - email пользователя

**Примеры:**

```bash
# Создать пользователя Telegram
python sdb user create @new_user

# Создать администратора
python sdb user create @admin_user --role admin

# Создать пользователя с email
python sdb user create @user_name --email user@example.com
```

**Результат:**
```
✅ Создание пользователя '@new_user'...

📋 Информация о пользователе:
   📊 Имя: @new_user
   📊 Платформа: Telegram
   📊 Роль: Пользователь
   📊 ID: 123456789
   📊 Статус: Активен

📥 Процесс создания:
   ✅ Пользователь создан
   ✅ Роль назначена
   ✅ Права доступа настроены
   ✅ Уведомление отправлено

📊 Результат создания:
   ✅ Пользователь создан успешно
   📊 ID пользователя: 123456789
   📊 Роль: Пользователь
   📊 Статус: Активен
   ⚠️ Требуется подтверждение email
```

### `python sdb user edit`

Редактирует пользователя.

**Опции:**
- `USERNAME` - имя пользователя для редактирования
- `--role admin/user/moderator` - изменить роль
- `--status active/inactive` - изменить статус
- `--email EMAIL` - изменить email
- `--password PASSWORD` - изменить пароль

**Примеры:**

```bash
# Изменить роль пользователя
python sdb user edit @user_name --role moderator

# Изменить статус
python sdb user edit @user_name --status inactive

# Изменить email
python sdb user edit @user_name --email new@example.com

# Изменить пароль
python sdb user edit @user_name --password newpassword123
```

**Результат:**
```
✏️ Редактирование пользователя '@user_name'...

📋 Текущая информация:
   📊 Имя: @user_name
   📊 Роль: Пользователь
   📊 Статус: Активен
   📊 Email: old@example.com

📥 Изменения:
   ✅ Роль: Пользователь → Модератор
   ✅ Email: old@example.com → new@example.com
   ✅ Статус: Активен (без изменений)

📊 Результат редактирования:
   ✅ Пользователь обновлен успешно
   📊 Роль изменена на: Модератор
   📊 Email обновлен
   ⚠️ Уведомление отправлено пользователю
```

### `python sdb user delete`

Удаляет пользователя.

**Опции:**
- `USERNAME` - имя пользователя для удаления
- `--force` - принудительное удаление
- `--keep-data` - сохранить данные пользователя
- `--backup` - создать бэкап перед удалением

**Примеры:**

```bash
# Удалить пользователя
python sdb user delete @user_name

# Принудительное удаление
python sdb user delete @user_name --force

# Удалить с сохранением данных
python sdb user delete @user_name --keep-data

# Удалить с бэкапом
python sdb user delete @user_name --backup
```

**Результат:**
```
🗑️ Удаление пользователя '@user_name'...

📋 Информация о пользователе:
   📊 Имя: @user_name
   📊 Роль: Пользователь
   📊 Статус: Активен
   📊 Регистрация: 2024-01-10

⚠️ ВНИМАНИЕ: Это действие нельзя отменить!
❓ Вы уверены, что хотите удалить пользователя '@user_name'? [y/N]: y

📥 Процесс удаления:
   ✅ Пользователь деактивирован
   ✅ Данные удалены
   ✅ Права доступа отозваны
   ✅ Бэкап создан

📊 Результат удаления:
   ✅ Пользователь удален успешно
   📊 Удалено записей: 15
   📊 Освобождено места: 2.3MB
   📁 Бэкап сохранен: user_backup_20240115_143022.json
```

### `python sdb user info`

Показывает информацию о пользователе.

**Опции:**
- `USERNAME` - имя пользователя
- `--detailed` - подробная информация
- `--json` - вывод в формате JSON
- `--history` - показать историю активности

**Примеры:**

```bash
# Информация о пользователе
python sdb user info @user_name

# Подробная информация
python sdb user info @user_name --detailed

# Информация в JSON
python sdb user info @user_name --json

# История активности
python sdb user info @user_name --history
```

**Результат:**
```
👤 Информация о пользователе '@user_name'

📋 Основная информация:
   📊 Имя: @user_name
   📊 ID: 123456789
   📊 Платформа: Telegram
   📊 Роль: Модератор
   📊 Статус: Активен
   📊 Email: user@example.com

📋 Регистрация:
   📊 Дата: 2024-01-10 10:30:15
   📊 IP адрес: 192.168.1.100
   📊 Устройство: Telegram Web

📋 Активность:
   📊 Последний вход: 2024-01-15 14:30:22
   📊 Всего сессий: 45
   📊 Время онлайн: 12 часов 30 минут
   📊 Команд выполнено: 234

📋 Права доступа:
   ✅ Чтение сообщений
   ✅ Отправка сообщений
   ✅ Использование команд
   ✅ Модерация чата
   ❌ Административные функции

📋 Статистика:
   📊 Сообщений отправлено: 1,234
   📊 Команд использовано: 567
   📊 Файлов загружено: 23
   📊 Предупреждений: 0
```

### `python sdb user ban`

Блокирует пользователя.

**Опции:**
- `USERNAME` - имя пользователя для блокировки
- `--reason REASON` - причина блокировки
- `--duration DAYS` - длительность блокировки
- `--permanent` - постоянная блокировка

**Примеры:**

```bash
# Заблокировать пользователя
python sdb user ban @user_name

# Блокировка с причиной
python sdb user ban @user_name --reason "Нарушение правил"

# Временная блокировка
python sdb user ban @user_name --duration 7

# Постоянная блокировка
python sdb user ban @user_name --permanent
```

**Результат:**
```
🚫 Блокировка пользователя '@user_name'...

📋 Информация о пользователе:
   📊 Имя: @user_name
   📊 Роль: Пользователь
   📊 Статус: Активен

📥 Процесс блокировки:
   ✅ Пользователь заблокирован
   ✅ Причина: Нарушение правил
   ✅ Длительность: 7 дней
   ✅ Уведомление отправлено

📊 Результат блокировки:
   ✅ Пользователь заблокирован успешно
   📊 Статус: Заблокирован
   📊 Дата разблокировки: 2024-01-22 14:30:22
   ⚠️ Уведомление отправлено пользователю
```

### `python sdb user unban`

Разблокирует пользователя.

**Опции:**
- `USERNAME` - имя пользователя для разблокировки
- `--reason REASON` - причина разблокировки
- `--force` - принудительная разблокировка

**Примеры:**

```bash
# Разблокировать пользователя
python sdb user unban @user_name

# Разблокировка с причиной
python sdb user unban @user_name --reason "Апелляция одобрена"

# Принудительная разблокировка
python sdb user unban @user_name --force
```

**Результат:**
```
✅ Разблокировка пользователя '@user_name'...

📋 Информация о пользователе:
   📊 Имя: @user_name
   📊 Статус: Заблокирован
   📊 Дата блокировки: 2024-01-08

📥 Процесс разблокировки:
   ✅ Пользователь разблокирован
   ✅ Причина: Апелляция одобрена
   ✅ Права восстановлены
   ✅ Уведомление отправлено

📊 Результат разблокировки:
   ✅ Пользователь разблокирован успешно
   📊 Статус: Активен
   📊 Права восстановлены
   ⚠️ Уведомление отправлено пользователю
```

## Расширенные команды (в разработке)

### `python sdb user search`

Ищет пользователей.

**Опции:**
- `QUERY` - поисковый запрос
- `--platform telegram` - платформа
- `--role admin/user/moderator` - роль
- `--status active/inactive/banned` - статус

**Примеры:**

```bash
# Поиск пользователей
python sdb user search "admin"

# Поиск по платформе
python sdb user search --platform telegram "user"

# Поиск по роли
python sdb user search --role admin

# Поиск заблокированных
python sdb user search --status banned
```

### `python sdb user export`

Экспортирует данные пользователей.

**Опции:**
- `--format json/csv/xml` - формат экспорта
- `--file FILE` - файл для сохранения
- `--include-sensitive` - включить чувствительные данные
- `--filter ROLE` - фильтр по роли

**Примеры:**

```bash
# Экспорт всех пользователей
python sdb user export

# Экспорт в CSV
python sdb user export --format csv --file users.csv

# Экспорт с чувствительными данными
python sdb user export --include-sensitive

# Экспорт только администраторов
python sdb user export --filter admin
```

### `python sdb user import`

Импортирует пользователей из файла.

**Опции:**
- `FILE` - файл для импорта
- `--format json/csv/xml` - формат файла
- `--update` - обновить существующих пользователей
- `--validate` - проверить данные перед импортом

**Примеры:**

```bash
# Импорт пользователей
python sdb user import users.json

# Импорт из CSV
python sdb user import users.csv --format csv

# Обновление существующих
python sdb user import users.json --update

# Импорт с проверкой
python sdb user import users.json --validate
```

### `python sdb user activity`

Показывает активность пользователей.

**Опции:**
- `--user USERNAME` - конкретный пользователь
- `--period DAYS` - период активности
- `--detailed` - подробная информация
- `--export FILE` - экспорт результатов

**Примеры:**

```bash
# Активность всех пользователей
python sdb user activity

# Активность конкретного пользователя
python sdb user activity --user @user_name

# Активность за последние 30 дней
python sdb user activity --period 30

# Подробная активность
python sdb user activity --detailed
```

### `python sdb user permissions`

Управляет правами доступа пользователей.

**Опции:**
- `USERNAME` - имя пользователя
- `--grant PERMISSION` - предоставить право
- `--revoke PERMISSION` - отозвать право
- `--list` - показать права

**Примеры:**

```bash
# Показать права пользователя
python sdb user permissions @user_name --list

# Предоставить право
python sdb user permissions @user_name --grant "moderate_chat"

# Отозвать право
python sdb user permissions @user_name --revoke "send_messages"
```

### `python sdb user backup`

Создает бэкап данных пользователей.

**Опции:**
- `--include-sensitive` - включить чувствительные данные
- `--compress` - сжать бэкап
- `--encrypt` - зашифровать бэкап
- `--path PATH` - путь для сохранения

**Примеры:**

```bash
# Создать бэкап
python sdb user backup

# Бэкап с чувствительными данными
python sdb user backup --include-sensitive

# Сжатый бэкап
python sdb user backup --compress

# Зашифрованный бэкап
python sdb user backup --encrypt
```

## Безопасность

### ❌ Критически опасные команды:
- `python sdb user delete --force` - принудительное удаление
- `python sdb user ban --permanent` - постоянная блокировка
- `python sdb user export --include-sensitive` - экспорт чувствительных данных

### ⚠️ Опасные команды:
- `python sdb user edit --role admin` - изменение роли
- `python sdb user delete` - удаление пользователя
- `python sdb user ban` - блокировка пользователя

### ✅ Безопасные команды:
- `python sdb user list` - только показывает список
- `python sdb user info` - только показывает информацию
- `python sdb user search` - только ищет пользователей
- `python sdb user activity` - только показывает активность

## Устранение проблем

### Проблема: "Пользователь не найден"
```bash
# Поиск пользователя
python sdb user search username

# Проверить в Telegram
python sdb user list --platform telegram

# Проверить статус
python sdb user info username
```

### Проблема: "Пользователь заблокирован"
```bash
# Проверить статус
python sdb user info username

# Разблокировать пользователя
python sdb user unban username

# Проверить права
python sdb user permissions username --list
```

### Проблема: "Недостаточно прав"
```bash
# Проверить права
python sdb user permissions username --list

# Предоставить права
python sdb user permissions username --grant "required_permission"

# Изменить роль
python sdb user edit username --role moderator
```

## Рекомендации

1. **Безопасность**: Регулярно проверяйте права доступа
2. **Мониторинг**: Следите за активностью пользователей
3. **Бэкапы**: Создавайте бэкапы данных пользователей
4. **Модерация**: Быстро реагируйте на нарушения
5. **Документация**: Ведите журнал действий администраторов 