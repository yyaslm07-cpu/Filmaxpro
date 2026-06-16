import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

BOT_TOKEN = "8688563134:AAHs6IP3l4Kbxx8FZx3XmOsSOpgGvjLMhA4"
bot = telebot.TeleBot(BOT_TOKEN)

BOT_USERNAME = "@VidGrabber2026_bot" 
CHANNEL_USERNAME = "@filmaxpro"
YOUTUBE_LINK = "https://youtube.com/@mosleh_2003?si=iRehojptx4LlM--6"

# رسالة الترحيب وفيها معرف البوت
welcome_message = f"""
⚖️┇أهلاً بك عزيزي، مع {BOT_USERNAME} يمكنك تحميل من عدة مواقع بصيغ متعددة والاستماع اليها في أي وقت،

💠┇المنصات المدعومة:

📥  يوتيوب         | 📥  انستكرام
📥  فيسبوك       | 📥  تويتر
📥  تيك توك       | 📥  سناب شات
📥  ساوند كلاود  | 📥  بينترست
📥  لايكي            | 📥  كواي
📥  تيليجرام       | 📥  PMC Music
📥  تمبلر            | 📥  ديلي موشن
📥  فيميو           | 📥  ثريدز
📥  فانيميت       | 📥  كاب كات

- قم بإرسال رابط المنشور فقط 📥
ولا تنسى قم بمشاركه البوت لاصدقائك  📥
"""

# رسالة طريقة الاستخدام (مخفية وتظهر عند الضغط على الزر فقط)
usage_message = f"""
💠┇طرق التحميل من اليوتيوب:
🏷┇من خلال أرسال لي رابط الأغنية من اليوتيوب،
🖇┇أو أرسال لي أسم الأغنية للبحث عنها في اليوتيوب.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من الانستكرام:
🏷┇قم بأرسال لي رابط الفيديو أو الصورة في الانستكرام،
🖇┇أو يمكنك تحميل ستوريات أي شخص فقط عبر أرسال لي اليوزر الخاص به.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من الفيسبوك:
🏷┇يمكنك تحميل مقاطع الفيديو العامة من موقع الفيسبوك،
🖇┇عن طريق أرسال رابط الفيديو فقط.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من بينترست:
🏷┇يمكنك تحميل مقاطع الفيديو العامة من موقع بينترست،
🖇┇عن طريق أرسال رابط الفيديو فقط.
🖇┇يمكنك تحميل الصور بحث الاسم صوره
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من لايكي:
🏷┇يمكنك تحميل مقاطع الفيديو العامة من موقع لايكي،
🖇┇عن طريق أرسال رابط الفيديو فقط.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من التويتر:
🏷┇يمكنك تحميل مقاطع الفيديو العامة من موقع تويتر،
🖇┇عن طريق أرسال رابط الفيديو فقط.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من التيك توك:
🏷┇يمكنك تحميل مقاطع الفيديو العامة من موقع التيك توك،
🖇┇عن طريق أرسال رابط الفيديو فقط.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من السناب جات:
🏷┇يمكنك تحميل الستوريات العامة من موقع سناب جات،
🖇┇عن طريق أرسال رابط الحساب فقط.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من تيليجرام:
🏷┇يمكنك تحميل الستوريات العامة من موقع تيليجرام،
🖇┇عن طريق أرسال رابط الستوري فقط.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من ساوند كلاود:
🏷┇يمكنك تحميل الأغاني العامة من موقع ساوند كلاود،
🖇┇عن طريق أرسال رابط الأغنية فقط.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من ديلي موشن:
🏷┇يمكنك تحميل الفيديوات العامة من موقع ديلي موشن،
🖇┇عن طريق أرسال رابط الفيديو فقط.
┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
💠┇طرق التحميل من فيميو:
🏷┇يمكنك تحميل الفيديوات العامة من موقع فيميو،
🖇┇عن طريق أرسال رابط الفيديو فقط.
"""

ydl_opts = {
    'format': 'best',
    'quiet': True,
    'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/119.0.0.0'}
}

def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return True

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
    
    # الأزرار السفلية لرسالة الترحيب
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    btn1 = InlineKeyboardButton("💡 طريقة استخدام البوت", callback_data="show_usage")
    btn2 = InlineKeyboardButton("🇮🇶 تغيير لغة البوت", callback_data="change_language")
    markup.add(btn1, btn2)
    
    bot.reply_to(message, welcome_message, reply_markup=markup)

# الاستجابة عند الضغط على الأزرار السفلية
@bot.callback_query_handler(func=lambda call: call.data in ["show_usage", "change_language"])
def callback_inline(call):
    if call.data == "show_usage":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, usage_message)
    elif call.data == "change_language":
        # رسالة تظهر كإشعار منبثق عند محاولة تغيير اللغة
        bot.answer_callback_query(call.id, "سيتم إضافة ميزة تغيير اللغة قريباً ⏳", show_alert=True)

@bot.message_handler(func=lambda message: True)
def process(message):
    url = message.text
    if not url.startswith("http"): url = f"ytsearch1:{url}"
    
    if not check_sub(message.from_user.id):
        bot.reply_to(message, "عذراً عزيزي، يجب عليك الاشتراك في قنواتنا أولاً 👇", reply_markup=subscription_markup())
        return

    msg = bot.reply_to(message, "جاري المعالجة... ⏳")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info: info = info['entries'][0]
            filename = ydl.prepare_filename(info)
            
            likes = info.get('like_count') or 0
            views = info.get('view_count') or 0
            duration = info.get('duration_string') or '0:00'

            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton(f"❤️ {likes}", callback_data="none"), 
                InlineKeyboardButton(f"👁 {views}", callback_data="none"), 
                InlineKeyboardButton(f"⏱ {duration}", callback_data="none")
            )
            # زر المشاركة يحتوي على رابط بوتك
            markup.row(InlineKeyboardButton("مشاركة البوت 📤", url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}"))

            with open(filename, 'rb') as f:
                bot.send_video(message.chat.id, f, caption=f"تم تحميل المقطع بنجاح ✅\n{BOT_USERNAME}", reply_markup=markup)
            
            audio_name = filename.rsplit('.', 1)[0] + ".mp3"
            with yt_dlp.YoutubeDL({'format': 'bestaudio/best', 'outtmpl': audio_name}) as ydl_a: ydl_a.download([url])
            with open(audio_name, 'rb') as f:
                bot.send_audio(message.chat.id, f, caption=f"المقطع الصوتي 🎵\n{BOT_USERNAME}")
            
            bot.delete_message(message.chat.id, msg.message_id)
            if os.path.exists(filename): os.remove(filename)
            if os.path.exists(audio_name): os.remove(audio_name)
    except Exception as e:
        bot.edit_message_text("حدث خطأ، تأكد من صحة الرابط.", message.chat.id, msg.message_id)

print("البوت جاهز بجميع الميزات...")
bot.infinity_polling()
