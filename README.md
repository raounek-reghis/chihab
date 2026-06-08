# 🎌 بوت الأنمي والأفلام — نسخة Koyeb (مجانية 100%)

---

## ✅ ما تحتاجه
- حساب GitHub: https://github.com
- حساب Koyeb: https://koyeb.com
- توكن بوت تيليغرام (من @BotFather)
- مفتاح Gemini (من https://aistudio.google.com)

---

## 🚀 خطوات الرفع

### 1️⃣ ارفع الملفات على GitHub
1. اذهب إلى https://github.com وسجل دخول
2. اضغط New repository → سمّه anime-bot → Create repository
3. اضغط "uploading an existing file"
4. ارفع الملفين فقط: bot.py و requirements.txt
5. اضغط Commit changes

### 2️⃣ أنشئ حساب Koyeb
1. اذهب إلى https://koyeb.com
2. اضغط Get Started → سجل بحساب GitHub مباشرة

### 3️⃣ أنشئ مشروع جديد
1. اضغط Create App
2. اختر GitHub
3. اختر الـ repo اسمه anime-bot
4. في خانة Run command اكتب:
   python bot.py
5. في خانة Port اكتب: 8000

### 4️⃣ أضف المتغيرات السرية
قبل الضغط Deploy، اضغط Add Variable وأضف:

   TELEGRAM_TOKEN    = توكن البوت من BotFather
   GEMINI_API_KEY    = مفتاح Gemini من aistudio.google.com
   ALLOWED_USER_ID   = ID أخيك (يرسل /myid للبوت)

5. اضغط Deploy ✅

---

## 🎮 أوامر البوت
- /start  — القائمة الرئيسية
- /myid   — معرفة الـ ID الخاص بك
- /help   — المساعدة
- /clear  — مسح المحادثة

---

## 📢 تعديل الإعلانات
افتح bot.py وابحث عن قسم ADS وغيّر رابط قناتك:
   "button_url": "https://t.me/اسم_قناتك"

وغيّر كل كم رد يظهر الإعلان:
   AD_EVERY_N_REPLIES = 5
