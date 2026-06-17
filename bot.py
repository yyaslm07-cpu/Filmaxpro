import os
from flask import Flask
from threading import Thread

# تشغيل خادم ويب صغير لإرضاء Render
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بكامل طاقته!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# تشغيل الويب في خلفية منفصلة
Thread(target=run_web).start()

# --- هنا يبدأ كود بوت التيليجرام الخاص بك (bot.infinity_polling() إلخ) ---

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import yt_dlp
import os
import secrets
import string
import glob
import requests

# ✅ إصلاح 1: استخدم متغيرات بيئة بدل كتابة التوكن مباشرة
# في الخادم نفذ: export BOT_TOKEN="توكنك"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ضع_توكنك_هنا")
bot = telebot.TeleBot(BOT_TOKEN)

BOT_USERNAME = "@VidGrabber2026_bot"
CHANNEL_USERNAME = "@filmaxpro"
YOUTUBE_LINK = "https://youtube.com/@mosleh_2003?si=iRehojptx4LlM--6"
ADMIN_ID = 1983356771

# ✅ الحد الأقصى لحجم الملف (50MB = حد تيليجرام)
MAX_FILE_SIZE_MB = 50

# عدد نتائج البحث في كل صفحة
RESULTS_PER_PAGE = 5

user_langs = {}
users_db = set()

# ✅ إعدادات Supabase (تُقرأ من متغيرات البيئة في Render)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_TABLE = "bot_users"


def _supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def supabase_ready():
    return bool(SUPABASE_URL and SUPABASE_KEY)


def db_add_user(user_id):
    """يحفظ المستخدم في Supabase (يتجاهل إذا موجود) + في الذاكرة."""
    users_db.add(user_id)
    if not supabase_ready():
        return
    try:
        # upsert: لو موجود ما يكرر، لو جديد يضيفه
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
        headers = _supabase_headers()
        headers["Prefer"] = "resolution=ignore-duplicates,return=minimal"
        requests.post(url, headers=headers,
                      json={"user_id": user_id}, timeout=10)
    except Exception as e:
        print(f"Supabase add error: {e}")


def db_get_all_users():
    """يرجّع قائمة كل أرقام المستخدمين من Supabase."""
    if not supabase_ready():
        return list(users_db)
    try:
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?select=user_id"
        r = requests.get(url, headers=_supabase_headers(), timeout=15)
        if r.status_code == 200:
            ids = [row["user_id"] for row in r.json()]
            users_db.update(ids)
            return ids
    except Exception as e:
        print(f"Supabase get error: {e}")
    return list(users_db)


def db_count_users():
    """يرجّع عدد المستخدمين الكلي من Supabase."""
    if not supabase_ready():
        return len(users_db)
    try:
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?select=user_id"
        headers = _supabase_headers()
        headers["Prefer"] = "count=exact"
        headers["Range"] = "0-0"
        r = requests.get(url, headers=headers, timeout=15)
        # العدد يجي في هيدر Content-Range مثل: 0-0/123
        cr = r.headers.get("Content-Range", "")
        if "/" in cr:
            total = cr.split("/")[-1]
            if total.isdigit():
                return int(total)
    except Exception as e:
        print(f"Supabase count error: {e}")
    return len(users_db)


# تحميل المستخدمين الموجودين عند الإقلاع (مرة وحدة)
if supabase_ready():
    try:
        db_get_all_users()
        print(f"✅ تم تحميل {len(users_db)} مستخدم من Supabase")
    except Exception as e:
        print(f"تعذّر تحميل المستخدمين عند الإقلاع: {e}")
else:
    print("⚠️ Supabase غير مفعّل (لم تُضبط SUPABASE_URL / SUPABASE_KEY) — الحفظ مؤقت فقط")

# ✅ ذاكرة مؤقتة لربط روابط /dl_ بالروابط الحقيقية + نتائج البحث
DL_CACHE = {}       # token -> url
SEARCH_CACHE = {}   # search_token -> {entries, query, lang}

bot.set_my_commands([
    BotCommand("start", "بدء الان"),
    BotCommand("admin", "الادمن فقط")
])

