import os, io, logging, qrcode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ====== Параметры из окружения (.sellerpay.env) ======
BOT_TOKEN   = os.getenv("BOT_TOKEN", "")
ADMIN_ID    = int(os.getenv("ADMIN_ID", "0"))
CARD_NUMBER = os.getenv("CARD_NUMBER", "0000000000000000")
PRO_PRICE   = int(os.getenv("PRO_PRICE", "299"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN пуст. Заполни /root/sellerapp/.sellerpay.env")

# ====== Логирование ======
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ====== Контентные тексты ======
APP_NAME = "SellerApp Team"   # подпись в сообщениях
WELCOME_TEXT = (
    "👋 Привет!\n\n"
    f"Я {APP_NAME}. Здесь можно оплатить PRO-доступ SellerApp Pro.\n"
    "Нажмите кнопку ниже, чтобы получить QR для перевода по СБП."
)

def make_qr_png(text: str) -> bytes:
    img = qrcode.make(text)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("💳 Оплатить по СБП", callback_data="pay")]]
    await (update.message or update.effective_message).reply_text(
        WELCOME_TEXT, reply_markup=InlineKeyboardMarkup(kb)
    )

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pay":
        # Простой QR: текст с реквизитами и суммой. При желании позже заменим на официальный SBP-QR.
        qr_text = f"Перевод по СБП на карту {CARD_NUMBER}. Сумма: {PRO_PRICE} руб."
        png = make_qr_png(qr_text)

        kb = [[InlineKeyboardButton("✅ Я оплатил", callback_data="paid")]]
        await query.message.reply_photo(
            png,
            caption=(
                f"💳 Отправьте перевод по СБП на карту:\n\n"
                f"`{CARD_NUMBER}`\n\n"
                f"Сумма: *{PRO_PRICE} ₽*\n\n"
                f"После перевода нажмите кнопку ниже."
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data == "paid":
        user = query.from_user
        ulink = f"@{user.username}" if user.username else f"id={user.id}"
        # Уведомляем админа
        if ADMIN_ID:
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"💰 {APP_NAME}: пользователь {user.first_name} ({ulink}) нажал «Я оплатил». Проверь перевод и активируй PRO."
                )
            except Exception as e:
                logging.error("Ошибка отправки админу: %s", e)
        # Ответ пользователю
        await query.message.reply_text(
            "✅ Спасибо! Мы проверим перевод и активируем PRO-доступ в течение нескольких минут."
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_button))
    logging.info("SellerApp Pay Bot запущен (polling).")
    app.run_polling()

if __name__ == "__main__":
    main()
