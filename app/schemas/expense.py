from pydantic import BaseModel, Field
from datetime import datetime


class ExpenseCreate(BaseModel):
    category: str = Field(min_length=1, max_length=15)
    amount: float = Field(gt=0, le=100000)
    comment: str | None = Field(default=None, max_length=50)


class ExpenseOut(BaseModel):
    id: int
    date: datetime
    category: str
    amount: float
    comment: str | None = None


class CategorySummary(BaseModel):
    category: str
    amount: float
    count: int
    average_bill: float

class ExpenseUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=15)
    amount: float | None = Field(default=None, gt=0, le=100000)
    comment: str | None = Field(default=None, max_length=50)
