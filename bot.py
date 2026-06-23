import os
from flask import Flask
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import time

# تشغيل خادم ويب صغير لإرضاء Render
app = Flask(__name__)


@app.route('/')
def home():
    return "البوت يعمل بكامل طاقته!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# تشغيل الويب في خلفية منفصلة
Thread(target=run_web, daemon=True).start()

# --- كود بوت التيليجرام ---

# تحديث أداة التحميل تلقائياً عند كل إقلاع
print("🔄 جاري تحديث مكتبة yt-dlp تلقائياً...")
os.system("pip install -U yt-dlp")

import telebot
import telebot.apihelper as apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import yt_dlp
import secrets
import string
import glob
import requests

# 🔥 [الرقعة السحرية] 🔥 اختراق مكتبة yt-dlp داخلياً لتجبر على قبول نطاق threads.com الإقليمي وحل المشكلة للأبد
try:
    import yt_dlp.extractor.threads
    yt_dlp.extractor.threads.ThreadsIE._VALID_URL = r'https?://(?:www\.)?threads\.(?:net|com)/(?:@(?P<username>[^/]+)/post/|t/)(?P<id>[^/?#]+)'
    print("✅ تم رقع مكتبة yt-dlp بنجاح لدعم نطاقات ثريدز .com و .net معاً!")
except Exception as e:
    print(f"⚠️ فشل رقع مكتبة yt-dlp: {e}")

# مهلات أطول لرفع الملفات الكبيرة
apihelper.CONNECT_TIMEOUT = 30
apihelper.READ_TIMEOUT = 300
apihelper.RETRY_ON_ERROR = True

# التوكن والمعرفات من متغيرات البيئة لحماية البيانات
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ضع_توكنك_هنا")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 1983356771))

if BOT_TOKEN == "ضع_توكنك_هنا":
    print("⚠️ تحذير: لم يتم ضبط BOT_TOKEN في متغيرات البيئة!")

bot = telebot.TeleBot(BOT_TOKEN)

BOT_USERNAME = "@VidGrabber2026_bot"
CHANNEL_USERNAME = "@filmaxpro"
YOUTUBE_LINK = "https://youtube.com/@mosleh_2003?si=iRehojptx4LlM--6"

# الحد الأقصى لحجم الملف
MAX_FILE_SIZE_MB = 50
DOWNLOAD_HEIGHTS = [720, 480, 360, 240]
COOKIES_FILE = "cookies.txt"

FFMPEG_LOCATION = None


def _detect_ffmpeg():
    global FFMPEG_LOCATION
    from shutil import which
    sys_ffmpeg = which("ffmpeg")
    if sys_ffmpeg:
        FFMPEG_LOCATION = os.path.dirname(sys_ffmpeg)
        print(f"✅ ffmpeg موجود على النظام: {sys_ffmpeg}")
        return
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        FFMPEG_LOCATION = os.path.dirname(exe)
        print(f"✅ ffmpeg عبر imageio-ffmpeg: {exe}")
        return
    except Exception as e:
        print(f"⚠️ imageio-ffmpeg غير متاح: {e}")


_detect_ffmpeg()


