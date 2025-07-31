# modules/notes_manager/permissions.py

# Имя модуля должно совпадать с именем из манифеста и папки
MODULE_NAME = "notes_manager"

# Все разрешения модуля (строго в формате "имя_модуля.название_разрешения")
PERM_ACCESS_USER_FEATURES = f"{MODULE_NAME}.access_user_features"
PERM_VIEW_NOTES = f"{MODULE_NAME}.view_notes"
PERM_CREATE_NOTES = f"{MODULE_NAME}.create_notes"
PERM_EDIT_NOTES = f"{MODULE_NAME}.edit_notes"
PERM_DELETE_NOTES = f"{MODULE_NAME}.delete_notes"
PERM_MANAGE_CATEGORIES = f"{MODULE_NAME}.manage_categories"
PERM_ADMIN_VIEW_ALL = f"{MODULE_NAME}.admin_view_all"
PERM_ADMIN_MANAGE = f"{MODULE_NAME}.admin_manage"