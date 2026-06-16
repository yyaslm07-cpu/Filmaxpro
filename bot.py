import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

BOT_TOKEN = "8688563134:AAHs6IP3l4Kbxx8FZx3XmOsSOpgGvjLMhA4"
bot = telebot.TeleBot(BOT_TOKEN)

BOT_USERNAME = "@VidGrabber2026_bot" 
CHANNEL_USERNAME = "@filmaxpro"
YOUTUBE_LINK = "https://youtube.com/@mosleh_2003?si=iRehojptx4LlM--6"
ADMIN_ID = 1000369751  # ⚠️ تم وضع الـ ID الخاص بك هنا لضمان عمل الإذاعة

user_langs = {}
users_db = set() 
user_urls = {} 

# القاموس الكامل لجميع اللغات بدون أي اختصار لضمان عدم حدوث أخطاء
texts = {
    'ar': {
        'welcome': f"⚖️┇أهلاً بك عزيزي، مع {BOT_USERNAME} يمكنك تحميل من عدة مواقع بصيغ متعددة والاستماع اليها في أي وقت،\n\n💠┇المنصات المدعومة:\n\n📥  يوتيوب         | 📥  انستكرام\n📥  فيسبوك       | 📥  تويتر\n📥  تيك توك       | 📥  سناب شات\n📥  ساوند كلاود  | 📥  بينترست\n📥  لايكي            | 📥  كواي\n📥  تيليجرام       | 📥  PMC Music\n📥  تمبلر            | 📥  ديلي موشن\n📥  فيميو           | 📥  ثريدز\n📥  فانيميت       | 📥  كاب كات\n\n- قم بإرسال رابط المنشور فقط 📥\nولا تنسى قم بمشاركه البوت لاصدقائك  📥",
        'usage': "💠┇طرق التحميل من البوت:\n\nسلّم البوت رابط المقطع مباشرة من أي منصة مدعومة، أو اكتب اسم الأغنية أو الفيديو باللغة العربية أو الإنجليزية وسيقوم البوت بالبحث والتحميل تلقائياً.",
        'force_sub': "عذراً عزيزي، يجب عليك الاشتراك في قنواتنا أولاً 👇",
        'sub_tg': "اشترك في قناة التلجرام 📢",
        'sub_yt': "اشترك في قناة اليوتيوب 📺",
        'usage_btn': "💡 طريقة استخدام البوت",
        'lang_btn': "🌐 تغيير لغة البوت",
        'choose_lang': "اختر لغتك المفضلة / Choose your language 👇",
        'select_format': "اختر الصيغة التي تود تحميلها للمقطع 👇",
        'processing': "جاري جلب البيانات ومعالجة المقطع... ⏳",
        'uploading': "جاري تحميل الملف ورفعه إلى تيليجرام... 📤",
        'success': f"تم تحميل المقطع بنجاح ✅\n{BOT_USERNAME}",
        'audio_cap': f"المقطع الصوتي 🎵\n{BOT_USERNAME}",
        'share': "مشاركة البوت 📤",
        'error': "حدث خطأ أثناء المعالجة، تأكد من أن الرابط عام وليس لحساب خاص.",
        'vid_option': "🎬 فيديو (Video)",
        'aud_option': "🎵 صوت (Audio)",
        'sub_option': "📝 ملف الترجمة (.srt)"
    },
    'en': {
        'welcome': f"⚖️┇Welcome! With {BOT_USERNAME} you can download from multiple platforms easily,\n\n- Just send the video link or search name 📥",
        'usage': "💠┇How to use:\nSend the video/audio link directly, or type the name of the song to search on YouTube.",
        'force_sub': "Sorry, you must subscribe to our channels first 👇",
        'sub_tg': "Subscribe to Telegram 📢",
        'sub_yt': "Subscribe to YouTube 📺",
        'usage_btn': "💡 How to use",
        'lang_btn': "🌐 Change Language",
        'choose_lang': "Choose your preferred language 👇",
        'select_format': "Choose your download format 👇",
        'processing': "Extracting data... ⏳",
        'uploading': "Downloading and uploading to Telegram... 📤",
        'success': f"Downloaded Successfully ✅\n{BOT_USERNAME}",
        'audio_cap': f"Audio Track 🎵\n{BOT_USERNAME}",
        'share': "Share Bot 📤",
        'error': "An error occurred. Make sure the link is public.",
        'vid_option': "🎬 Video",
        'aud_option': "🎵 Audio",
        'sub_option': "📝 Subtitles (.srt)"
    },
    'fr': {
        'welcome': f"⚖️┇Bienvenue! Avec {BOT_USERNAME} vous pouvez télécharger depuis plusieurs sites,\n\n- Envoyez simplement le lien 📥",
        'usage': "💠┇Comment utiliser:\nEnvoyez le lien de la vidéo ou écrivez le nom de la chanson.",
        'force_sub': "Désolé, vous devez d'abord vous abonner 👇",
        'sub_tg': "S'abonner à Telegram 📢",
        'sub_yt': "S'abonner à YouTube 📺",
        'usage_btn': "💡 Comment utiliser",
        'lang_btn': "🌐 Changer de langue",
        'choose_lang': "Choisissez votre langue 👇",
        'select_format': "Choisissez le format 👇",
        'processing': "Traitement en cours... ⏳",
        'uploading': "Téléchargement et envoi... 📤",
        'success': f"Téléchargé avec succès ✅\n{BOT_USERNAME}",
        'audio_cap': f"Piste audio 🎵\n{BOT_USERNAME}",
        'share': "Partager le Bot 📤",
        'error': "Une erreur est survenue.",
        'vid_option': "🎬 Vidéo",
        'aud_option': "🎵 Audio",
        'sub_option': "📝 Sous-titres (.srt)"
    },
    'it': {
        'welcome': f"⚖️┇Benvenuto! Con {BOT_USERNAME} puoi scaricare da molti siti,\n\n- Invia il link 📥",
        'usage': "💠┇Come usare:\nInvia il link del video o cerca per nome.",
        'force_sub': "Devi prima iscriverti ai nostri canali 👇",
        'sub_tg': "Iscriviti a Telegram 📢",
        'sub_yt': "Iscriviti a YouTube 📺",
        'usage_btn': "💡 Come usare",
        'lang_btn': "🌐 Cambia lingua",
        'choose_lang': "Scegli la tua lingua 👇",
        'select_format': "Scegli il formato 👇",
        'processing': "Elaborazione... ⏳",
        'uploading': "Caricamento in corso... 📤",
        'success': f"Scaricato con successo ✅\n{BOT_USERNAME}",
        'audio_cap': f"Traccia audio 🎵\n{BOT_USERNAME}",
        'share': "Condividi Bot 📤",
        'error': "Si è verificato un errore.",
        'vid_option': "🎬 Video",
        'aud_option': "🎵 Audio",
        'sub_option': "📝 Sottotitoli (.srt)"
    },
    'hi': {
        'welcome': f"⚖️┇स्वागत है! {BOT_USERNAME} के साथ आप कई साइटों से डाउनलोड कर सकते हैं।\n\n- बस लिंक भेजें 📥",
        'usage': "💠┇उपयोग कैसे करें:\nवीडियो का लिंक भेजें या गाने का नाम लिखकर खोजें।",
        'force_sub': "क्षма करें, आपको पहले हमारे चैनल की सदस्यता लेनी होगी 👇",
        'sub_tg': "टेलीग्राम से जुड़ें 📢",
        'sub_yt': "यूट्यूब से जुड़ें 📺",
        'usage_btn': "💡 उपयोग कैसे करें",
        'lang_btn': "🌐 भाषा बदलें",
        'choose_lang': "अपनी भाषा चुनें 👇",
        'select_format': "डाउनलोड प्रारूप चुनें 👇",
        'processing': "प्रसंस्करण जारी है... ⏳",
        'uploading': "डाउनलोड और अपलोड हो रहा है... 📤",
        'success': f"सफलतापूर्वक डाउनलोड किया गया ✅\n{BOT_USERNAME}",
        'audio_cap': f"ऑडियो ट्रैक 🎵\n{BOT_USERNAME}",
        'share': "बॉट साझा करें 📤",
        'error': "एक त्रुटि हुई। लिंक की जांच करें।",
        'vid_option': "🎬 वीडियो",
        'aud_option': "🎵 ऑडियो",
        'sub_option': "📝 उपशीर्षक (.srt)"
    },
    'bn': {
        'welcome': f"⚖️┇স্বাগতম! {BOT_USERNAME} এর মাধ্যমে আপনি অনেক সাইট থেকে ডাউনলোড করতে পারবেন।\n\n- শুধু লিংক পাঠান 📥",
        'usage': "💠┇কীভাবে ব্যবহার করবেন:\nভিডিও লিংক পাঠান অথবা গানের নাম লিখে অনুসন্ধান করুন।",
        'force_sub': "দুঃখিত, আপনাকে প্রথমে আমাদের চ্যানেলে সাবস্ক্রাইব করতে হবে 👇",
        'sub_tg': "টেলিগ্রামে সাবস্ক্রাইব করুন 📢",
        'sub_yt': "ইউটিউবে সাবস্ক্রাইব করুন 📺",
        'usage_btn': "💡 কীভাবে ব্যবহার করবেন",
        'lang_btn': "🌐 ভাষা পরিবর্তন করুন",
        'choose_lang': "আপনার ভাষা নির্বাচন করুন 👇",
        'select_format': "ডাউনলোড ফরম্যাট চয়ন করুন 👇",
        'processing': "প্রক্রিয়াকরণ করা হচ্ছে... ⏳",
        'uploading': "ডাউনলোড এবং আপলোড হচ্ছে... 📤",
        'success': f"সফলভাবে ডাউনলোড হয়েছে ✅\n{BOT_USERNAME}",
        'audio_cap': f"অডিও ট্র্যাক 🎵\n{BOT_USERNAME}",
        'share': "বট শেয়ার করুন 📤",
        'error': "একটি ত্রুটি ঘটেছে। লিংকটি পরীক্ষা করুন।",
        'vid_option': "🎬 ভিডিও",
        'aud_option': "🎵 অডিও",
        'sub_option': "📝 সাবটাইটেল (.srt)"
    },
    'ru': {
        'welcome': f"⚖️┇Добро пожаловать! С {BOT_USERNAME} вы можете скачивать с многих сайтов.\n\n- Просто отправьте ссылку 📥",
        'usage': "💠┇Как использовать:\nОтправьте ссылку на видео или напишите название для поиска.",
        'force_sub': "Извините, вы должны сначала подписаться на наши каналы 👇",
        'sub_tg': "Подписаться на Telegram 📢",
        'sub_yt': "Подписаться на YouTube 📺",
        'usage_btn': "💡 Как использовать",
        'lang_btn': "🌐 Изменить язык",
        'choose_lang': "Выберите ваш язык 👇",
        'select_format': "Выберите формат скачивания 👇",
        'processing': "Обработка данных... ⏳",
        'uploading': "Скачивание и отправка в Telegram... 📤",
        'success': f"Успешно скачано ✅\n{BOT_USERNAME}",
        'audio_cap': f"Аудиодорожка 🎵\n{BOT_USERNAME}",
        'share': "Поделиться ботом 📤",
        'error': "Произошла ошибка. Проверьте ссылку.",
        'vid_option': "🎬 Видео",
        'aud_option': "🎵 Аудио",
        'sub_option': "📝 Субтитры (.srt)"
    }
}

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

