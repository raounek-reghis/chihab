import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ─── إعداد اللوغ ───────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── مفاتيح API ────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["8946579180:AAGDJD4WL_8ZNaII7jiD8-27hAOao5HqBfo"]
GEMINI_API_KEY = os.environ["AQ.Ab8RN6KRZctnaRjPowOAk7AlwkeApOLmGKuXqsaAZ4Xz4y6_Qw"]
ALLOWED_USER_ID = int(os.environ.get("8946579180", "0"))
PORT = int(os.environ.get("PORT", "8000"))

# ─── إعدادات الإعلانات ─────────────────────────────────────
AD_EVERY_N_REPLIES = 5

ADS = [
    {
        "text": "📢 هل تحب الأنمي؟ انضم لقناتنا للمزيد من التوصيات يومياً!",
        "button_text": "📺 انضم للقناة",
        "button_url": "https://t.me/karba3_40"
    {
        "text": "🎌 قناة الأنمي والأفلام — أفضل التوصيات كل يوم، انضم الآن!",
        "button_text": "🔔 اشترك مجاناً",
        "button_url": "https://t.me/karba3_40"    },
]

# ─── إعداد Gemini ───────────────────────────────────────────
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""أنت مساعد متخصص في اقتراح الأنميات والأفلام.
تتحدث بالعربية دائماً وتعطي توصيات مفيدة مع وصف مختصر وتقييم لكل عمل.
عندما تقترح أنميات أو أفلام، قدّم دائماً:
- اسم العمل (بالعربي والإنجليزي)
- نوعه (أكشن / رومانسي / خيال علمي / إلخ)
- وصف قصير ومشوّق
- تقييمك من 10
- سبب توصيتك به
استخدم إيموجيات مناسبة لتجميل ردودك."""
)

# ─── بيانات المستخدمين ─────────────────────────────────────
user_chats: dict[int, any] = {}
user_reply_count: dict[int, int] = {}

# ─── سيرفر ويب صغير (مطلوب لـ Koyeb) ─────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        pass  # إخفاء لوغ الطلبات

def run_web_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info(f"🌐 Web server running on port {PORT}")
    server.serve_forever()

# ─── فلتر التحقق من المستخدم ───────────────────────────────
async def is_allowed(update: Update) -> bool:
    user_id = update.effective_user.id
    if ALLOWED_USER_ID != 0 and user_id != ALLOWED_USER_ID:
        await update.effective_message.reply_text("⛔ عذراً، هذا البوت خاص ولا يمكنك استخدامه.")
        logger.warning(f"محاولة دخول غير مصرح بها من ID: {user_id}")
        return False
    return True

# ─── إرسال إعلان إذا حان وقته ─────────────────────────────
async def maybe_send_ad(update: Update, user_id: int) -> None:
    import random
    count = user_reply_count.get(user_id, 0)
    if count > 0 and count % AD_EVERY_N_REPLIES == 0:
        ad = random.choice(ADS)
        keyboard = [[InlineKeyboardButton(ad["button_text"], url=ad["button_url"])]]
        await update.effective_message.reply_text(
            f"━━━━━━━━━━━━━━━\n{ad['text']}\n━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

# ─── /myid ─────────────────────────────────────────────────
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"🪪 معلوماتك:\n"
        f"• الاسم: {user.full_name}\n"
        f"• الـ ID: `{user.id}`\n\n"
        f"انسخ الـ ID وضعه في Koyeb كـ ALLOWED\\_USER\\_ID",
        parse_mode="Markdown",
    )

# ─── /start ────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_allowed(update):
        return
    keyboard = [
        [
            InlineKeyboardButton("🎌 اقترح أنمي", callback_data="suggest_anime"),
            InlineKeyboardButton("🎬 اقترح فيلم", callback_data="suggest_movie"),
        ],
        [
            InlineKeyboardButton("🔥 الأكثر شعبية", callback_data="popular"),
            InlineKeyboardButton("🎲 اختيار عشوائي", callback_data="random"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *مرحباً بك في بوت الأنمي والأفلام!*\n\n"
        "يمكنني مساعدتك في:\n"
        "🎌 اقتراح أنميات رائعة\n"
        "🎬 اقتراح أفلام مميزة\n"
        "💬 أو اكتب لي ما تحب وسأقترح لك!\n\n"
        "اختر من القائمة أو اكتب طلبك مباشرة:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

# ─── /help ─────────────────────────────────────────────────
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_allowed(update):
        return
    await update.message.reply_text(
        "📖 *كيفية استخدام البوت:*\n\n"
        "• اكتب أي شيء مثل: _'اقترح لي أنمي أكشن'_\n"
        "• أو: _'أريد فيلم رومانسي'_\n"
        "• أو: _'ما أفضل أنمي خيال علمي؟'_\n\n"
        "الأوامر المتاحة:\n"
        "/start - القائمة الرئيسية\n"
        "/help - المساعدة\n"
        "/clear - مسح سجل المحادثة",
        parse_mode="Markdown",
    )

# ─── /clear ────────────────────────────────────────────────
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_allowed(update):
        return
    user_id = update.effective_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    await update.message.reply_text("🗑️ تم مسح سجل المحادثة. ابدأ محادثة جديدة!")

# ─── أزرار inline ──────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not await is_allowed(update):
        return

    prompts = {
        "suggest_anime": "اقترح لي أنمي رائع مع وصف تفصيلي",
        "suggest_movie": "اقترح لي فيلم رائع مع وصف تفصيلي",
        "popular": "ما هي أشهر الأنميات والأفلام حالياً؟",
        "random": "اقترح لي عملاً عشوائياً مميزاً (أنمي أو فيلم)",
    }

    user_id = query.from_user.id
    user_text = prompts.get(query.data, "مرحباً")
    await query.message.reply_text("⏳ جاري التفكير...")
    response = await get_ai_response(user_id, user_text)
    await query.message.reply_text(response, parse_mode="Markdown")

    user_reply_count[user_id] = user_reply_count.get(user_id, 0) + 1
    await maybe_send_ad(update, user_id)

# ─── رسائل نصية ────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_allowed(update):
        return
    user_id = update.effective_user.id
    user_text = update.message.text

    await update.message.reply_text("⏳ جاري التفكير...")
    response = await get_ai_response(user_id, user_text)
    await update.message.reply_text(response, parse_mode="Markdown")

    user_reply_count[user_id] = user_reply_count.get(user_id, 0) + 1
    await maybe_send_ad(update, user_id)

# ─── استدعاء Gemini API ────────────────────────────────────
async def get_ai_response(user_id: int, user_text: str) -> str:
    try:
        if user_id not in user_chats:
            user_chats[user_id] = model.start_chat(history=[])
        chat = user_chats[user_id]
        response = chat.send_message(user_text)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "❌ حدث خطأ، حاول مرة أخرى لاحقاً."

# ─── تشغيل البوت ───────────────────────────────────────────
def main() -> None:
    # شغّل سيرفر الويب في خيط منفصل
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 البوت يعمل الآن...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
