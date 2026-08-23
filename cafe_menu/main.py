from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import models
import schemas
from database import engine, get_db

# ساخت خودکار جداول دیتابیس بر اساس models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cafe Digital Menu",
    description="API for managing cafe menu categories and items"
)

app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در نسخه نهایی اینجا دامنه سایتت رو می‌نویسی
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ۱. دریافت تمام دسته‌بندی‌ها به همراه محصولات داخل هر دسته‌بندی
@app.get("/categories/", response_model=List[schemas.CategoryResponse], tags=["Categories"])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

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
    # چک می‌کنیم که آیا دسته‌بندی انتخابی وجود دارد یا نه
    category = db.query(models.Category).filter(models.Category.id == item.category_id).first()
    if not category:
        # پیام خطای انگلیسی
        raise HTTPException(status_code=404, detail="Category not found")

    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

import os

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def get_menu_page():
    # پیدا کردن مسیر دقیق پوشه‌ای که همین فایل main.py توش قرار داره
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "index.html")
    
    # باز کردن و خواندن فایل HTML با مسیر مطلق
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()