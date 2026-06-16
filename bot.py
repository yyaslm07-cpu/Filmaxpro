import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

BOT_TOKEN = "8688563134:AAHs6IP3l4Kbxx8FZx3XmOsSOpgGvjLMhA4"
bot = telebot.TeleBot(BOT_TOKEN)

BOT_USERNAME = "@VidGrabber2026_bot" 
CHANNEL_USERNAME = "@filmaxpro"
YOUTUBE_LINK = "https://youtube.com/@mosleh_2003?si=iRehojptx4LlM--6"
ADMIN_ID = 123456789  # ⚠️ ضع الـ ID الخاص بك هنا لكي تعمل ميزة الإذاعة

user_langs = {}
users_db = set() # لحفظ من استخدم البوت للإذاعة
user_urls = {} # لحفظ الرابط مؤقتاً حتى يختار المستخدم الصيغة

# الترجمات واللغات
texts = {
    'ar': {
        'welcome': f"⚖️┇أهلاً بك عزيزي، مع {BOT_USERNAME} يمكنك تحميل من عدة مواقع بصيغ متعددة الاستماع اليها في أي وقت،\n\n- قم بإرسال رابط المنشور فقط 📥",
        'usage': "💠┇طرق التحميل:\nأرسل رابط المقطع من أي منصة، أو اكتب اسم الأغنية للبحث في يوتيوب.",
        'force_sub': "عذراً عزيزي، يجب عليك الاشتراك في قنواتنا أولاً 👇",
        'sub_tg': "اشترك في قناة التلجرام 📢",
        'sub_yt': "اشترك في قناة اليوتيوب 📺",
        'usage_btn': "💡 طريقة استخدام البوت",
        'lang_btn': "🌐 تغيير لغة البوت",
        'choose_lang': "اختر لغتك المفضلة 👇",
        'select_format': "اختر الصيغة التي تود تحميلها 👇",
        'processing': "جاري المعالجة... ⏳",
        'success': f"تم التحميل بنجاح ✅\n{BOT_USERNAME}",
        'error': "حدث خطأ، تأكد من صحة الرابط أو أن الحساب ليس خاصاً."
    },
    'en': {
        'welcome': f"⚖️┇Welcome! With {BOT_USERNAME} you can download from multiple sites easily,\n\n- Just send the link 📥",
        'usage': "💠┇How to use:\nSend any video link or song name.",
        'force_sub': "Sorry, you must subscribe to our channels first 👇",
        'sub_tg': "Subscribe to Telegram 📢",
        'sub_yt': "Subscribe to YouTube 📺",
        'usage_btn': "💡 How to use",
        'lang_btn': "🌐 Change Language",
        'choose_lang': "Choose your preferred language 👇",
        'select_format': "Choose download format 👇",
        'processing': "Processing... ⏳",
        'success': f"Downloaded Successfully ✅\n{BOT_USERNAME}",
        'error': "Error occurred. Check the link."
    }
}
# تم اختصار اللغات في الكود لسهولة القراءة، يمكنك إضافة البقية بنسق مشابه

def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return True

def subscription_markup(lang):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(texts[lang]['sub_tg'], url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
               InlineKeyboardButton(texts[lang]['sub_yt'], url=YOUTUBE_LINK))
    return markup

def main_markup(lang):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(texts[lang]['usage_btn'], callback_data="show_usage"),
               InlineKeyboardButton(texts[lang]['lang_btn'], callback_data="change_language"))
    return markup

@bot.message_handler(commands=['start', 'cast'])
def handle_commands(message):
    chat_id = message.chat.id
    users_db.add(chat_id)
    lang = user_langs.get(chat_id, 'ar')

    if message.text.startswith('/cast'):
        if chat_id == ADMIN_ID:
            broadcast_msg = message.text.replace('/cast', '').strip()
            if not broadcast_msg:
                bot.reply_to(message, "اكتب الرسالة بعد الأمر هكذا: /cast السلام عليكم")
                return
            success = 0
            for uid in users_db.copy():
                try:
                    bot.send_message(uid, f"📢 رسالة من الإدارة:\n\n{broadcast_msg}")
                    success += 1
                except: pass
            bot.reply_to(message, f"✅ تم إرسال الإذاعة إلى {success} مستخدم.")
        return

    if not check_sub(chat_id):
        bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
        return
    
    bot.reply_to(message, texts[lang]['welcome'], reply_markup=main_markup(lang))

