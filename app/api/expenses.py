from app.db.database import get_connection
from app.db import repository
from app.schemas.expense import ExpenseOut, ExpenseCreate, CategorySummary, ExpenseUpdate
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Annotated

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ExpenseOut)
def create_expenses(payload: ExpenseCreate, conn=Depends(get_connection)):

    if payload.category.lower() == "forbidden":
        raise HTTPException(status_code=400, detail="Category is forbidden")

    created_expense = repository.create_expense(
        conn, payload.category, payload.amount, payload.comment)

    return created_expense


@router.get("", status_code=status.HTTP_200_OK, response_model=list[ExpenseOut])
def get_sorted_expenses(
    conn=Depends(get_connection),
    category: Annotated[str | None, Query(min_length=1, max_length=20)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    skip: Annotated[int, Query(ge=0)] = 0,
    ):

    return repository.get_sorted_expenses(conn, category=category, limit=limit, skip=skip)


@router.get("/summary", status_code=status.HTTP_200_OK, response_model=list[CategorySummary])
def get_summary(conn=Depends(get_connection)):
    expenses = repository.get_summary(conn)
    return expenses


@router.get("/{expense_id}", status_code=status.HTTP_200_OK, response_model=ExpenseOut)
def get_id_expense(expense_id: int, conn=Depends(get_connection)):
    expense = repository.get_id_expense(conn, expense_id=expense_id)

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return expense


@router.patch("/{expense_id}", status_code=status.HTTP_200_OK, response_model=ExpenseOut)
def update_expense(payload: ExpenseUpdate, expense_id: int, conn=Depends(get_connection)):
    update_dict = payload.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated_data = repository.update_expense(conn, expense_id, update_dict)

    if updated_data is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    return updated_data


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, conn=Depends(get_connection)):
    deleted_count = repository.delete_expense(conn, expense_id=expense_id)

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")

    return
