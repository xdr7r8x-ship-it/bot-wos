# 🎮 Dream Memory - Zero Setup Edition

## ⚡ Zero AI, Zero API, Zero Waiting!

هذا الإصدار يعمل **فوراً** بدون أي إعداد!

### ✅，不需要 API Key
### ✅，不需要 AI
### ✅，不需要等待

---

## 🚀 التشغيل الفوري

```powershell
# افتح PowerShell في هذا المجلد
pip install opencv-python pillow PyQt6 pywin32
START.bat
```

---

## 📱 كيف يعمل؟

يستخدم **Template Matching** و **Color Detection** بدلاً من AI:

```
✅ يكتشف الأشياء بالألوان (أحمر، أزرق، ذهبي...)
✅ يطابق القوالب (Templates)
✅ سريع جداً - 5+ مرات في الثانية
✅ بدون إنترنت
```

---

## 🎮 الأزرار

| الزر | الوظيفة |
|-----|---------|
| **F8** | إظهار/إخفاء Overlay |
| **F9** | تشغيل/إيقاف المسح |
| **ESC** | خروج |

---

## 📊 مقارنة السرعة

| الطريقة | السرعة | الإعداد | الحدود |
|---------|--------|---------|--------|
| **Zero Setup** | ⚡⚡⚡⚡⚡ | ❌ 0 ثانية | ❌ لا حدود |
| **Ollama** | ⚡⚡⚡⚡ | ⏱️ 5 دقائق | ❌ لا حدود |
| **Gemini** | ⚡⚡⚡ | ⚡⚡⚡ فوراً | ⚠️ 60/دقيقة |

---

## 🔧 التخصيص

### إضافة قوالب خاصة

أضف صور للعناصر التي تريد اكتشافها في مجلد `templates/`:

```
INSTANT_VERSION/
├── templates/
│   ├── gold.png      # صورة للذهب
│   ├── gem.png       # صورة للجوهرة
│   └── key.png       # صورة للمفتاح
```

---

## 📂 الملفات

```
INSTANT_VERSION/
├── main.py              # التطبيق
├── config.py            # الإعدادات
├── template_detector.py # محرك الاكتشاف
├── START.bat            # التشغيل
├── requirements.txt     # المكتبات
└── templates/           # قوالب مخصصة
    └── (أضف صورك هنا)
```

---

## ⚙️ الإعدادات

في `config.py`:

```python
DETECTION_MODE = "hybrid"  # hybrid, template, color

# Template
TEMPLATE_MATCH_THRESHOLD = 0.7  # دقة التطابق

# Color
COLOR_THRESHOLD = 50  # حساسية اللون

# Speed
SCAN_INTERVAL_MS = 200  # سرعة المسح
```

---

## 🎯 للأداء الأفضل

1. **للبحث السريع:**
   ```python
   DETECTION_MODE = "color"
   SCAN_INTERVAL_MS = 100
   ```

2. **للبحث الدقيق:**
   ```python
   DETECTION_MODE = "template"
   TEMPLATE_MATCH_THRESHOLD = 0.8
   ```

3. **للأفضل من keduanya:**
   ```python
   DETECTION_MODE = "hybrid"
   ```

---

## ⚠️ ملاحظة

- هذا **يكتشف بالألوان والقوالب**
- ليس ذكاء اصطناعي
- قد يحتاج تخصيص للأشياء المحددة في اللعبة

---

## 💡 نصائح

1. أضف قوالب مخصصة لأشياء اللعبة
2. استخدم `hybrid` للحصول على أفضل النتائج
3. اضبط `COLOR_THRESHOLD` إذا كان لا يكتشف

---

صنع بـ ❤️ - بدون AI!