@bot.message_handler(func=lambda message: True)
def process_url(message):
    chat_id = message.chat.id
    users_db.add(chat_id)
    lang = user_langs.get(chat_id, 'ar')
    url = message.text

    if not url.startswith("http"): url = f"ytsearch1:{url}"
    
    if not check_sub(chat_id):
        bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
        return

    # حفظ الرابط وطلب اختيار الصيغة
    user_urls[chat_id] = url
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🎬 فيديو (Video)", callback_data="dl_vid"), 
               InlineKeyboardButton("🎵 صوت (Audio)", callback_data="dl_aud"))
    markup.row(InlineKeyboardButton("📝 استخراج الترجمة (.srt/.vtt)", callback_data="dl_sub"))
    
    bot.reply_to(message, texts[lang]['select_format'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    lang = user_langs.get(chat_id, 'ar')

    if call.data == "show_usage":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, texts[lang]['usage'])

    elif call.data == "change_language":
        bot.answer_callback_query(call.id)
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"), InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
        bot.send_message(chat_id, texts[lang]['choose_lang'], reply_markup=markup)

    elif call.data.startswith("lang_"):
        new_lang = call.data.split("_")[1]
        user_langs[chat_id] = new_lang
        bot.answer_callback_query(call.id, "✅ Done", show_alert=True)
        bot.edit_message_text(texts[new_lang]['welcome'], chat_id, call.message.message_id, reply_markup=main_markup(new_lang))

    elif call.data.startswith("dl_"):
        url = user_urls.get(chat_id)
        if not url:
            bot.answer_callback_query(call.id, "الرابط قديم، يرجى إرساله مجدداً", show_alert=True)
            return

        bot.edit_message_text(texts[lang]['processing'], chat_id, call.message.message_id)
        
        try:
            if call.data == "dl_vid":
                ydl_opts = {'format': 'best', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if 'entries' in info: info = info['entries'][0]
                    filename = ydl.prepare_filename(info)
                    
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("مشاركة البوت 📤", url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}"))
                    with open(filename, 'rb') as f:
                        bot.send_video(chat_id, f, caption=texts[lang]['success'], reply_markup=markup)
                    if os.path.exists(filename): os.remove(filename)

            elif call.data == "dl_aud":
                ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.mp3', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if 'entries' in info: info = info['entries'][0]
                    filename = ydl.prepare_filename(info)
                    with open(filename, 'rb') as f:
                        bot.send_audio(chat_id, f, caption=texts[lang]['success'])
                    if os.path.exists(filename): os.remove(filename)

            elif call.data == "dl_sub":
                ydl_opts = {
                    'skip_download': True, 'writesubtitles': True, 'writeautomaticsub': True,
                    'subtitleslangs': ['ar', 'en'], 'subtitlesformat': 'srt/vtt/best',
                    'outtmpl': '%(title)s.%(ext)s', 'quiet': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(url, download=True)
                    # البحث عن ملفات الترجمة في المجلد وإرسالها
                    sent = False
                    for file in os.listdir():
                        if file.endswith(('.srt', '.vtt')):
                            with open(file, 'rb') as f:
                                bot.send_document(chat_id, f, caption="تم استخراج ملف الترجمة بنجاح 📝")
                            os.remove(file)
                            sent = True
                    if not sent: bot.send_message(chat_id, "لم يتم العثور على ترجمات مرفقة بهذا المقطع ❌")

        except Exception as e:
            bot.edit_message_text(texts[lang]['error'], chat_id, call.message.message_id)

print("البوت الاحترافي يعمل الآن...")
bot.infinity_polling()