def _build_cookies_file():
    if os.path.exists(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0:
        print(f"✅ ملف الكوكيز موجود ({os.path.getsize(COOKIES_FILE)} بايت)")
        return
    render_secret = "/etc/secrets/cookies.txt"
    if os.path.exists(render_secret) and os.path.getsize(render_secret) > 0:
        try:
            with open(render_secret, "r", encoding="utf-8", errors="ignore") as src:
                data = src.read()
            with open(COOKIES_FILE, "w", encoding="utf-8") as dst:
                dst.write(data)
            print(f"✅ تم نسخ الكوكيز من Secret File ({os.path.getsize(COOKIES_FILE)} بايت)")
            return
        except Exception as e:
            print(f"❌ تعذّر نسخ Secret File: {e}")
    content = os.environ.get("COOKIES_CONTENT", "")
    if not content.strip():
        print("⚠️ لا يوجد كوكيز المدمجة")
        return
    try:
        if "\\n" in content and "\n" not in content:
            content = content.replace("\\n", "\n")
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ تم إنشاء ملف الكوكيز ({os.path.getsize(COOKIES_FILE)} بايت)")
    except Exception as e:
        print(f"❌ تعذّر كتابة ملف الكوكيز: {e}")


_build_cookies_file()

download_executor = ThreadPoolExecutor(max_workers=4)
user_langs = {}
users_db = set()

# إعدادات Supabase
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
    users_db.add(user_id)
    if not supabase_ready():
        return
    try:
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
        headers = _supabase_headers()
        headers["Prefer"] = "resolution=ignore-duplicates,return=minimal"
        requests.post(url, headers=headers, json={"user_id": user_id}, timeout=10)
    except Exception as e:
        print(f"Supabase add error: {e}")


def db_get_all_users():
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
    if not supabase_ready():
        return len(users_db)
    try:
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?select=user_id"
        headers = _supabase_headers()
        headers["Prefer"] = "count=exact"
        headers["Range"] = "0-0"
        r = requests.get(url, headers=headers, timeout=15)
        cr = r.headers.get("Content-Range", "")
        if "/" in cr:
            total = cr.split("/")[-1]
            if total.isdigit():
                return int(total)
    except Exception as e:
        print(f"Supabase count error: {e}")
    return len(users_db)


if supabase_ready():
    try:
        db_get_all_users()
        print(f"✅ تم تحميل {len(users_db)} مستخدم من Supabase")
    except Exception as e:
        print(f"تعذّر تحميل المستخدمين عند الإقلاع: {e}")

bot.set_my_commands([
    BotCommand("start", "بدء الان"),
    BotCommand("admin", "الادمن فقط")
])

texts = {
    'ar': {
        'welcome': f"⚖️┇أهلاً بك عزيزي، مع {BOT_USERNAME} يمكنك تحميل من عدة مواقع بصيغ متعددة والاستماع اليها في أي وقت،\n\n💠┇المنصات المدعومة:\n\n📥  يوتيوب         | 📥  انستكرام\n📥  فيسبوك       | 📥  تويتر/X\n📥  تيك توك       | 📥  سناب شات\n📥  ساوند كلاود  | 📥  بينترست\n📥  لايكي            | 📥  كواي\n📥  تيليجرام       | 📥  PMC Music\n📥  تمبلر            | 📥  ديلي موشن\n📥  فيميو           | 📥  ثريدز\n📥  فانيميت       | 📥  كاب كات\n\n- أرسل رابط المنشور للتحميل 📥\nولا تنسى قم بمشاركه البوت لاصدقائك  📥",
        'usage': "💠┇طرق استخدام البوت:\n\nأرسل رابط المقطع مباشرة من أي منصة مدعومة وسيحمّل لك البوت الفيديو ثم الصوت تلقائياً.",
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
        'error': "حدث خطأ، تأكد من صحة الرابط أو أن الحساب ليس خاصاً ❌",
        'too_large': f"❌ المقطع أكبر من {MAX_FILE_SIZE_MB}MB حتى بعد خفض الجودة، ولا يمكن إرساله عبر تيليجرام.",
    },
    'en': {
        'welcome': f"⚖️┇Welcome! With {BOT_USERNAME} you can download from multiple platforms easily,\n\n- Send a link to download 📥",
        'usage': "💠┇How to use:\nSend a link, the bot will download the video then the audio automatically.",
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
        'too_large': f"❌ File size exceeds {MAX_FILE_SIZE_MB}MB even after lowering quality, cannot send via Telegram.",
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
        'too_large': f"❌ Fichier trop volumineux (>{MAX_FILE_SIZE_MB}MB).",
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
        'too_large': f"❌ File troppo grande (>{MAX_FILE_SIZE_MB}MB).",
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
        'success': f"سफलतापूर्वक डाउनलोड किया गया ✅\n{BOT_USERNAME}",
        'audio_cap': f"ऑडियो ट्रैक 🎵\n{BOT_USERNAME}",
        'share': "बॉट साझा करें 📤",
        'error': "एक त्रुटિ हुई। लिंक की जांच करें।",
        'too_large': f"❌ फ़ाइल {MAX_FILE_SIZE_MB}MB से बड़ी है।",
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
        'error': "একটি ত্রুটি ঘটেছে। लिंकটি परीक्षा করুন।",
        'too_large': f"❌ ফাইলের আকার {MAX_FILE_SIZE_MB}MB এর বেশি।",
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
        'too_large': f"❌ Файл больше {MAX_FILE_SIZE_MB}MB, невозможно отправить.",
    }
}


def t(lang, key):
    return (texts.get(lang, {}).get(key) or texts['ar'].get(key) or texts['en'].get(key) or key)


def rand_token(n=10):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(n))


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


