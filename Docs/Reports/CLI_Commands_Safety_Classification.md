# 🛡️ Классификация CLI команд SwiftDevBot-Lite по уровню опасности

## ❌ **КРИТИЧЕСКИ ОПАСНО**

### **База данных (cli/db.py):**
```bash
python sdb db downgrade base          # УДАЛИТ ВСЕ ДАННЫЕ!
python sdb db init-core --force       # ПЕРЕЗАПИШЕТ таблицы!
python sdb db stamp --purge           # УДАЛИТ историю миграций!
```

### **Бэкапы (cli/backup.py):**
```bash
python sdb backup restore backup_name # ПЕРЕЗАПИШЕТ текущие данные!
python sdb backup-smart sync --force  # Может удалить файлы!
python sdb backup cleanup --all       # УДАЛИТ ВСЕ старые бэкапы!
```

### **Безопасность (cli/security.py):**
```bash
python sdb security keys --rotate --force  # Сломает все API!
python sdb security permissions --reset     # Сбросит ВСЕ права!
python sdb security firewall --block-all    # Заблокирует доступ!
```

### **Система (cli/system.py):**
```bash
python sdb system service stop --all       # ОСТАНОВИТ всё!
python sdb system env unset --all          # Удалит ВСЕ переменные!
python sdb system logs --clear             # Удалит логи!
```

### **Кэш (cli/cache.py):**
```bash
python sdb cache clear --all               # Удалит ВСЕ кэши!
```

### **Задачи (cli/tasks.py):**
```bash
python sdb tasks cancel --all              # Остановит ВСЕ задачи!
```

### **Пользователи (cli/user.py):**
```bash
python sdb user bulk --delete              # Удалит ВСЕХ пользователей!
python sdb user groups --delete --all      # Удалит ВСЕ группы!
```

### **Модули (cli/module.py):**
```bash
python sdb module uninstall --all          # Удалит ВСЕ модули!
python sdb module disable --all            # Отключит ВСЕ модули!
```

### **Плагины (cli/plugin.py):**
```bash
python sdb plugin uninstall --all          # Удалит ВСЕ плагины!
python sdb plugin disable --all            # Отключит ВСЕ плагины!
```

### **Зависимости (cli/deps.py):**
```bash
python sdb deps remove --all               # Удалит ВСЕ зависимости!
```

### **Конфигурация (cli/config.py):**
```bash
python sdb config reset --all              # Сбросит ВСЕ настройки!
python sdb config migrate --force          # Принудительная миграция!
```

---

## ⚠️ **ОПАСНО**

### **База данных (cli/db.py):**
```bash
python sdb db vacuum --aggressive          # Может заблокировать БД
python sdb db optimize --rebuild           # Долгая операция, может упасть
python sdb db downgrade 1                  # Откат на одну версию (риск потери данных)
python sdb db analyze --full               # Может замедлить систему
```

### **Бэкапы (cli/backup.py):**
```bash
python sdb backup create --no-db           # Без бэкапа БД - риск потери данных
python sdb backup cleanup --old            # Удалит старые бэкапы
python sdb backup encrypt --password       # Может сломать доступ к бэкапам
python sdb backup sync --remote            # Может перезаписать удаленные данные
```

### **Безопасность (cli/security.py):**
```bash
python sdb security audit --fix            # Может изменить права!
python sdb security keys --generate        # Создаст новые ключи
python sdb security ssl --renew            # Обновит сертификаты
python sdb security firewall --rules       # Изменит правила файрвола
```

### **Система (cli/system.py):**
```bash
python sdb system service restart --all    # Перезапустит все сервисы
python sdb system env set KEY=VALUE        # Изменит переменные окружения
python sdb system logs --rotate            # Перезапишет логи
```

### **Мониторинг (cli/monitor.py):**
```bash
python sdb monitor alerts --configure      # Изменит настройки алертов
python sdb monitor logs --clear            # Очистит логи мониторинга
```

### **Кэш (cli/cache.py):**
```bash
python sdb cache clear --old               # Удалит старые кэши
python sdb cache warm                      # Может нагрузить систему
```

### **Задачи (cli/tasks.py):**
```bash
python sdb tasks retry TASK_ID             # Повторит задачу (может создать дубли)
python sdb tasks schedule --cron           # Создаст новые задачи
```

### **Уведомления (cli/notifications.py):**
```bash
python sdb notifications configure --email # Изменит настройки уведомлений
python sdb notifications send --channel    # Отправит тестовое сообщение
```

### **Пользователи (cli/user.py):**
```bash
python sdb user bulk --import              # Импортирует пользователей
python sdb user permissions --assign       # Изменит права пользователей
python sdb user quota --set                # Установит лимиты
```

