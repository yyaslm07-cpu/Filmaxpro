import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import yt_dlp
import os

# ✅ إصلاح 1: استخدم متغيرات بيئة بدل كتابة التوكن مباشرة
# في الخادم نفذ: export BOT_TOKEN="توكنك"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ضع_توكنك_هنا")
bot = telebot.TeleBot(BOT_TOKEN)

BOT_USERNAME = "@VidGrabber2026_bot"
CHANNEL_USERNAME = "@filmaxpro"
YOUTUBE_LINK = "https://youtube.com/@mosleh_2003?si=iRehojptx4LlM--6"
ADMIN_ID = 1000369751

# ✅ الحد الأقصى لحجم الملف (50MB = حد تيليجرام)
MAX_FILE_SIZE_MB = 50

user_langs = {}
users_db = set()

bot.set_my_commands([
    BotCommand("start", "بدء الان"),
    BotCommand("admin", "الادمن فقط")
])

texts = {
    'ar': {
        'welcome': f"⚖️┇أهلاً بك عزيزي، مع {BOT_USERNAME} يمكنك تحميل من عدة مواقع بصيغ متعددة والاستماع اليها في أي وقت،\n\n💠┇المنصات المدعومة:\n\n📥  يوتيوب         | 📥  انستكرام\n📥  فيسبوك       | 📥  تويتر/X\n📥  تيك توك       | 📥  سناب شات\n📥  ساوند كلاود  | 📥  بينترست\n📥  لايكي            | 📥  كواي\n📥  تيليجرام       | 📥  PMC Music\n📥  تمبلر            | 📥  ديلي موشن\n📥  فيميو           | 📥  ثريدز\n📥  فانيميت       | 📥  كاب كات\n\n- قم بإرسال رابط المنشور فقط 📥\nولا تنسى قم بمشاركه البوت لاصدقائك  📥",
        'usage': "💠┇طرق التحميل من البوت:\n\nأرسل رابط المقطع مباشرة من أي منصة مدعومة وسيقوم البوت بالتحميل تلقائياً.",
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
        'too_large': f"❌ حجم الملف أكبر من {MAX_FILE_SIZE_MB}MB، لا يمكن إرساله عبر تيليجرام."
    },
    'en': {
        'welcome': f"⚖️┇Welcome! With {BOT_USERNAME} you can download from multiple platforms easily,\n\n- Just send the video link 📥",
        'usage': "💠┇How to use:\nSend the video/audio link directly.",
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
        'too_large': f"❌ File size exceeds {MAX_FILE_SIZE_MB}MB, cannot send via Telegram."
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

# ✅ إصلاح 4: فصل /cast عن /admin لمعالجة أفضل للنص الإضافي
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    users_db.add(chat_id)
    lang = user_langs.get(chat_id, 'ar')
    if not check_sub(chat_id):
        bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
        return
    bot.reply_to(message, texts[lang]['welcome'], reply_markup=main_markup(lang))

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    chat_id = message.chat.id
    if chat_id == ADMIN_ID:
        bot.reply_to(message, "مرحباً بك يا مدير البوت 👑\nلإرسال إذاعة لجميع المستخدمين، اكتب:\n/cast رسالتكم")
    else:
        bot.reply_to(message, "عذراً، هذا الأمر مخصص لإدارة البوت فقط ❌")

@bot.message_handler(commands=['cast'])
def handle_cast(message):
    chat_id = message.chat.id
    if chat_id != ADMIN_ID:
        return
    # ✅ إصلاح 5: استخراج النص بعد /cast بشكل صحيح
    parts = message.text.split(None, 1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(message, "اكتب الرسالة بعد الأمر هكذا:\n/cast رسالتكم")
        return
    broadcast_msg = parts[1].strip()
    success = 0
    for uid in users_db.copy():
        try:
            bot.send_message(uid, f"📢 رسالة من الإدارة:\n\n{broadcast_msg}")
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ تم إرسال الإذاعة إلى {success} مستخدم.")

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
        # زر معلوماتي فقط، لا يفعل شيئاً
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def process_url(message):
    chat_id = message.chat.id
    users_db.add(chat_id)
    lang = user_langs.get(chat_id, 'ar')
    url = message.text.strip()

    if not url.startswith("http"):
        bot.reply_to(message, texts[lang]['invalid_link'])
        return

    if not check_sub(chat_id):
        bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
        return

    msg = bot.reply_to(message, texts[lang]['processing'])
    vid_file = None
    aud_file = None

    try:
        # ── تحميل الفيديو ──
        vid_template = f'vid_{chat_id}.%(ext)s'
        with yt_dlp.YoutubeDL(get_ydl_opts_video(vid_template)) as ydl:
            info = ydl.extract_info(url, download=True)
            vid_file = ydl.prepare_filename(info)

            # ✅ إصلاح 6: التحقق من حجم الملف قبل الإرسال
            if os.path.exists(vid_file):
                file_size_mb = os.path.getsize(vid_file) / (1024 * 1024)
                if file_size_mb > MAX_FILE_SIZE_MB:
                    bot.edit_message_text(texts[lang]['too_large'], chat_id, msg.message_id)
                    os.remove(vid_file)
                    return

            likes = info.get('like_count') or 0
            views = info.get('view_count') or 0
            duration = info.get('duration_string') or '0:00'

            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton(f"❤️ {likes:,}", callback_data="n"),
                InlineKeyboardButton(f"👁 {views:,}", callback_data="n"),
                InlineKeyboardButton(f"⏱ {duration}", callback_data="n")
            )
            markup.row(InlineKeyboardButton(texts[lang]['share'], url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}"))

            with open(vid_file, 'rb') as f:
                bot.send_video(chat_id, f, caption=texts[lang]['success'], reply_markup=markup, reply_to_message_id=message.message_id)

        # ── تحميل الصوت بصيغة mp3 ──
        aud_template = f'aud_{chat_id}.%(ext)s'
        with yt_dlp.YoutubeDL(get_ydl_opts_audio(aud_template)) as ydl:
            info_a = ydl.extract_info(url, download=True)
            # ✅ إصلاح 7: الملف بعد postprocessor يكون .mp3 دائماً
            aud_file = f'aud_{chat_id}.mp3'
            if os.path.exists(aud_file):
                with open(aud_file, 'rb') as f:
                    bot.send_audio(
                        chat_id, f,
                        caption=texts[lang]['audio_cap'],
                        title=info_a.get('title', 'Audio'),
                        performer=BOT_USERNAME
                    )

        # ✅ إصلاح 8: حذف رسالة التحميل بأمان
        try:
            bot.delete_message(chat_id, msg.message_id)
        except:
            pass

    except Exception as e:
        print(f"Error for {chat_id}: {e}")
        # ✅ إصلاح 9: معالجة الخطأ بأمان دون crash
        try:
            bot.edit_message_text(texts[lang]['error'], chat_id, msg.message_id)
        except:
            bot.send_message(chat_id, texts[lang]['error'])

    finally:
        # ✅ إصلاح 10: حذف الملفات المؤقتة دائماً حتى عند الخطأ
        for f in [vid_file, aud_file]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

print("✅ البوت يعمل الآن...")
bot.infinity_polling()