def lang_markup():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"), InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
    markup.row(InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"), InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it"))
    markup.row(InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi"), InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn"))
    markup.row(InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"))
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
                bot.reply_to(message, "اكتب الرسالة بعد الأمر هكذا: /cast رسالتكم")
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

    if not check_sub(chat_id):
        bot.reply_to(message, texts[lang]['force_sub'], reply_markup=subscription_markup(lang))
        return

    msg = bot.reply_to(message, texts[lang]['processing'])
    
    try:
        # نظام البحث الذكي وجلب الرابط الفعلي
        if not url.startswith("http"):
            search_opts = {'format': 'best', 'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{url}", download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    url = info['entries'][0]['webpage_url']
                else:
                    bot.edit_message_text(texts[lang]['error'], chat_id, msg.message_id)
                    return

        user_urls[chat_id] = url
        
        # عرض خيارات الصيغ المترجمة للمستند بالكامل
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton(texts[lang]['vid_option'], callback_data="dl_vid"), 
                   InlineKeyboardButton(texts[lang]['aud_option'], callback_data="dl_aud"))
        markup.row(InlineKeyboardButton(texts[lang]['sub_option'], callback_data="dl_sub"))
        
        bot.edit_message_text(texts[lang]['select_format'], chat_id, msg.message_id, reply_markup=markup)
        
    except Exception as e:
        bot.edit_message_text(texts[lang]['error'], chat_id, msg.message_id)

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
        user_langs[chat_id] = new_lang
        bot.answer_callback_query(call.id, "✅ Done", show_alert=False)
        bot.edit_message_text(texts[new_lang]['welcome'], chat_id, call.message.message_id, reply_markup=main_markup(new_lang))

    elif call.data.startswith("dl_"):
        url = user_urls.get(chat_id)
        if not url:
            bot.answer_callback_query(call.id, "Error: Request Expired", show_alert=True)
            return

        bot.edit_message_text(texts[lang]['uploading'], chat_id, call.message.message_id)
        
        try:
            # استخدام حفظ بـ ID المقطع لتجنب مشاكل تشفير أسماء الملفات على السيرفر
            if call.data == "dl_vid":
                ydl_opts = {'format': 'best', 'outtmpl': '%(id)s.%(ext)s', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    likes = info.get('like_count') or 0
                    views = info.get('view_count') or 0
                    duration = info.get('duration_string') or '0:00'

                    markup = InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton(f"❤️ {likes}", callback_data="n"), InlineKeyboardButton(f"👁 {views}", callback_data="n"), InlineKeyboardButton(f"⏱ {duration}", callback_data="n"))
                    markup.row(InlineKeyboardButton(texts[lang]['share'], url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}"))

                    with open(filename, 'rb') as f:
                        bot.send_video(chat_id, f, caption=texts[lang]['success'], reply_markup=markup)
                    if os.path.exists(filename): os.remove(filename)

            elif call.data == "dl_aud":
                ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(id)s.mp3', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    with open(filename, 'rb') as f:
                        bot.send_audio(chat_id, f, caption=texts[lang]['audio_cap'])
                    if os.path.exists(filename): os.remove(filename)

            elif call.data == "dl_sub":
                ydl_opts = {
                    'skip_download': True, 'writesubtitles': True, 'writeautomaticsub': True,
                    'subtitleslangs': ['ar', 'en'], 'subtitlesformat': 'srt',
                    'outtmpl': '%(id)s.%(ext)s', 'quiet': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(url, download=True)
                    sent = False
                    for file in os.listdir():
                        if file.endswith('.srt') or file.endswith('.vtt'):
                            with open(file, 'rb') as f:
                                bot.send_document(chat_id, f, caption="Subtitles File 📝")
                            os.remove(file)
                            sent = True
                    if not sent: 
                        bot.send_message(chat_id, "No subtitles found ❌")

            bot.delete_message(chat_id, call.message.message_id)

        except Exception as e:
            bot.edit_message_text(texts[lang]['error'], chat_id, call.message.message_id)

print("البوت الاحترافي الشامل يعمل الآن بكل قوته...")
bot.infinity_polling()
