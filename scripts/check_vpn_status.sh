#!/bin/bash
# Скрипт проверки статуса VPN подключения SwiftDevBot

echo "🔍 Проверка VPN подключения SwiftDevBot..."
echo "================================================="

# Проверяем статус systemd сервиса
echo "📋 Статус сервиса:"
sudo systemctl is-active --quiet swiftdevbot-vpn.service
if [ $? -eq 0 ]; then
    echo "✅ VPN сервис активен"
else
    echo "❌ VPN сервис неактивен"
    echo "Детали:"
    sudo systemctl status swiftdevbot-vpn.service --lines=5 --no-pager
fi

# Проверяем VPN интерфейс
echo ""
echo "🌐 VPN интерфейс:"
if ip addr show tun1 >/dev/null 2>&1; then
    VPN_IP=$(ip addr show tun1 | grep -o 'inet [0-9.]*' | cut -d' ' -f2)
    echo "✅ VPN интерфейс активен (IP: $VPN_IP)"
else
    echo "❌ VPN интерфейс не найден"
fi

# Проверяем внешний IP
echo ""
echo "🌍 Внешний IP-адрес:"
EXTERNAL_IP=$(curl -s --connect-timeout 5 https://icanhazip.com 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$EXTERNAL_IP" ]; then
    echo "✅ Внешний IP: $EXTERNAL_IP"
    if [ "$EXTERNAL_IP" = "31.202.91.112" ]; then
        echo "🎉 Подключение через ASUS роутер подтверждено!"
    else
        echo "⚠️  IP не соответствует ожидаемому (31.202.91.112)"
    fi
else
    echo "❌ Не удалось получить внешний IP"
fi

# Проверяем доступность роутера
echo ""
echo "📡 Проверка связи с роутером:"
if ping -c 1 -W 3 192.168.31.1 >/dev/null 2>&1; then
    echo "✅ Роутер доступен (192.168.31.1)"
else
    echo "❌ Роутер недоступен"
fi

echo ""
echo "================================================="
echo "Проверка завершена $(date)"
