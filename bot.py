import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

BOT_TOKEN = "8688563134:AAHs6IP3l4Kbxx8FZx3XmOsSOpgGvjLMhA4"
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL_USERNAME = "@filmaxpro"
YOUTUBE_LINK = "https://youtube.com/@mosleh_2003?si=iRehojptx4LlM--6"

# رسالة الترحيب الاحترافية الخاصة بك
welcome_message = """📤┇أهلاً بك عزيزي، مع @bbt1bot يمكنك تحميل من عدة مواقع بصيغ متعددة والاستماع اليها في أي وقت،

📤┇المنصات المدعومة:

📤  يوتيوب         | 📤  انستكرام
📤  فيسبوك       | 📤  تويتر
📤  تيك توك       | 📤  سناب شات
📤  ساوند كلاود  | 📤  بينترست
📤  لايكي            | 📤  كواي
📤  تيليجرام       | 📤  PMC Music
📤  تمبلر            | 📤  ديلي موشن
📤  فيميو           | 📤  ثريدز
📤  فانيميت       | 📤  كاب كات

- قم بإرسال رابط المنشور فقط 📤
ولا تنسى قم بمشاركه البوت لاصدقائك  📤"""

# إعدادات متقدمة لتخطي حماية المنصات
ydl_opts = {
    'format': 'best',
    'quiet': True,
    'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
}

# التحقق من الاشتراك
def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return True

# أزرار الاشتراك الإجباري (تلجرام + يوتيوب)
def subscription_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    btn1 = InlineKeyboardButton("اشترك في قناة التلجرام 📢", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    btn2 = InlineKeyboardButton("اشترك في قناة اليوتيوب 📺", url=YOUTUBE_LINK)
    markup.add(btn1, btn2)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    if not check_sub(message.from_user.id):
        bot.reply_to(message, "عذراً عزيزي، يجب عليك الاشتراك في قنواتنا أولاً 👇", reply_markup=subscription_markup())
        return
    bot.reply_to(message, welcome_message)

@bot.message_handler(func=lambda message: True)
def process(message):
    url = message.text
    if not url.startswith("http"): return
    
    if not check_sub(message.from_user.id):
        bot.reply_to(message, "عذراً عزيزي، يجب عليك الاشتراك في قنواتنا أولاً 👇", reply_markup=subscription_markup())
        return

    msg = bot.reply_to(message, "جاري معالجة الفيديو واستخراج الإحصائيات... ⏳")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # جلب الإحصائيات
            likes = info.get('like_count', 0)
            views = info.get('view_count', 0)
            duration = info.get('duration_string', '0:00')

            # الأزرار الشفافة الاحترافية
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton(f"❤️ {likes}", callback_data="none"),
                InlineKeyboardButton(f"👁 {views}", callback_data="none"),
                InlineKeyboardButton(f"⏱ {duration}", callback_data="none")
            )
            markup.row(
                InlineKeyboardButton("مشاركة البوت 📤", url="https://t.me/share/url?url=https://t.me/bbt1bot")
            )

            # إرسال الفيديو
            with open(filename, 'rb') as f:
                bot.send_video(message.chat.id, f, caption="تم تحميل المقطع بنجاح ✅\n@bbt1bot", reply_markup=markup)
            
            # تحميل الصوت
            audio_name = filename.rsplit('.', 1)[0] + ".mp3"
            with yt_dlp.YoutubeDL({'format': 'bestaudio/best', 'outtmpl': audio_name}) as ydl_a:
                ydl_a.download([url])
            
            # إرسال الصوت
            with open(audio_name, 'rb') as f:
                bot.send_audio(message.chat.id, f, caption="المقطع الصوتي 🎵\n@bbt1bot")
            
            bot.delete_message(message.chat.id, msg.message_id)
            if os.path.exists(filename): os.remove(filename)
            if os.path.exists(audio_name): os.remove(audio_name)
            
    except Exception as e:
        bot.edit_message_text("حدث خطأ في جلب الإحصائيات أو التحميل. تأكد من أن الرابط ليس لحساب خاص.", message.chat.id, msg.message_id)

print("البوت جاهز بجميع الميزات...")
bot.infinity_polling()

