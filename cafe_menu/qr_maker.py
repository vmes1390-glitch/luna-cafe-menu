import qrcode

# آدرس سرور شما (فعلاً آدرس لوکال رو می‌دیم)
url = "http://10.163.164.133:8000"
# تنظیمات ظاهر بارکد
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(url)
qr.make(fit=True)

# ساخت تصویر با رنگ مشکی و پس‌زمینه سفید
img = qr.make_image(fill_color="black", back_color="white")

# ذخیره عکس روی سیستم
img.save("luna_cafe_qr.png")

# پیام انگلیسی جایگزین شد
print("✅ Luna Cafe QR Code generated successfully!")