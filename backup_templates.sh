#!/bin/bash
# === Автоматический бэкап шаблонов SellerApp ===

BACKUP_DIR="/root/sellerapp/templates_ready"
ARCHIVE_DIR="/root/sellerapp"
DATE=$(date +%Y%m%d_%H%M%S)
ARCHIVE_FILE="$ARCHIVE_DIR/templates_ready_$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

# Копируем основные страницы
cp /root/sellerapp/templates/{index.html,forecast.html,sales_forecast.html,stocks.html,analytics.html,settings.html,assistant.html,base.html,footer.html} "$BACKUP_DIR" 2>/dev/null

# Создаём архив
tar -czf "$ARCHIVE_FILE" -C "$BACKUP_DIR" .

# Удаляем старые архивы старше 7 дней
find "$ARCHIVE_DIR" -name "templates_ready_*.tar.gz" -type f -mtime +7 -delete

# Сообщение в лог
echo "$(date '+%F %T') ✅ Резервное копирование шаблонов выполнено: $ARCHIVE_FILE" >> /root/sellerapp/backup.log