### **Модули (cli/module.py):**
```bash
python sdb module install --from-git       # Установит новый модуль
python sdb module update --all             # Обновит все модули
python sdb module enable/disable NAME      # Включит/отключит модуль
```

### **Локализация (cli/locale.py):**
```bash
python sdb locale compile                  # Перекомпилирует переводы
python sdb locale translate --auto         # Автоматически переведет
```

### **Плагины (cli/plugin.py):**
```bash
python sdb plugin install URL              # Установит новый плагин
python sdb plugin update --all             # Обновит все плагины
python sdb plugin enable/disable NAME      # Включит/отключит плагин
```

### **API (cli/api.py):**
```bash
python sdb api keys --generate             # Создаст новые API ключи
python sdb api keys --revoke               # Отзовет API ключи
python sdb api rate-limit --set            # Изменит лимиты запросов
```

### **Зависимости (cli/deps.py):**
```bash
python sdb deps update --all               # Обновит все зависимости
python sdb deps audit --security           # Проверит уязвимости
```

### **Конфигурация (cli/config.py):**
```bash
python sdb config migrate --version        # Мигрирует конфигурацию
python sdb config backup --auto            # Создаст бэкап конфигурации
```

### **Разработка (cli/dev.py):**
```bash
python sdb dev lint --fix                  # Исправит код автоматически
python sdb dev debug --enable              # Включит режим отладки
python sdb dev profile --memory            # Профилирует память
```

---

## ✅ **БЕЗОПАСНО**

### **База данных (cli/db.py):**
```bash
python sdb db status                       # Только показывает статус
python sdb db size --human-readable        # Только читает размеры
python sdb db tables --list                # Только показывает таблицы
python sdb db upgrade                      # Добавляет, не удаляет
python sdb db current                      # Показывает текущую версию
python sdb db history                      # Показывает историю миграций
python sdb db health-check                 # Проверяет здоровье БД
```

### **Бэкапы (cli/backup.py):**
```bash
python sdb backup list                     # Только показывает список
python sdb backup create                   # Создает копию
python sdb backup verify                   # Проверяет целостность
python sdb backup-smart scan               # Только анализирует
python sdb backup test-restore             # Тестирует восстановление
```

### **Безопасность (cli/security.py):**
```bash
python sdb security audit                  # Только проверяет
python sdb security keys --list            # Только показывает ключи
python sdb security permissions --check    # Только проверяет права
python sdb security firewall --status      # Только показывает статус
python sdb security ssl --certificate      # Только показывает сертификат
python sdb security scan --vulnerabilities # Только сканирует
```

### **Система (cli/system.py):**
```bash
python sdb system status                   # Только показывает статус
python sdb system logs --tail              # Только читает логи
python sdb system health-check             # Только проверяет здоровье
python sdb system env list                 # Только показывает переменные
```

### **Мониторинг (cli/monitor.py):**
```bash
python sdb monitor status                  # Только показывает статус
python sdb monitor metrics --cpu --memory  # Только собирает метрики
python sdb monitor alerts --list           # Только показывает алерты
python sdb monitor logs --analyze          # Только анализирует логи
python sdb monitor performance --slow-queries # Только анализирует производительность
python sdb monitor dashboard               # Только показывает дашборд
python sdb monitor report --daily          # Только генерирует отчет
```

### **Кэш (cli/cache.py):**
```bash
python sdb cache status                    # Только показывает статус
python sdb cache stats                     # Только показывает статистику
```

### **Задачи (cli/tasks.py):**
```bash
python sdb tasks list --running            # Только показывает задачи
python sdb tasks logs TASK_ID              # Только показывает логи
```

### **Уведомления (cli/notifications.py):**
```bash
python sdb notifications list              # Только показывает уведомления
python sdb notifications test              # Только тестирует
```

### **Пользователи (cli/user.py):**
```bash
python sdb user list                       # Только показывает пользователей
python sdb user show USERNAME              # Только показывает пользователя
python sdb user activity --logs            # Только показывает активность
python sdb user quota --check              # Только проверяет квоты
```

### **Модули (cli/module.py):**
```bash
python sdb module list                     # Только показывает модули
python sdb module info NAME                # Только показывает информацию
python sdb module validate                 # Только проверяет
python sdb module dependencies --check     # Только проверяет зависимости
python sdb module permissions --list       # Только показывает права
```

### **Локализация (cli/locale.py):**
```bash
python sdb locale list                     # Только показывает языки
python sdb locale extract --update         # Только извлекает строки
python sdb locale export --format          # Только экспортирует
```

