from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# --- اسکیماهای مربوط به محصولات (Items) ---
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    image_url: Optional[str] = None

class ItemCreate(ItemBase):
    category_id: int

class ItemResponse(ItemBase):
    id: int
    category_id: int

    # به Pydantic اجازه می‌ده اطلاعات رو مستقیم از آبجکت‌های SQLAlchemy بخونه
    model_config = ConfigDict(from_attributes=True)


# --- اسکیماهای مربوط به دسته‌بندی‌ها (Categories) ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    items: List[ItemResponse] = []

    model_config = ConfigDict(from_attributes=True)