texts = {
    'ar': {
        'welcome': f"⚖️┇أهلاً بك عزيزي، مع {BOT_USERNAME} يمكنك تحميل من عدة مواقع بصيغ متعددة والاستماع اليها في أي وقت،\n\n💠┇المنصات المدعومة:\n\n📥  يوتيوب         | 📥  انستكرام\n📥  فيسبوك       | 📥  تويتر/X\n📥  تيك توك       | 📥  سناب شات\n📥  ساوند كلاود  | 📥  بينترست\n📥  لايكي            | 📥  كواي\n📥  تيليجرام       | 📥  PMC Music\n📥  تمبلر            | 📥  ديلي موشن\n📥  فيميو           | 📥  ثريدز\n📥  فانيميت       | 📥  كاب كات\n\n- أرسل رابط المنشور للتحميل، أو اكتب اسم أي أغنية/مقطع للبحث 🔎\nولا تنسى قم بمشاركه البوت لاصدقائك  📥",
        'usage': "💠┇طرق استخدام البوت:\n\n1) أرسل رابط المقطع مباشرة من أي منصة مدعومة وسيعرض لك البوت الجودات للاختيار قبل التحميل.\n\n2) اكتب اسم أي أغنية أو مقطع (بدون رابط) وسيبحث لك البوت ويرسل النتائج، اضغط على /dl_ تحت أي نتيجة لتحميلها.",
        'force_sub': "عذراً عزيزي، يجب عليك الاشتراك في قنواتنا أولاً 👇",
        'sub_tg': "اشترك في قناة التلجرام 📢",
        'sub_yt': "اشترك في قناة اليوتيوب 📺",
        'usage_btn': "💡 كيفية استخدام البوت.",
        'lang_btn': "🌐 تغيير لغة البوت.",
        'choose_lang': "اختر لغتك المفضلة / Choose your language 👇",
        'processing': "جاري التحميل... ⏳",
        'invalid_link': "عذراً، أرسل رابطاً صحيحاً من المنصات المدعومة فقط ❌",
        'success': f"تم تحميل المقطع بنجاح ✅\n{BOT_USERNAME}",
        'audio_cap': f"المقطع الصوتي 🎵\n{BOT_USERNAME}",
        'share': "مشاركة البوت 📤",
        'error': "حدث خطأ، تأكد من صحة الرابط أو أن الحساب ليس خاصاً.",
        'too_large': f"❌ حجم الملف أكبر من {MAX_FILE_SIZE_MB}MB، لا يمكن إرساله عبر تيليجرام.",
        # مفاتيح جديدة
        'searching': "🔎 جاري البحث...",
        'no_results': "لا توجد نتائج لبحثك ❌",
        'fetching_info': "⏳ جاري جلب الجودات المتاحة...",
        'choose_quality': "اختر الجودة المطلوبة 👇",
        'expired': "انتهت صلاحية الطلب، أعد إرسال الرابط أو البحث 🔄",
        'search_header': '🔎 : نتائج البحث لـ "{q}"',
        'next_btn': "التالي ➡️",
        'prev_btn': "⬅️ السابق",
        'audio_btn': "🎵 صوت MP3",
        'video_btn': "🎬 فيديو",
    },
    'en': {
        'welcome': f"⚖️┇Welcome! With {BOT_USERNAME} you can download from multiple platforms easily,\n\n- Send a link to download, or type any song/clip name to search 🔎",
        'usage': "💠┇How to use:\n1) Send a link, then pick a quality before downloading.\n2) Type a song/clip name (no link) to search, then tap /dl_ under any result.",
        'force_sub': "Sorry, you must subscribe to our channels first 👇",
        'sub_tg': "Subscribe to Telegram 📢",
        'sub_yt': "Subscribe to YouTube 📺",
        'usage_btn': "💡 How to use.",
        'lang_btn': "🌐 Change Language.",
        'choose_lang': "Choose your preferred language 👇",
        'processing': "Downloading... ⏳",
        'invalid_link': "Sorry, please send a valid link only ❌",
        'success': f"Downloaded Successfully ✅\n{BOT_USERNAME}",
        'audio_cap': f"Audio Track 🎵\n{BOT_USERNAME}",
        'share': "Share Bot 📤",
        'error': "An error occurred. Make sure the link is public.",
        'too_large': f"❌ File size exceeds {MAX_FILE_SIZE_MB}MB, cannot send via Telegram.",
        # new keys
        'searching': "🔎 Searching...",
        'no_results': "No results found ❌",
        'fetching_info': "⏳ Fetching available qualities...",
        'choose_quality': "Choose quality 👇",
        'expired': "Request expired, please resend 🔄",
        'search_header': '🔎 : Search results for "{q}"',
        'next_btn': "Next ➡️",
        'prev_btn': "⬅️ Prev",
        'audio_btn': "🎵 Audio MP3",
        'video_btn': "🎬 Video",
    },
    'fr': {
        'welcome': f"⚖️┇Bienvenue! Avec {BOT_USERNAME} vous pouvez télécharger depuis plusieurs sites,\n\n- Envoyez simplement le lien 📥",
        'usage': "💠┇Comment utiliser:\nEnvoyez le lien de la vidéo.",
        'force_sub': "Désolé, vous devez d'abord vous abonner 👇",
        'sub_tg': "S'abonner à Telegram 📢",
        'sub_yt': "S'abonner à YouTube 📺",
        'usage_btn': "💡 Comment utiliser.",
        'lang_btn': "🌐 Changer de langue.",
        'choose_lang': "Choisissez votre langue 👇",
        'processing': "Téléchargement... ⏳",
        'invalid_link': "Veuillez envoyer un lien valide ❌",
        'success': f"Téléchargé avec succès ✅\n{BOT_USERNAME}",
        'audio_cap': f"Piste audio 🎵\n{BOT_USERNAME}",
        'share': "Partager le Bot 📤",
        'error': "Une erreur est survenue.",
        'too_large': f"❌ Fichier trop volumineux (>{MAX_FILE_SIZE_MB}MB)."
    },
    'it': {
        'welcome': f"⚖️┇Benvenuto! Con {BOT_USERNAME} puoi scaricare da molti siti,\n\n- Invia il link 📥",
        'usage': "💠┇Come usare:\nInvia il link del video.",
        'force_sub': "Devi prima iscriverti ai nostri canali 👇",
        'sub_tg': "Iscriviti a Telegram 📢",
        'sub_yt': "Iscriviti a YouTube 📺",
        'usage_btn': "💡 Come usare.",
        'lang_btn': "🌐 Cambia lingua.",
        'choose_lang': "Scegli la tua lingua 👇",
        'processing': "Scaricamento in corso... ⏳",
        'invalid_link': "Per favore invia un link valido ❌",
        'success': f"Scaricato con successo ✅\n{BOT_USERNAME}",
        'audio_cap': f"Traccia audio 🎵\n{BOT_USERNAME}",
        'share': "Condividi Bot 📤",
        'error': "Si è verificato un errore.",
        'too_large': f"❌ File troppo grande (>{MAX_FILE_SIZE_MB}MB)."
    },
    'hi': {
        'welcome': f"⚖️┇स्वागत है! {BOT_USERNAME} के साथ आप कई साइटों से डाउनलोड कर सकते हैं।\n\n- बस लिंक भेजें 📥",
        'usage': "💠┇उपयोग कैसे करें:\nवीडियो का लिंक भेजें।",
        'force_sub': "क्षमा करें, आपको पहले हमारे चैनल की सदस्यता लेनी होगी 👇",
        'sub_tg': "टेलीग्राम से जुड़ें 📢",
        'sub_yt': "यूट्यूब से जुड़ें 📺",
        'usage_btn': "💡 उपयोग कैसे करें।",
        'lang_btn': "🌐 भाषा बदलें।",
        'choose_lang': "अपनी भाषा चुनें 👇",
        'processing': "डाउनलोड हो रहा है... ⏳",
        'invalid_link': "कृपया केवल वैध लिंक भेजें ❌",
        'success': f"सफलतापूर्वक डाउनलोड किया गया ✅\n{BOT_USERNAME}",
        'audio_cap': f"ऑडियो ट्रैक 🎵\n{BOT_USERNAME}",
        'share': "बॉट साझा करें 📤",
        'error': "एक त्रुटि हुई। लिंक की जांच करें।",
        'too_large': f"❌ फ़ाइल {MAX_FILE_SIZE_MB}MB से बड़ी है।"
    },
    'bn': {
        'welcome': f"⚖️┇স্বাগতম! {BOT_USERNAME} এর মাধ্যমে আপনি অনেক সাইট থেকে ডাউনলোড করতে পারবেন।\n\n- শুধু লিংক পাঠান 📥",
        'usage': "💠┇কীভাবে ব্যবহার করবেন:\nভিডিও লিংক পাঠান।",
        'force_sub': "দুঃখিত, আপনাকে প্রথমে আমাদের চ্যানেলে সাবস্ক্রাইব করতে হবে 👇",
        'sub_tg': "টেলিগ্রামে সাবস্ক্রাইব করুন 📢",
        'sub_yt': "ইউটিউবে সাবস্ক্রাইব করুন 📺",
        'usage_btn': "💡 কীভাবে ব্যবহার করবেন।",
        'lang_btn': "🌐 ভাষা পরিবর্তন করুন।",
        'choose_lang': "আপনার ভাষা নির্বাচন করুন 👇",
        'processing': "ডাউনলোড হচ্ছে... ⏳",
        'invalid_link': "অনুগ্রহ করে একটি সঠিক লিংক পাঠান ❌",
        'success': f"সফলভাবে ডাউনলোড হয়েছে ✅\n{BOT_USERNAME}",
        'audio_cap': f"অডিও ট্র্যাক 🎵\n{BOT_USERNAME}",
        'share': "বট শেয়ার করুন 📤",
        'error': "একটি ত্রুটি ঘটেছে। লিংকটি পরীক্ষা করুন।",
        'too_large': f"❌ ফাইলের আকার {MAX_FILE_SIZE_MB}MB এর বেশি।"
    },
    'ru': {
        'welcome': f"⚖️┇Добро пожаловать! С {BOT_USERNAME} вы можете скачивать с многих сайтов.\n\n- Просто отправьте ссылку 📥",
        'usage': "💠┇Как использовать:\nОтправьте ссылку на видео.",
        'force_sub': "Извините, вы должны сначала подписаться на наши каналы 👇",
        'sub_tg': "Подписаться на Telegram 📢",
        'sub_yt': "Подписаться на YouTube 📺",
        'usage_btn': "💡 Как использовать.",
        'lang_btn': "🌐 Изменить язык.",
        'choose_lang': "Выберите ваш язык 👇",
        'processing': "Скачивание... ⏳",
        'invalid_link': "Пожалуйста, отправьте действительную ссылку ❌",
        'success': f"Успешно скачано ✅\n{BOT_USERNAME}",
        'audio_cap': f"Аудиодорожка 🎵\n{BOT_USERNAME}",
        'share': "Поделиться ботом 📤",
        'error': "Произошла ошибка. Проверьте ссылку.",
        'too_large': f"❌ Файл больше {MAX_FILE_SIZE_MB}MB, невозможно отправить."
    }
}


