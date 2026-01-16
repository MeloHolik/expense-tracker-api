from typing import Optional, Dict, Any

from fastapi import FastAPI, Header, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="HTTP Sandbox API")

# ⚠️ Только для экспериментов: данные в памяти, пропадут при перезапуске
fake_db: Dict[int, Dict[str, Any]] = {}
counter = {"value": 0}


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    # Совместимость pydantic v1/v2
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    amount: float = Field(gt=0)
    comment: Optional[str] = Field(default=None, max_length=50)


class CounterSet(BaseModel):
    value: int


class CounterPatch(BaseModel):
    delta: int


@app.get("/")
def root():
    return {"message": "Hello API", "hint": "Open /docs for Swagger"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------
# Path vs Query
# ---------------------------
@app.get("/path/{item_id}")
def path_demo(item_id: int):
    return {"item_id": item_id, "where": "path param"}


@app.get("/query")
def query_demo(category: Optional[str] = None, limit: int = 10):
    return {"category": category, "limit": limit, "where": "query params"}


# ---------------------------
# Headers
# ---------------------------
@app.get("/headers")
def headers_demo(
    user_agent: Optional[str] = Header(default=None),
    x_token: Optional[str] = Header(default=None),
):
    return {"user_agent": user_agent, "x_token": x_token}


@app.get("/need-token")
def need_token(x_token: str = Header(...)):
    # если заголовка нет -> это будет 422 (ошибка валидации)
    return {"x_token": x_token, "note": "Missing header causes 422 (validation)"}


@app.get("/protected")
def protected(x_token: Optional[str] = Header(default=None)):
    # пример "аутентификация/доступ" (401/403)
    if x_token is None:
        raise HTTPException(status_code=401, detail="Missing X-Token header")
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Invalid token")
    return {"status": "ok"}


# ---------------------------
# Body (JSON) + статус-коды
# ---------------------------
@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate):
    # бизнес-правило -> 400 (JSON/схема валидны, но правило запрещает)
    if payload.name.lower() == "forbidden":
        raise HTTPException(status_code=400, detail="name 'forbidden' is not allowed")

    new_id = max(fake_db.keys(), default=0) + 1
    item = {"id": new_id, **model_to_dict(payload)}
    fake_db[new_id] = item
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = fake_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del fake_db[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/items/{item_id}/force", status_code=status.HTTP_201_CREATED)
def create_item_force_id(item_id: int, payload: ItemCreate):
    # конфликт -> 409
    if item_id in fake_db:
        raise HTTPException(status_code=409, detail="Item already exists")
    item = {"id": item_id, **model_to_dict(payload)}
    fake_db[item_id] = item
    return item


# ---------------------------
# Safe / Idempotent playground
# ---------------------------
@app.get("/counter")
def get_counter():
    # Safe: не меняет состояние
    return {"value": counter["value"]}


@app.post("/counter/increment")
def increment_counter():
    # НЕ идемпотентен: повтор меняет результат/состояние
    counter["value"] += 1
    return {"value": counter["value"]}


@app.put("/counter")
def set_counter(payload: CounterSet):
    # Идемпотентен: "установить в X" можно повторять — итог одинаковый
    counter["value"] = payload.value
    return {"value": counter["value"]}


@app.patch("/counter")
def patch_counter(payload: CounterPatch):
    # Обычно НЕ идемпотентен (зависит от смысла patch)
    counter["value"] += payload.delta
    return {"value": counter["value"]}


# ---------------------------
# 500 demo
# ---------------------------
@app.get("/boom")
def boom():
    # специально ломаемся, чтобы увидеть 500
    1 / 0
