from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# آدرس فایل دیتابیس SQLite ما. این فایل به صورت خودکار کنار پروژه‌ات ساخته می‌شه.
SQLALCHEMY_DATABASE_URL = "sqlite:///./cafe_menu.db"

# ساخت موتور دیتابیس
# چک کردن تردها رو برای SQLite غیرفعال می‌کنیم تا با FastAPI به مشکل نخوره
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# ساخت یک کلاس برای ایجاد نشست‌ها (Sessions) با دیتابیس
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# یک تابع کمکی برای در اختیار گذاشتن دیتابیس به APIها
# این تابع موقع اجرای هر درخواست وب، یک اتصال باز می‌کنه و در پایان می‌بنددش
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()