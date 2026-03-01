
#!/bin/bash
echo "⚙️ Скрипт активирован $(date)" >> /root/sellerapp/cron_test.log
source /root/sellerapp/venv/bin/activate
set -a; source /root/sellerapp/.env; set +a

SERVICE="sellerapp"
LOG="/root/sellerapp/monitor.log"

# Проверяем статус
if systemctl is-active --quiet $SERVICE; then
  echo "$(date '+%F %T') ✅ $SERVICE работает" >> "$LOG"
else
  echo "$(date '+%F %T') ❌ $SERVICE упал — перезапускаю" >> "$LOG"
  systemctl restart $SERVICE
  sleep 5
  if systemctl is-active --quiet $SERVICE; then
    MSG="♻️ $SERVICE был перезапущен — теперь всё ок ✅"
  else
    MSG="🚨 Ошибка: $SERVICE не удалось запустить ❌"
  fi
  echo "[$(date)] Отправляю в Telegram: ${MSG}" >> "$LOG"
  curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
       -d chat_id=${CHAT_ID} \
       -d text="${MSG}"
fi