# ✅ دالة آمنة لجلب النصوص الجديدة مع رجوع تلقائي للعربية/الإنجليزية
def t(lang, key):
    return (texts.get(lang, {}).get(key)
            or texts['ar'].get(key)
            or texts['en'].get(key)
            or key)


# ✅ توليد رمز قصير آمن للأوامر (حروف وأرقام فقط)
def rand_token(n=10):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(n))


# ✅ تنظيف بسيط للذاكرة المؤقتة لمنع تضخمها
def _trim_caches():
    if len(DL_CACHE) > 6000:
        DL_CACHE.clear()
    if len(SEARCH_CACHE) > 300:
        SEARCH_CACHE.clear()


def fmt_duration(seconds):
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return "0:00"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fmt_views(v):
    try:
        v = int(v)
    except (TypeError, ValueError):
        return "0"
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.1f}K"
    return str(v)


# ✅ إصلاح 2: إعدادات yt_dlp المحسّنة لدعم جميع المنصات
def get_ydl_opts_video(output_template):
    return {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_template,
        'quiet': True,
        'nocheckcertificate': True,
        'merge_output_format': 'mp4',
        # ✅ Headers تساعد في تجاوز حماية بعض المنصات (Instagram, TikTok, إلخ)
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        # ✅ إيقاف playlist تلقائياً (لمنع تحميل قوائم كاملة)
        'noplaylist': True,
        'max_filesize': MAX_FILE_SIZE_MB * 1024 * 1024,
    }


