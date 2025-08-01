# modules/example_module/permissions.py

MODULE_NAME = "example_module" # Важно, чтобы совпадало с именем модуля/папки

# Базовый доступ к пользовательскому интерфейсу модуля
PERM_ACCESS_USER_FEATURES = f"{MODULE_NAME}.access_user_features"

# Просмотр информации
PERM_VIEW_MODULE_SETTINGS = f"{MODULE_NAME}.view_module_settings" # Переименовал для ясности
PERM_VIEW_SECRET_INFO = f"{MODULE_NAME}.view_secret_info"

# Выполнение действий
PERM_PERFORM_BASIC_ACTION = f"{MODULE_NAME}.perform_basic_action" # Старое "do_magic"
PERM_PERFORM_ADVANCED_ACTION = f"{MODULE_NAME}.perform_advanced_action"

# Работа с заметками (CRUD)
PERM_MANAGE_OWN_NOTES = f"{MODULE_NAME}.manage_own_notes" # Общее право на свои заметки

# Административные права для модуля
PERM_ADMIN_VIEW_ALL_NOTES = f"{MODULE_NAME}.admin_view_all_notes"
PERM_ADMIN_MANAGE_MODULE = f"{MODULE_NAME}.admin_manage_module" # Общее админское право для модуля