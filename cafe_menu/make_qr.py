import qrcode

# لینک سایتت
url = "https://erfan4831.pythonanywhere.com/"

# ساخت QR کد
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(url)
qr.make(fit=True)

# ذخیره به صورت عکس
img = qr.make_image(fill_color="black", back_color="white")
img.save("luna_cafe_qr.png")

print("QR کد با موفقیت در فایل luna_cafe_qr.png ذخیره شد!")