def get_ydl_opts_audio(output_template):
    return {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'quiet': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        # ✅ إصلاح 3: تحويل الصوت لـ mp3 بدلاً من webm لدعم كل الأجهزة
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }


# ✅ جديد: إعدادات تحميل حسب الجودة المختارة
def get_ydl_opts_quality(output_template, quality):
    opts = get_ydl_opts_video(output_template)
    opts.pop('max_filesize', None)  # نتحقق من الحجم يدوياً بعد التحميل
    if quality == 'best':
        opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    else:
        h = int(quality)
        opts['format'] = (
            f'bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/'
            f'best[height<={h}][ext=mp4]/best[height<={h}]/best'
        )
    return opts


# ✅ جديد: إعدادات البحث (سريع، بدون تحميل)
def get_ydl_opts_search():
    return {
        'quiet': True,
        'nocheckcertificate': True,
        'extract_flat': True,
        'skip_download': True,
        'default_search': 'ytsearch',
    }


def get_ydl_opts_info():
    return {
        'quiet': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'skip_download': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
    }


def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return True


def subscription_markup(lang):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(texts[lang]['sub_tg'], url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
        InlineKeyboardButton(texts[lang]['sub_yt'], url=YOUTUBE_LINK)
    )
    return markup


def main_markup(lang):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(texts[lang]['usage_btn'], callback_data="show_usage"),
        InlineKeyboardButton(texts[lang]['lang_btn'], callback_data="change_language")
    )
    return markup


