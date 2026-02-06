from pydantic import BaseModel, Field
from datetime import datetime


class ExpenseBase(BaseModel):
    category: str = Field(min_length=1, max_length=15)
    amount: float = Field(gt=0, le=100000)
    comment: str | None = Field(default=None, max_length=50)

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseOut(ExpenseBase):
    id: int
    date: datetime

class CategorySummary(BaseModel):
    category: str
    amount: float
    count: int
    average_bill: float

class ExpenseUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=15)
    amount: float | None = Field(default=None, gt=0, le=100000)
    comment: str | None = Field(default=None, max_length=50)
