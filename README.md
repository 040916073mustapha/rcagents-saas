# Royal Chaussures Server 👑👠

**AI Customer Support Bot** لمتجر **Royal Chaussures** — أحذية وإكسسوارات نسائية فاخرة في تلمسان، الجزائر.

## 🏷️ النسخة المستقرة الحالية

**Tag:** `v2.4-dm-stable` 🏆  
**Commit:** `6314b8e`  
**النموذج:** `DeepSeek-V4-Flash` (عبر DeepInfra، Fallback: `Meta-Llama-3.1-70B`)

## ✅ الميزات

- 🤖 **AI Vision** — قراءة صور الأحذية مع الأسعار والألوان والتفاصيل بدقة
- 💬 **ردود ذكية** — بالعربية والدارجة والفرنسية
- 📱 **دعم المنصات:** Facebook Messenger · Instagram · WhatsApp
- 🛍️ **Shopify متكامل** — استعلام عن المنتجات، المخزون، الطلبات
- 🚚 **ZR Express** — متابعة الشحن عبر 58 ولاية
- 📊 **Dashboard** — لوحة تحكم للإدارة (طلبات، منتجات، عملاء)
- 🧪 **Logging كامل** — تشخيص كل طلب AI مع الـ Response/Status Code
- 🔐 **HMAC-SHA256** — التحقق من صحة Meta Webhook Payloads
- 🔇 **Deduplication** — منع الردود المكررة (بـ message.mid / wamid)
- 🛡️ **Echo Filter** — تجاهل رسائل البوت الذاتية (is_echo)
- ⏱️ **Auto-fallback Model** — إذا فشل DeepSeek-V4-Flash (60s) → Meta-Llama-3.1-70B (45s) → Fallback text

## 🏗️ المعمارية — DM System Architecture

```
┌─────────────────────────────────────┐
│ Meta Webhook POST                   │
│ app.py → /webhook                   │
├─────────────────────────────────────┤
│ 1. HMAC-SHA256 Verification 🔐      │
│ 2. object detection (page/ig/wa)    │
│ 3. _get_store_id_from_entry()       │
│    └─ Fallback → store_id="1"       │
│ 4. _process_messaging_multi()       │
│    ├─ 🔇 is_echo? → SKIP [ECHO]     │
│    ├─ 🔇 duplicate mid? → SKIP      │
│    │   [DEDUP]                      │
│    └─ ✅ New msg → Thread + AI      │
├─────────────────────────────────────┤
│ AIEngine.send_request()             │
│  ├─ 1st: DeepSeek-V4-Flash (60s)    │
│  └─ 2nd: Meta-Llama-3.1-70B (45s)  │
│  └─ ❌ All fail → Fallback text      │
├─────────────────────────────────────┤
│ _send_ig_reply_ai()                 │
│  ├─ POST /me/messages (Page Token)  │
│  ├─ Logs Response 200 ✅            │
│  └─ Logs Error 4XX ❌               │
└─────────────────────────────────────┘
```

## ⚙️ متغيرات البيئة (Render)

| المتغير | الوصف |
|---|---|
| `AI_MODEL` | نموذج AI الأساسي |
| `AI_API_URL` | DeepInfra endpoint: `https://api.deepinfra.com/v1/openai/chat/completions` |
| `AI_API_KEY` | مفتاح DeepInfra API |
| `AI_SYSTEM_PROMPT` | System Prompt (أولوية على النص الثابت) |
| `SHOPIFY_CATALOG_TOKEN` | Token قراءة المنتجات والمخزون |
| `SHOPIFY_ORDERS_TOKEN` | Token إدارة الطلبات |
| `FB_PAGE_ACCESS_TOKEN` | **Token صفحة فيسبوك (هام للإرسال)** |
| `FB_VERIFY_TOKEN` | Token التحقق من Webhook |
| `WHATSAPP_ACCESS_TOKEN` | Token واتساب API |
| `FACEBOOK_APP_SECRET` | **مطلوب لـ HMAC-SHA256** |
| `DATABASE_URL` | PostgreSQL (Neon) / SQLite للمحلي |

## 🔧 التطوير

### تجربة نموذج AI جديد
1. غيّر `AI_MODEL` في Render Environment Variables فقط
2. تأكد من الـ Logs: `[AI]` يطبع Status و Response
3. إذا تعطل → `git reset --hard 6314b8e` والعودة لـ v2.4-dm-stable

### إضافة منصة جديدة
- أضف دالة `process_xxx_entries` مماثلة لـ `process_whatsapp_entries`
- أضف endpoint في Flask (`/xxx/webhook`)
- أضف دالة إرسال مماثلة لـ `send_whatsapp_reply`
- **لا تنسى إضافة Dedup + Echo Filter للقناة الجديدة**