### **Плагины (cli/plugin.py):**
```bash
python sdb plugin list --enabled           # Только показывает плагины
python sdb plugin info NAME                # Только показывает информацию
python sdb plugin validate                 # Только проверяет
```

### **API (cli/api.py):**
```bash
python sdb api status                      # Только показывает статус
python sdb api rate-limit --get            # Только показывает лимиты
python sdb api docs --generate             # Только генерирует документацию
python sdb api test --endpoint             # Только тестирует endpoints
```

### **Зависимости (cli/deps.py):**
```bash
python sdb deps check --outdated           # Только проверяет устаревшие
python sdb deps audit --security           # Только проверяет безопасность
python sdb deps lock --generate            # Только генерирует lock файл
```

### **Конфигурация (cli/config.py):**
```bash
python sdb config validate                 # Только проверяет
python sdb config diff --staged            # Только показывает различия
python sdb config template --generate      # Только генерирует шаблон
```

### **Разработка (cli/dev.py):**
```bash
python sdb dev test --coverage             # Только запускает тесты
python sdb dev docs --build                # Только строит документацию
python sdb dev profile --cpu               # Только профилирует
```

---

## 🎯 **ПРАВИЛА БЕЗОПАСНОСТИ**

### **Перед выполнением ЛЮБОЙ команды:**

1. **✅ Сделайте бэкап** (если команда может изменить данные)
2. **✅ Прочитайте справку** (`--help`)
3. **✅ Проверьте, что вы в правильной директории**
4. **✅ Убедитесь, что у вас есть права**
5. **✅ Используйте `--dry-run` для тестирования**
6. **✅ Подтвердите действие** (если система спрашивает)

### **Особенно осторожно с командами:**
- Содержащими `--all`, `--force`, `--purge`
- Содержащими `delete`, `remove`, `clear`
- Содержащими `reset`, `uninstall`, `disable`
- Содержащими `downgrade`, `restore`, `sync`

### **Всегда безопасно:**
- Команды со словами `list`, `show`, `status`, `info`
- Команды со словами `check`, `validate`, `test`
- Команды со словами `analyze`, `report`, `metrics`

---

## 🚨 **ЭКСТРЕННЫЕ СИТУАЦИИ**

### **Если что-то пошло не так:**

1. **🛑 НЕ ПАНИКУЙТЕ** - паника усугубляет ситуацию
2. **📋 ЗАПИШИТЕ** что именно вы делали
3. **🔄 ВОССТАНОВИТЕ** из последнего бэкапа
4. **📞 ОБРАТИТЕСЬ** за помощью с подробным описанием

### **Команды для диагностики проблем:**
```bash
python sdb system health-check             # Проверить общее состояние
python sdb db status                       # Проверить состояние БД
python sdb backup list                     # Проверить доступные бэкапы
python sdb monitor status                  # Проверить мониторинг
```

---

## 📊 **СТАТИСТИКА ОПАСНОСТИ**

### **По модулям:**
- **База данных**: 3 критически опасных, 4 опасных, 7 безопасных
- **Бэкапы**: 3 критически опасных, 4 опасных, 5 безопасных
- **Безопасность**: 3 критически опасных, 4 опасных, 6 безопасных
- **Система**: 3 критически опасных, 3 опасных, 4 безопасных
- **Мониторинг**: 0 критически опасных, 2 опасных, 7 безопасных
- **Кэш**: 1 критически опасный, 2 опасных, 2 безопасных
- **Задачи**: 1 критически опасный, 2 опасных, 2 безопасных
- **Пользователи**: 2 критически опасных, 3 опасных, 4 безопасных
- **Модули**: 2 критически опасных, 3 опасных, 5 безопасных
- **Локализация**: 0 критически опасных, 2 опасных, 3 безопасных
- **Плагины**: 2 критически опасных, 3 опасных, 3 безопасных
- **API**: 0 критически опасных, 3 опасных, 4 безопасных
- **Зависимости**: 1 критически опасный, 2 опасных, 3 безопасных
- **Конфигурация**: 2 критически опасных, 2 опасных, 4 безопасных
- **Разработка**: 0 критически опасных, 3 опасных, 3 безопасных

### **Общая статистика:**
- **❌ Критически опасно**: 22 команды
- **⚠️ Опасно**: 45 команд
- **✅ Безопасно**: 67 команд

**Всего команд**: 134

---

## 🎯 **ЗАКЛЮЧЕНИЕ**

**Помните: Лучше сделать лишний бэкап, чем потерять данные!**

**Помните: Лучше потратить 5 минут на проверку, чем 5 часов на восстановление!**

**Помните: Лучше спросить дважды, чем пожалеть один раз!**

**Безопасность превыше всего!** 🛡️ 