def lang_markup():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"), InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
    markup.row(InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"), InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it"))
    markup.row(InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi"), InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn"))
    markup.row(InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"))
    return markup


# ✅ جديد: بناء أزرار الجودة من معلومات الفيديو
def build_quality_markup(info, token, lang):
    formats = info.get('formats', []) or []
    heights = sorted({
        f['height'] for f in formats
        if f.get('height') and f.get('vcodec') not in (None, 'none')
    })
    preferred = [144, 240, 360, 480, 720, 1080, 1440, 2160]
    filtered = [h for h in heights if h in preferred]
    heights = filtered or heights

    markup = InlineKeyboardMarkup(row_width=2)
    row = []
    if heights:
        for h in heights:
            row.append(InlineKeyboardButton(f"🎬 {h}p", callback_data=f"dl|{token}|{h}"))
            if len(row) == 2:
                markup.row(*row)
                row = []
        if row:
            markup.row(*row)
    else:
        # منصات بجودة واحدة (تيك توك/انستقرام أحياناً)
        markup.row(InlineKeyboardButton(t(lang, 'video_btn'), callback_data=f"dl|{token}|best"))

    markup.row(InlineKeyboardButton(t(lang, 'audio_btn'), callback_data=f"dl|{token}|audio"))
    return markup


# ✅ جديد: عرض الجودات لرابط معين قبل التحميل
def send_quality_options(message, url, lang):
    # ✅ السلوك المطلوب: تحميل مباشر للفيديو + الصوت بدون اختيار جودة
    chat_id = message.chat.id
    status = bot.reply_to(message, texts[lang]['processing'])  # "جاري التحميل... ⏳"
    token2 = rand_token()
    vid_file = None
    aud_file = None
    try:
        # ── تحميل الفيديو ──
        vid_template = f'vid_{chat_id}_{token2}.%(ext)s'
        with yt_dlp.YoutubeDL(get_ydl_opts_video(vid_template)) as ydl:
            info = ydl.extract_info(url, download=True)
            vid_file = ydl.prepare_filename(info)

        # بعد الدمج قد يصبح الامتداد mp4
        if vid_file and not os.path.exists(vid_file):
            base = os.path.splitext(vid_file)[0]
            if os.path.exists(base + '.mp4'):
                vid_file = base + '.mp4'

        if vid_file and os.path.exists(vid_file):
            size_mb = os.path.getsize(vid_file) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                bot.edit_message_text(texts[lang]['too_large'], chat_id, status.message_id)
            else:
                likes = info.get('like_count') or 0
                views = info.get('view_count') or 0
                duration = info.get('duration_string') or fmt_duration(info.get('duration'))

                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton(f"❤️ {likes:,}", callback_data="n"),
                    InlineKeyboardButton(f"👁 {views:,}", callback_data="n"),
                    InlineKeyboardButton(f"⏱ {duration}", callback_data="n")
                )
                markup.row(InlineKeyboardButton(
                    texts[lang]['share'],
                    url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}"
                ))

                with open(vid_file, 'rb') as f:
                    bot.send_video(chat_id, f, caption=texts[lang]['success'],
                                   reply_markup=markup, reply_to_message_id=message.message_id)

        # ── تحميل الصوت بصيغة mp3 ──
        aud_template = f'aud_{chat_id}_{token2}.%(ext)s'
        with yt_dlp.YoutubeDL(get_ydl_opts_audio(aud_template)) as ydl:
            info_a = ydl.extract_info(url, download=True)
        aud_file = f'aud_{chat_id}_{token2}.mp3'
        if os.path.exists(aud_file):
            size_a = os.path.getsize(aud_file) / (1024 * 1024)
            if size_a <= MAX_FILE_SIZE_MB:
                with open(aud_file, 'rb') as f:
                    bot.send_audio(
                        chat_id, f,
                        caption=texts[lang]['audio_cap'],
                        title=info_a.get('title', 'Audio'),
                        performer=BOT_USERNAME
                    )

        # حذف رسالة "جاري التحميل"
        try:
            bot.delete_message(chat_id, status.message_id)
        except:
            pass

    except Exception as e:
        print(f"Download error for {chat_id}: {e}")
        try:
            bot.edit_message_text(texts[lang]['error'], chat_id, status.message_id)
        except:
            bot.send_message(chat_id, texts[lang]['error'])
    finally:
        for pattern in (f'vid_{chat_id}_{token2}.*', f'aud_{chat_id}_{token2}.*'):
            for f in glob.glob(pattern):
                try:
                    os.remove(f)
                except:
                    pass


