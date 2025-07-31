#!/bin/bash
# Простая обертка для упаковки бота

cd "$(dirname "$0")"

echo "🚀 SwiftDevBot Packager"
echo "======================="
echo ""

# Переходим в корень проекта
cd ..

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден!"
    exit 1
fi

echo "📦 Запуск упаковщика..."
python3 scripts/package_bot.py "$@"