## 📜 ملفات مهمة

- `server.py` — السيرفر الرئيسي (بوت + ويبهوك + Dashboard)
- `webhook_server.py` — ويبهوك Shopify
- `render_deploy/` — إعدادات Render

## 🔒 الأمان

- الكود لا يلمس دوال Webhook الأساسية
- قاعدة Payload الصحيح: `isinstance(image_url, str) and image_url.strip()`
- لا فلاتر thinking/regex
- Logging كامل لكل طلب API
- HMAC-SHA256 للتحقق من Meta Webhooks

---

## 📋 DM System — قائمة الفحص الوقائي (Checklist)

### ✅ قبل ربط قناة جديدة (Messenger / Instagram / WhatsApp / Telegram)

- [ ] **1. Meta App Review Status** — تأكد أن التطبيق لديه الـ Permissions المطلوبة (`pages_messaging`, `instagram_basic`, `instagram_manage_messages`, `whatsapp_business_messaging`)
- [ ] **2. Webhook URL** — `https://<domain>/webhook` يستقبل POST من Meta
- [ ] **3. Verify Token** — مطابق في Meta Developers Dashboard و `FB_VERIFY_TOKEN` في Render
- [ ] **4. Page Access Token صالح** — ليس منتهي الصلاحية (صلاحية 60 يوماً للـ Long-lived Token). استخدم `get_fb_page_token()` لتجديده تلقائياً

### 🛡️ الحماية من الـ Webhook Pitfalls

- [ ] **5. HMAC-SHA256 قديم/مفقود** — تأكد أن `FACEBOOK_APP_SECRET` مضبوط في Render. إذا الـ verification معطل (`SIGNATURE_VERIFICATION=DISABLED` للاختبار)، **لا تنشر للإنتاج بدونه**
- [ ] **6. Echo Filter** — تأكد من `is_echo` check في بداية `_process_messaging_multi()`: إذا `True` → تجاهل فوراً. هذا يمنع البوت من الرد على نفسه
- [ ] **7. Deduplication** — تأكد أن `__processed_mids` قائمة نشطة. تحقق من `[DEDUP]` في Logs عند إرسال نفس الرسالة مرتين
- [ ] **8. Sender ID ≠ Business ID** — في Instagram DM، `recipient.id` يجب أن يكون **رقم الزبون** (`sender.id`) وليس `IG_BUSINESS_ID`. استخدم `/me/messages` مع **Page Access Token** وليس `/{ig_id}/messages`

### 🤖 AI & Fallback

- [ ] **9. AI Timeout** — `timeout=60` للـ Primary model، `timeout=45` للـ Fallback. إذا انتهت المهلة → Fallback تلقائي
- [ ] **10. Fallback Model** — DeepSeek-V4-Flash يفشل؟ جرب `Meta-Llama-3.1-70B-Instruct-Turbo`. إذا فشلا معاً → أرسل رسالة Fallback مُعدة مسبقاً
- [ ] **11. Image URL validity** — تأكد من: `isinstance(image_url, str) and image_url.strip()` قبل بناء الـ vision payload
- [ ] **12. Logging كامل** — `[AI] Sending to ...`, `[AI] Response ...`, `[META] Sending to ...`, `[META] Response ...` — كل خطوة مسجلة

### 🔄 Deployment

- [ ] **13. Manual Deploy** — بعد كل Commit مهم، اذهب إلى **Render Dashboard → Manual Deploy → Deploy latest commit**
- [ ] **14. تحقق من Logs** — افتح Render Logs بعد الـ Deploy: لا `[CRITICAL]`, لا 500, لا `[DEDUP]` للرسالة الأولى
- [ ] **15. Git Tag للنسخ المستقرة** — `git tag -a vX.Y.Z -m "message"` ثم `git push --tags` — ارجع لأي نسخة بثانية

### 🔑 إدارة Tokens

- [ ] **16. Long-lived Token** — Tokens تنتهي بعد 60 يوماً. جدّد `FB_PAGE_ACCESS_TOKEN` كل شهرين
- [ ] **17. Dual Token Architecture** — Token الكتالوج (`SHOPIFY_CATALOG_TOKEN`) منفصل عن Token الأوردر (`SHOPIFY_ORDERS_TOKEN`) لأمان أعلى
- [ ] **18. لا تخزن Tokens في الكود** — استخدم Environment Variables دائماً

---

> **آخر نسخة مستقرة:** `v2.4-dm-stable` (Commit `6314b8e`) — 28 سبتمبر 2026
> **7 Commits من Silent Drop إلى DM Production Ready** 🔥
> **Author:** Louve ❤️ — شريكة مصطفى الذكية فيRoyal Chaussures