def _common_opts(opts):
    if os.path.exists(COOKIES_FILE):
        opts['cookiefile'] = COOKIES_FILE
    if FFMPEG_LOCATION:
        opts['ffmpeg_location'] = FFMPEG_LOCATION
    return opts


def _video_format(height):
    return f'bv*[height<={height}]+ba/b[height<={height}]/bv*+ba/b/best'


def get_ydl_opts_video(output_template, height):
    return _common_opts({
        'format': _video_format(height),
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'retries': 3,
        'fragment_retries': 3,
        'socket_timeout': 15,
        'concurrent_fragment_downloads': 4,
        'http_headers': {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/124.0.0.0 Safari/537.36'),
            'Accept-Language': 'en-US,en;q=0.9',
        },
    })


def get_ydl_opts_audio(output_template):
    return _common_opts({
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'retries': 3,
        'fragment_retries': 3,
        'socket_timeout': 15,
        'http_headers': {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/124.0.0.0 Safari/537.36'),
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })


def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
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
    markup.row(InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
               InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
    markup.row(InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
               InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it"))
    markup.row(InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi"),
               InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn"))
    markup.row(InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"))
    return markup


def _report(chat_id, status_msg_id, text):
    try:
        if status_msg_id:
            bot.edit_message_text(text, chat_id, status_msg_id)
        else:
            bot.send_message(chat_id, text)
    except Exception:
        try:
            bot.send_message(chat_id, text)
        except Exception:
            pass


def _cleanup(prefix):
    for f in glob.glob(f'{prefix}*'):
        try:
            os.remove(f)
        except Exception:
            pass


def _find_output(prefix):
    cands = [c for c in glob.glob(f'{prefix}*') if not c.endswith(('.part', '.ytdl', '.temp'))]
    if not cands:
        return None
    mp4 = [c for c in cands if c.lower().endswith('.mp4')]
    pick = (mp4 or cands)
    pick.sort(key=lambda p: os.path.getsize(p) if os.path.exists(p) else 0, reverse=True)
    return pick[0]


def download_video(chat_id, url, lang, status_msg_id=None, reply_to=None):
    last_info = None
    got_file_but_too_big = False
    had_error = False

    for height in DOWNLOAD_HEIGHTS:
        token2 = rand_token()
        prefix = f'vid_{chat_id}_{token2}.'
        template = f'vid_{chat_id}_{token2}.%(ext)s'
        try:
            with yt_dlp.YoutubeDL(get_ydl_opts_video(template, height)) as ydl:
                info = ydl.extract_info(url, download=True)
                last_info = info

            out_file = _find_output(prefix)
            if not out_file or not os.path.exists(out_file):
                had_error = True
                _cleanup(prefix)
                continue

            size_mb = os.path.getsize(out_file) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                got_file_but_too_big = True
                _cleanup(prefix)
                continue

            likes = (last_info.get('like_count') or 0) if last_info else 0
            views = (last_info.get('view_count') or 0) if last_info else 0
            duration = ((last_info.get('duration_string') or fmt_duration(last_info.get('duration'))) if last_info else "0:00")

            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton(f"❤️ {likes:,}", callback_data="n"),
                InlineKeyboardButton(f"👁 {views:,}", callback_data="n"),
                InlineKeyboardButton(f"⏱ {duration}", callback_data="n")
            )
            markup.row(InlineKeyboardButton(texts[lang]['share'], url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}"))

            with open(out_file, 'rb') as f:
                bot.send_video(chat_id, f, caption=texts[lang]['success'],
                               reply_markup=markup, reply_to_message_id=reply_to,
                               timeout=300, supports_streaming=True)
            _cleanup(prefix)
            return True

        except Exception as e:
            had_error = True
            print(f"Video download error (h={height}) for {chat_id}: {e}")
            _cleanup(prefix)
            continue

    if got_file_but_too_big:
        _report(chat_id, status_msg_id, texts[lang]['too_large'])
    else:
        _report(chat_id, status_msg_id, texts[lang]['error'])
    return False


def download_audio(chat_id, url, lang):
    token2 = rand_token()
    prefix = f'aud_{chat_id}_{token2}.'
    template = f'aud_{chat_id}_{token2}.%(ext)s'
    ok = False
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts_audio(template)) as ydl:
            info = ydl.extract_info(url, download=True)

        out_file = f'aud_{chat_id}_{token2}.mp3'
        if not os.path.exists(out_file):
            alt = _find_output(prefix)
            if alt and alt.lower().endswith('.mp3'):
                out_file = alt

        if os.path.exists(out_file):
            size_mb = os.path.getsize(out_file) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                return False
            with open(out_file, 'rb') as f:
                bot.send_audio(
                    chat_id, f,
                    caption=texts[lang]['audio_cap'],
                    title=(info.get('title') or 'Audio'),
                    performer=BOT_USERNAME,
                    timeout=300
                )
            ok = True
    except Exception as e:
        print(f"Audio download error for {chat_id}: {e}")
    finally:
        _cleanup(prefix)
    return ok


# [🔥 إصلاح الخلل الخفي 🔥] الحفاظ على النطاق كما هو (.com أو .net) وإصلاح الـ @ المفقودة فقط
def clean_url(url):
    url = url.strip()
    
    if "threads.com" in url or "threads.net" in url:
        if "?" in url:
            url = url.split("?")[0]
            
        # إصلاح الـ @ المفقودة تلقائياً بناءً على النطاق الفعلي للشخص والكوكيز الخاصة به
        if "/post/" in url and "/@" not in url:
            url = url.replace(".com/", ".com/@").replace(".net/", ".net/@")
    else:
        if "?" in url:
            url = url.split("?")[0]
            
    return url


def do_download_link(message, url, lang):
    chat_id = message.chat.id
    if not check_sub(chat_id):
        bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
        return

    url = clean_url(url)
    try:
        status = bot.reply_to(message, texts[lang]['processing'])
        status_id = status.message_id
    except Exception:
        status_id = None

    download_video(chat_id, url, lang, status_id, reply_to=message.message_id)

    try:
        download_audio(chat_id, url, lang)
    except Exception as e:
        print(f"Auto-audio error for {chat_id}: {e}")

    try:
        if status_id:
            bot.delete_message(chat_id, status_id)
    except Exception:
        pass


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
    all_users = db_get_all_users()
    status = bot.reply_to(message, f"⏳ جاري الإرسال إلى {len(all_users)} مستخدم...")
    success = 0
    failed = 0
    for i, uid in enumerate(all_users):
        try:
            bot.send_message(uid, f"📢 رسالة من الإدارة:\n\n{broadcast_msg}")
            success += 1
        except Exception:
            failed += 1
        if (i + 1) % 25 == 0:
            time.sleep(1)
        else:
            time.sleep(0.05)
    try:
        bot.edit_message_text(f"✅ تم إرسال الإذاعة.\n\n📨 وصلت: {success}\n❌ فشلت: {failed}", chat_id, status.message_id)
    except Exception:
        bot.reply_to(message, f"✅ تم الإرسال إلى {success} مستخدم.")


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

    elif call.data == "n":
        bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: True)
def process_url(message):
    if not message.text:
        return
    chat_id = message.chat.id
    db_add_user(chat_id)
    lang = user_langs.get(chat_id, 'ar')
    text = message.text.strip()

    if text.startswith('/'):
        return

    if text.startswith("http"):
        download_executor.submit(do_download_link, message, text, lang)
    else:
        bot.reply_to(message, texts[lang]['invalid_link'])


def main():
    print("✅ البوت يعمل الآن...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    time.sleep(3)
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
        except Exception as e:
            msg = str(e)
            if "409" in msg or "Conflict" in msg:
                print("⚠️ تعارض 409: نسخة أخرى من البوت تعمل. انتظار 15 ثانية...")
                time.sleep(15)
            else:
                print(f"Polling crashed, restarting in 5s: {e}")
                time.sleep(5)


if __name__ == "__main__":
    main()
