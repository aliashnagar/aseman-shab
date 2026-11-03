# فروشگاه آسمان شب

پروژهٔ جنگو برای تبدیل قالب فروشگاه، ورود مدیر و پنل مدیریت به سایت دارای دیتابیس.

## اجرا

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

سایت: `http://127.0.0.1:8000/`  
داشبورد پنل: `http://127.0.0.1:8000/panel/`  
مدیریت محصولات: `http://127.0.0.1:8000/panel/products/`  
مدیریت سفارش‌ها: `http://127.0.0.1:8000/panel/orders/`  
مدیریت دسته‌بندی‌ها و امکانات پیشرفته: `http://127.0.0.1:8000/django-admin/`

ورود پنل با همان کاربر superuser انجام می‌شود. بازدیدهای صفحهٔ اصلی در دیتابیس ثبت می‌شوند و نمودار پنل از زمان اجرای migration مربوط به بازدیدها داده جمع می‌کند.

فهرست محصولات صفحهٔ اصلی از مسیر `GET /api/products/` دریافت می‌شود. فایل‌های CSS، JavaScript، تصویر ماه و فونت‌های محلی در `static/store/` قرار دارند.

## نکتهٔ پیش از انتشار

برای محیط واقعی، مقادیر حساس را در متغیرهای محیطی قرار دهید، مثلاً:

```bash
export SECRET_KEY="your-secret-key"
export DEBUG="False"
export ALLOWED_HOSTS="your-username.pythonanywhere.com,localhost,127.0.0.1"
export CSRF_TRUSTED_ORIGINS="https://your-username.pythonanywhere.com"
```

یا یک فایل `.env` بسازید با نمونه‌ای از [`.env.example`](./.env.example). پروژه به‌صورت خودکار برای فایل `.env` بارگذاری می‌کند.

## استقرار روی PythonAnywhere

1. کد را روی PythonAnywhere آپلود کنید.
2. در بخش «Environment Variables» متغیرهای بالا را تنظیم کنید.
3. وب‌اپ را روی مسیر پروژه و WSGI مطابق این پروژه تنظیم کنید.
4. دستورهای نصب: `pip install -r requirements.txt`
5. اجرای مهاجرت: `python manage.py migrate`
6. اگر لازم شد: `python manage.py createsuperuser`
7. برای فایل‌های آپلودی، پوشه `media/` را در پروژه یا مسیر مناسب پروژه تنظیم کنید.

در حالت تولید، `DEBUG` خاموش است و صفحهٔ 404 اختصاصی به‌صورت سفارشی نمایش داده می‌شود.
