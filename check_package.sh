#!/bin/bash
# Простая проверка готового пакета SwiftDevBot

PACKAGE_FILE="deploy_packages/SwiftDevBot_deploy_20250724_033714.zip"

echo "🔍 Проверка готового пакета SwiftDevBot..."
echo "================================================"

if [ ! -f "$PACKAGE_FILE" ]; then
    echo "❌ Пакет не найден: $PACKAGE_FILE"
    exit 1
fi

echo "✅ Пакет найден: $PACKAGE_FILE"

# Размер файла
SIZE=$(ls -lh "$PACKAGE_FILE" | awk '{print $5}')
echo "📊 Размер: $SIZE"

# Проверка ключевых файлов
echo ""
echo "📋 Проверка ключевых файлов:"
python3 -c "
import zipfile
with zipfile.ZipFile('$PACKAGE_FILE', 'r') as z:
    files = z.namelist()
    key_files = ['install.sh', 'install.bat', 'config.template.yaml', 'start.sh', 'start.bat', 'DEPLOY_README.md', 'run_bot.py', 'requirements.txt']
    all_ok = True
    for f in key_files:
        if f in files:
            print(f'  ✓ {f}')
        else:
            print(f'  ✗ {f} - ОТСУТСТВУЕТ!')
            all_ok = False
    print(f'\n📊 Всего файлов: {len(files)}')
    if all_ok:
        print('🎉 Все ключевые файлы на месте!')
    else:
        print('❌ Некоторые файлы отсутствуют!')
"

echo ""
echo "🎯 Пакет готов к передаче пользователю!"
echo "📍 Расположение: $(pwd)/$PACKAGE_FILE"
echo ""
echo "📋 Инструкция для пользователя:"
echo "1. Распаковать: unzip SwiftDevBot_deploy_20250724_033714.zip"
echo "2. Установить: ./install.sh (или install.bat для Windows)"
echo "3. Настроить: nano config.yaml"
echo "4. Запустить: ./start.sh (или start.bat для Windows)"
