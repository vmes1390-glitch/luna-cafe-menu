from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

import models
from models import Item, Category
import schemas
from database import engine, get_db

# ساخت خودکار جداول دیتابیس بر اساس models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cafe Digital Menu",
    description="API for managing cafe menu categories and items"
)

base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")

# اگر پوشه static وجود نداشت، خودش به صورت خودکار می‌سازه‌اش
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ۱. دریافت تمام دسته‌بندی‌ها به همراه محصولات
@app.get("/categories/", response_model=List[schemas.CategoryResponse], tags=["Categories"])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.display_order.asc(), models.Category.id.asc()).all()

# ۲. ایجاد یک دسته‌بندی جدید
@app.post("/categories/", response_model=schemas.CategoryResponse, tags=["Categories"])
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# ۳. ایجاد یک محصول جدید
@app.post("/items/", response_model=schemas.ItemResponse, tags=["Items"])
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == item.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# ۴. ویرایش کامل محصول
@app.put("/items/{item_id}", response_model=schemas.ItemResponse, tags=["Items"])
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    category = db.query(models.Category).filter(models.Category.id == item.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

# ۵. حذف محصول
@app.delete("/items/{item_id}", tags=["Items"])
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return {"message": "محصول با موفقیت حذف شد"}
    return {"error": "محصول پیدا نشد"}

# ۶. صفحه اصلی منو
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def get_menu_page():
    html_path = os.path.join(base_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------------------------------
# تنظیمات پنل مدیریت اختصاصی (SQLAdmin)
# ----------------------------------------------------

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        # نام کاربری و رمز عبور شما و پسرخاله‌تان
        ADMIN_USERS = {
            "erfan": "erfan_pass_123",       # حساب شما
            "vita_admin": "cafe_vita_2026"   # حساب پسرخاله‌تان
        }

        if username in ADMIN_USERS and ADMIN_USERS[username] == password:
            request.session.update({"user": username})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user = request.session.get("user")
        if not user:
            return False
        return True

authentication_backend = AdminAuth(secret_key="vita-secret-random-key-change-this")

# راه‌اندازی داشبورد مدیریت
# راه‌اندازی داشبورد مدیریت
admin = Admin(
    app=app, 
    engine=engine, 
    authentication_backend=authentication_backend, 
    title="Cafe Vita Admin"
)

class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name, Category.display_order]
    column_labels = {
        Category.id: "ID", 
        Category.name: "Category Name",
        Category.display_order: "Order"
    }

    form_excluded_columns = [Category.items]
    
    name = "Category"
    name_plural = "Categories"
    icon = "fa-solid fa-layer-group"

    column_default_sort = [(Category.display_order, False)]

class ItemAdmin(ModelView, model=Item):
    # ستون‌های جدول
    column_list = [Item.id, Item.name, Item.price, Item.category_id]
    
    # برچسب‌های انگلیسی و مرتب
    column_labels = {
        Item.id: "ID",
        Item.name: "Item Name",
        Item.price: "Price (Tomans)",
        Item.description: "Description",
        Item.image_url: "Image URL",
        Item.category_id: "Category ID"
    }
    
    # جستجو و مرتب‌سازی
    column_searchable_list = [Item.name]
    column_sortable_list = [Item.price, Item.id]
    
    name = "Item"
    name_plural = "Menu Items"
    icon = "fa-solid fa-mug-hot"

admin.add_view(CategoryAdmin)
admin.add_view(ItemAdmin)