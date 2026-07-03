# 🎮 Dream Memory Overlay - Production Ready

## ✅ يعمل فوراً - بدون إعداد تقريباً!

### 📋 المتطلبات

| المتطلب | الحالة | الرابط |
|---------|--------|--------|
| Python 3.8+ | يجب تثبيته | [تحميل Python](https://www.python.org/downloads/) |
| BlueStacks | اللعبة | متجر التطبيقات |
| Gemini API Key | مجاني | [أخذ مفتاح](https://aistudio.google.com/app/apikey) |

---

## 🚀 التشغيل الفوري

### الخطوة 1: تثبيت Python
1. اذهب إلى: https://www.python.org/downloads/
2. حمل وأثبت Python 3.10+
3. **مهم:** فعّل "Add Python to PATH"

### الخطوة 2: تشغيل
```powershell
# افتح PowerShell في مجلد المشروع
cd C:\DreamMemory

# تثبيت المكتبات
pip install mss pillow PyQt6 pywin32 requests

# التشغيل
python main.py
```

### أو ببساطة:
```powershell
# شغّل السكربت
START-NOW.bat
```

---

## 🔑 الحصول على مفتاح Gemini (مجاني)

1. اذهب إلى: https://aistudio.google.com/app/apikey
2. سجّل دخول بحساب Google
3. اضغط "Create API Key"
4. انسخ المفتاح

### إضافة المفتاح:
```powershell
# الطريقة 1: متغير البيئة
$env:GEMINI_API_KEY = "مفتاحك_هنا"
python main.py

# الطريقة 2: في السكربت
# عدّل START-NOW.bat وضع مفتاحك فيه
```

---

## 📱 بدون Gemini؟ استخدم Ollama!

```powershell
# 1. تحميل Ollama
# https://ollama.com/download

# 2. تحميل النموذج
ollama pull qwen2.5vl:3b

# 3. تشغيل
ollama serve

# 4. تشغيل التطبيق
python main.py
```

**Ollama أفضل!** - بدون حدود، بدون انتظار!

---

## 🎮 الأزرار

| الزر | الوظيفة |
|-----|---------|
| **F8** | إظهار/إخفاء Overlay |
| **F9** | تشغيل/إيقاف المراقبة |
| **F10** | تحليل يدوي |
| **ESC** | خروج |

---

## ⚙️ الإعدادات

في ملف `config.py`:

```python
# اختيار الذكاء الاصطناعي
VISION_BACKEND = "auto"  # تلقائي

# أو_force Ollama أو Gemini
# VISION_BACKEND = "ollama"
# VISION_BACKEND = "gemini"
```

---

## 🔧 حل المشاكل

### "Module not found"
```powershell
pip install mss pillow PyQt6 pywin32 requests
```

### "API key not valid"
- المفتاح غير صحيح أو انتهت صلاحيته
- خذ مفتاح جديد من: https://aistudio.google.com/app/apikey

### "Quota exceeded"
- Gemini له حد مجاني: 60 طلب/دقيقة
- انتظر ساعة أو استخدم Ollama (بدون حدود)

### BlueStacks غير مكتشف
- تأكد أن BlueStacks في وضع نافذة (Windowed)
- لا تستخدم ملء الشاشة

---

## 📂 الملفات

```
production_version/
├── main.py              # التطبيق الرئيسي
├── config.py            # الإعدادات
├── hybrid_analyzer.py   # محلل الذكاء الاصطناعي
├── overlay.py          # النافذة الشفافة
├── capture.py          # التقاط الشاشة
├── window_tracker.py   # اكتشاف BlueStacks
├── request_watcher.py # مراقبة الطلبات
├── START-NOW.bat      # التشغيل السريع
└── README.md           # هذا الملف
```

---

## ⚡ مقارنة السرعة

| الطريقة | السرعة | الحدود |
|---------|--------|--------|
| **Ollama (GPU)** | ⚡⚡⚡⚡⚡ | ❌ لا حدود |
| **Ollama (CPU)** | ⚡⚡⚡ | ❌ لا حدود |
| **Gemini** | ⚡⚡⚡ | ⚠️ 60/دقيقة |

---

## 🎯 كيف يعمل؟

```
BlueStacks (اللعبة)
       ↓
التقاط الشاشة
       ↓
استخراج الطلبات + المشهد
       ↓
إرسال للذكاء الاصطناعي
       ↓
تحديد مواقع الأشياء
       ↓
رسم الدوائر على Overlay
```

---

## ⚠️ ملاحظة مهمة

- هذا **Overlay** وليس **Bot**
- يعرض فقط أماكن الأشياء
- لا يضغط أو يتحرك تلقائياً
- آمن للاستخدام!

---

## 💡 نصائح

1. **للسرعة:** استخدم Ollama مع GPU
2. **للبساطة:** Gemini API
3. **للعب:** استخدم F9 لتشغيل المراقبة
4. **للتحكم:** F10 للتحليل اليدوي

---

صنع بـ ❤️ للمستخدمين العرب
