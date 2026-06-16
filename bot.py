import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

BOT_TOKEN = "8688563134:AAHs6IP3l4Kbxx8FZx3XmOsSOpgGvjLMhA4"
bot = telebot.TeleBot(BOT_TOKEN)

# معرف البوت الخاص بك
BOT_USERNAME = "@VidGrabber2026_bot" 
CHANNEL_USERNAME = "@filmaxpro"
YOUTUBE_LINK = "https://youtube.com/@mosleh_2003?si=iRehojptx4LlM--6"

# رسالة الترحيب
welcome_message = f"""📤┇أهلاً بك عزيزي، مع {BOT_USERNAME} يمكنك تحميل من عدة مواقع بصيغ متعددة والاستماع اليها في أي وقت،

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

# رسالة طريقة الاستخدام التي أضفتها أنت
usage_message = """طريقة استخدام البوت 💡:

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
🖇┇عن طريق أرسال رابط الفيديو فقط."""

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

# أزرار الاشتراك الإجباري
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
    
    # إضافة زر "طريقة الاستخدام" تحت رسالة الترحيب
    markup = InlineKeyboardMarkup()
    btn_usage = InlineKeyboardButton("طريقة استخدام البوت 💡", callback_data="show_usage")
    markup.add(btn_usage)
    
    bot.reply_to(message, welcome_message, reply_markup=markup)

# دالة للاستجابة عند الضغط على زر "طريقة الاستخدام"
@bot.callback_query_handler(func=lambda call: call.data == "show_usage")
def callback_usage(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, usage_message)

@bot.message_handler(func=lambda message: True)
def process(message):
    url = message.text
    
    # إذا كان النص ليس رابطاً، سيقوم البوت بالبحث عنه كأغنية في يوتيوب (ميزة جديدة!)
    if not url.startswith("http"): 
        url = f"ytsearch1:{url}"
    
    if not check_sub(message.from_user.id):
        bot.reply_to(message, "عذراً عزيزي، يجب عليك الاشتراك في قنواتنا أولاً 👇", reply_markup=subscription_markup())
        return

    msg = bot.reply_to(message, "جاري معالجة طلبك واستخراج الإحصائيات... ⏳")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # إذا كان بحثاً عن طريق الاسم، نحتاج لأخذ أول نتيجة
            if 'entries' in info:
                info = info['entries'][0]
                
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
                InlineKeyboardButton("مشاركة البوت 📤", url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME[1:]}")
            )

            # إرسال الفيديو باسم بوتك
            with open(filename, 'rb') as f:
                bot.send_video(message.chat.id, f, caption=f"تم التحميل بنجاح ✅\n{BOT_USERNAME}", reply_markup=markup)
            
            # تحميل الصوت
            audio_name = filename.rsplit('.', 1)[0] + ".mp3"
            with yt_dlp.YoutubeDL({'format': 'bestaudio/best', 'outtmpl': audio_name}) as ydl_a:
                ydl_a.download([url])
            
            # إرسال الصوت باسم بوتك
            with open(audio_name, 'rb') as f:
                bot.send_audio(message.chat.id, f, caption=f"المقطع الصوتي 🎵\n{BOT_USERNAME}")
            
            bot.delete_message(message.chat.id, msg.message_id)
            if os.path.exists(filename): os.remove(filename)
            if os.path.exists(audio_name): os.remove(audio_name)
            
    except Exception as e:
        bot.edit_message_text("حدث خطأ في جلب الإحصائيات أو التحميل. تأكد من صحة الرابط أو أن الحساب ليس خاصاً.", message.chat.id, msg.message_id)

print("البوت جاهز بجميع الميزات...")
bot.infinity_polling()