# ✅ جديد: التحميل الفعلي بالجودة المختارة
def do_download(chat_id, url, quality, lang, status_msg_id=None):
    token2 = rand_token()
    out_file = None
    try:
        if quality == 'audio':
            template = f'aud_{chat_id}_{token2}.%(ext)s'
            with yt_dlp.YoutubeDL(get_ydl_opts_audio(template)) as ydl:
                info = ydl.extract_info(url, download=True)
            out_file = f'aud_{chat_id}_{token2}.mp3'
            if os.path.exists(out_file):
                size_mb = os.path.getsize(out_file) / (1024 * 1024)
                if size_mb > MAX_FILE_SIZE_MB:
                    if status_msg_id:
                        bot.edit_message_text(texts[lang]['too_large'], chat_id, status_msg_id)
                    else:
                        bot.send_message(chat_id, texts[lang]['too_large'])
                    return
                with open(out_file, 'rb') as f:
                    bot.send_audio(
                        chat_id, f,
                        caption=texts[lang]['audio_cap'],
                        title=info.get('title', 'Audio'),
                        performer=BOT_USERNAME
                    )
        else:
            template = f'vid_{chat_id}_{token2}.%(ext)s'
            with yt_dlp.YoutubeDL(get_ydl_opts_quality(template, quality)) as ydl:
                info = ydl.extract_info(url, download=True)
                out_file = ydl.prepare_filename(info)

            # بعد الدمج قد يصبح الامتداد mp4
            if out_file and not os.path.exists(out_file):
                base = os.path.splitext(out_file)[0]
                if os.path.exists(base + '.mp4'):
                    out_file = base + '.mp4'

            if out_file and os.path.exists(out_file):
                size_mb = os.path.getsize(out_file) / (1024 * 1024)
                if size_mb > MAX_FILE_SIZE_MB:
                    if status_msg_id:
                        bot.edit_message_text(texts[lang]['too_large'], chat_id, status_msg_id)
                    else:
                        bot.send_message(chat_id, texts[lang]['too_large'])
                    return

                likes = info.get('like_count') or 0
                views = info.get('view_count') or 0
                duration = info.get('duration_string') or fmt_duration(info.get('duration'))

                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton(f"❤️ {likes:,}", callback_data="n"),
                    InlineKeyboardButton(f"👁 {views:,}", callback_data="n"),
                    InlineKeyboardButton(f"⏱ {duration}", callback_data="n")
                )
                markup.row(InlineKeyboardButton(
                    texts[lang]['share'],
                    url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}"
                ))

                with open(out_file, 'rb') as f:
                    bot.send_video(chat_id, f, caption=texts[lang]['success'], reply_markup=markup)

        # حذف رسالة الحالة بعد النجاح
        if status_msg_id:
            try:
                bot.delete_message(chat_id, status_msg_id)
            except:
                pass

    except Exception as e:
        print(f"Download error for {chat_id}: {e}")
        try:
            if status_msg_id:
                bot.edit_message_text(texts[lang]['error'], chat_id, status_msg_id)
            else:
                bot.send_message(chat_id, texts[lang]['error'])
        except:
            pass
    finally:
        # حذف كل الملفات المؤقتة المرتبطة بهذا الطلب
        for pattern in (f'vid_{chat_id}_{token2}.*', f'aud_{chat_id}_{token2}.*'):
            for f in glob.glob(pattern):
                try:
                    os.remove(f)
                except:
                    pass


