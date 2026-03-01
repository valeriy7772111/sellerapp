
# ===== Импорты =====
import json
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== Конфигурация =====
BOT_TOKEN = "8468617922:AAHxX_OuUpUTtaHBHFvBQBVYJTMfj306BMo"
USERS_FILE = "/root/sellerapp/users.json"

# ===== Логирование =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ===== Загрузка пользователей =====
def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# ===== Сохранение пользователей =====
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ===== Сохранение и продление PRO-статуса =====
def activate_pro(user_id, username):
    users = load_users()
    now = datetime.now()
    old_data = users.get(str(user_id), {})

    # Если PRO ещё активен — прибавляем 30 дней к текущей дате окончания
    if old_data.get("pro") and old_data.get("expires"):
        try:
            expires_date = datetime.strptime(old_data["expires"], "%Y-%m-%d %H:%M")
            if expires_date > now:
                expires_date += timedelta(days=30)
            else:
                expires_date = now + timedelta(days=30)
        except Exception:
            expires_date = now + timedelta(days=30)
    else:
        expires_date = now + timedelta(days=30)

    users[str(user_id)] = {
        "username": username,
        "email": old_data.get("email", ""),
        "pro": True,
        "expires": expires_date.strftime("%Y-%m-%d %H:%M"),
        "registered": old_data.get("registered", now.strftime("%Y-%m-%d %H:%M"))
    }

    save_users(users)
    logging.info(f"✅ PRO активирован для {username} до {expires_date}")

# ===== Проверка истёкших PRO =====
def check_expired_pro():
    users = load_users()
    now = datetime.now()
    changed = False

    for uid, data in list(users.items()):
        if data.get("pro") and data.get("expires"):
            try:
                exp_date = datetime.strptime(data["expires"], "%Y-%m-%d %H:%M")
                if exp_date < now:
                    users[uid]["pro"] = False
                    changed = True
                    logging.info(f"⏳ PRO-доступ истёк для {data.get('username')}")
            except Exception:
                continue

    if changed:
        save_users(users)
        logging.info("✅ Обновлены пользователи с истёкшим PRO-доступом")

# ===== Планировщик проверки =====
scheduler = BackgroundScheduler()
scheduler.add_job(check_expired_pro, "interval", hours=24)
scheduler.start()

# ===== Регистрация нового пользователя =====
async def register_user(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username or "_"
    users = load_users()

    if str(user_id) not in users:
        users[str(user_id)] = {
            "username": username,
            "email": "",
            "pro": False,
            "expires": "",
            "registered": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_users(users)
        await update.message.reply_text("✅ Регистрация выполнена. Добро пожаловать в SellerApp Pro!")
    else:
        await update.message.reply_text("Вы уже зарегистрированы ✅")

# ===== Основные обработчики команд =====
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", register_user))
application.run_polling()
