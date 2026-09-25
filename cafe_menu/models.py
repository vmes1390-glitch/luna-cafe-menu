from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# کلاس پایه که تمام مدل‌های ما ازش ارث‌بری می‌کنن
class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"

    # ستون‌های جدول دسته‌بندی
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # برقراری رابطه یک‌به‌چند: یک دسته‌بندی می‌تونه چندین محصول داشته باشه
    items: Mapped[List["Item"]] = relationship(
        back_populates="category", 
        cascade="all, delete-orphan" # اگر دسته‌بندی پاک شد، محصولاتش هم پاک بشن
    )

    def __str__(self):
        return self.name

class Item(Base):
    __tablename__ = "items"

    # ستون‌های جدول محصولات
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text) # اختیاری (می‌تونه خالی باشه)
    price: Mapped[int] = mapped_column(Integer) # قیمت به تومان
    image_url: Mapped[Optional[str]] = mapped_column(String(255)) # لینک عکس محصول
    
    # کلید خارجی (Foreign Key) که به id در جدول categories اشاره می‌کنه
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    
    # برقراری رابطه با جدول دسته‌بندی برای دسترسی راحت‌تر در کدهای پایتون
    category: Mapped["Category"] = relationship(back_populates="items")