# ✅ جديد: تنفيذ البحث
def do_search(query, max_results=20):
    with yt_dlp.YoutubeDL(get_ydl_opts_search()) as ydl:
        info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
    return info.get('entries', []) or []


# ✅ جديد: بناء نص + أزرار صفحة نتائج البحث
def render_search_page(stoken, page):
    data = SEARCH_CACHE.get(stoken)
    if not data:
        return None, None
    entries = data['entries']
    query = data['query']
    lang = data.get('lang', 'ar')

    start = page * RESULTS_PER_PAGE
    chunk = entries[start:start + RESULTS_PER_PAGE]

    lines = [t(lang, 'search_header').format(q=query), ""]
    for e in chunk:
        title = e.get('title') or '—'
        uploader = e.get('uploader') or e.get('channel') or ''
        dur = fmt_duration(e.get('duration'))
        views = fmt_views(e.get('view_count'))
        tok = e.get('dl_token')
        lines.append(f"🎬 {title}")
        if uploader:
            lines.append(f"👤 {uploader}")
        lines.append(f"⏱ {dur} - 👁 {views}")
        lines.append(f"/dl_{tok}")
        lines.append("")
    text = "\n".join(lines)

    markup = InlineKeyboardMarkup()
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(t(lang, 'prev_btn'), callback_data=f"pg|{stoken}|{page-1}"))
    if start + RESULTS_PER_PAGE < len(entries):
        nav.append(InlineKeyboardButton(t(lang, 'next_btn'), callback_data=f"pg|{stoken}|{page+1}"))
    if nav:
        markup.row(*nav)
    return text, markup


# ✅ جديد: معالجة البحث
def handle_search(message, query):
    chat_id = message.chat.id
    lang = user_langs.get(chat_id, 'ar')

    if not check_sub(chat_id):
        bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
        return

    status = bot.reply_to(message, t(lang, 'searching'))
    try:
        entries = [e for e in do_search(query, 20) if e and e.get('id')]
        if not entries:
            bot.edit_message_text(t(lang, 'no_results'), chat_id, status.message_id)
            return

        stoken = rand_token()
        _trim_caches()
        for e in entries:
            tok = rand_token()
            e['dl_token'] = tok
            DL_CACHE[tok] = f"https://www.youtube.com/watch?v={e['id']}"
        SEARCH_CACHE[stoken] = {'entries': entries, 'query': query, 'lang': lang}

        text, markup = render_search_page(stoken, 0)
        bot.edit_message_text(text, chat_id, status.message_id,
                              reply_markup=markup, disable_web_page_preview=True)
    except Exception as e:
        print(f"Search error for {chat_id}: {e}")
        try:
            bot.edit_message_text(texts[lang]['error'], chat_id, status.message_id)
        except:
            bot.send_message(chat_id, texts[lang]['error'])


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    db_add_user(chat_id)
    lang = user_langs.get(chat_id, 'ar')
    if not check_sub(chat_id):
        bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
        return
    bot.reply_to(message, texts[lang]['welcome'], reply_markup=main_markup(lang))


@bot.message_handler(commands=['admin'])
def handle_admin(message):
    chat_id = message.chat.id
    if chat_id == ADMIN_ID:
        count = db_count_users()
        bot.reply_to(
            message,
            "مرحباً بك يا مدير البوت 👑\n\n"
            f"👥 عدد المستخدمين: {count}\n\n"
            "الأوامر المتاحة لك:\n"
            "• /stats — عرض عدد المستخدمين\n"
            "• /cast رسالتك — إرسال إذاعة لجميع المستخدمين"
        )
    else:
        bot.reply_to(message, "عذراً، هذا الأمر مخصص لإدارة البوت فقط ❌")


@bot.message_handler(commands=['stats'])
def handle_stats(message):
    chat_id = message.chat.id
    if chat_id != ADMIN_ID:
        return
    count = db_count_users()
    storage = "Supabase (دائم) ✅" if supabase_ready() else "ذاكرة مؤقتة ⚠️"
    bot.reply_to(message, f"📊 إحصائيات البوت\n\n👥 عدد المستخدمين: {count}\n💾 التخزين: {storage}")


