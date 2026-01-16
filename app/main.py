from app.db.init_db import init_db
from app.db.database import DB_PATH
from app.api.expenses import router as expenses_router
from fastapi import FastAPI

app = FastAPI(title="Expense Tracker API")
app.include_router(expenses_router)


@app.on_event("startup")
def on_startup():
    init_db(DB_PATH)


@app.get("/health")
def health():
    return {"status": "ok"}