@bot.message_handler(commands=['cast'])
def handle_cast(message):
    chat_id = message.chat.id
    if chat_id != ADMIN_ID:
        return
    parts = message.text.split(None, 1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(message, "اكتب الرسالة بعد الأمر هكذا:\n/cast رسالتكم")
        return
    broadcast_msg = parts[1].strip()
    # نجيب أحدث قائمة كاملة من Supabase
    all_users = db_get_all_users()
    status = bot.reply_to(message, f"⏳ جاري الإرسال إلى {len(all_users)} مستخدم...")
    success = 0
    failed = 0
    for uid in all_users:
        try:
            bot.send_message(uid, f"📢 رسالة من الإدارة:\n\n{broadcast_msg}")
            success += 1
        except:
            failed += 1
    try:
        bot.edit_message_text(
            f"✅ تم إرسال الإذاعة.\n\n📨 وصلت: {success}\n❌ فشلت: {failed}",
            chat_id, status.message_id
        )
    except:
        bot.reply_to(message, f"✅ تم الإرسال إلى {success} مستخدم.")


# ✅ جديد: معالج أوامر /dl_ القادمة من نتائج البحث
@bot.message_handler(func=lambda m: bool(m.text) and m.text.startswith('/dl_'))
def handle_dl(message):
    chat_id = message.chat.id
    db_add_user(chat_id)
    lang = user_langs.get(chat_id, 'ar')

    if not check_sub(chat_id):
        bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
        return

    token = message.text.strip()[4:].split('@')[0].split()[0]
    url = DL_CACHE.get(token)
    if not url:
        bot.reply_to(message, t(lang, 'expired'))
        return
    send_quality_options(message, url, lang)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    lang = user_langs.get(chat_id, 'ar')

    if call.data == "show_usage":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, texts[lang]['usage'])

    elif call.data == "change_language":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, texts[lang]['choose_lang'], reply_markup=lang_markup())

    elif call.data.startswith("lang_"):
        new_lang = call.data.split("_")[1]
        if new_lang in texts:
            user_langs[chat_id] = new_lang
            bot.answer_callback_query(call.id, "✅ Done", show_alert=False)
            bot.edit_message_text(texts[new_lang]['welcome'], chat_id, call.message.message_id, reply_markup=main_markup(new_lang))

    # ✅ جديد: التنقل بين صفحات البحث
    elif call.data.startswith("pg|"):
        try:
            _, stoken, page = call.data.split("|")
            page = int(page)
        except:
            bot.answer_callback_query(call.id)
            return
        if stoken not in SEARCH_CACHE:
            bot.answer_callback_query(call.id, t(lang, 'expired'), show_alert=True)
            return
        bot.answer_callback_query(call.id)
        text, markup = render_search_page(stoken, page)
        if text:
            try:
                bot.edit_message_text(text, chat_id, call.message.message_id,
                                      reply_markup=markup, disable_web_page_preview=True)
            except:
                pass

    # ✅ جديد: اختيار الجودة وبدء التحميل
    elif call.data.startswith("dl|"):
        try:
            _, token, quality = call.data.split("|")
        except:
            bot.answer_callback_query(call.id)
            return
        url = DL_CACHE.get(token)
        if not url:
            bot.answer_callback_query(call.id, t(lang, 'expired'), show_alert=True)
            return
        bot.answer_callback_query(call.id)
        try:
            bot.edit_message_text(texts[lang]['processing'], chat_id, call.message.message_id)
        except:
            pass
        do_download(chat_id, url, quality, lang, call.message.message_id)

    elif call.data == "n":
        # زر معلوماتي فقط، لا يفعل شيئاً
        bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: True)
def process_url(message):
    if not message.text:
        return
    chat_id = message.chat.id
    db_add_user(chat_id)
    lang = user_langs.get(chat_id, 'ar')
    text = message.text.strip()

    # تجاهل الأوامر غير المعروفة
    if text.startswith('/'):
        return

    if text.startswith("http"):
        # رابط → عرض الجودات قبل التحميل
        if not check_sub(chat_id):
            bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
            return
        send_quality_options(message, text, lang)
    else:
        # نص عادي → بحث
        handle_search(message, text)


print("✅ البوت يعمل الآن...")
bot.remove_webhook()
bot.infinity_polling(skip_pending=True, timeout=30)
