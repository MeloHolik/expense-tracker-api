from datetime import datetime


def create_expense(conn, category, amount, comment):
    """
    Функция для внесения траты в БД и возврата траты с id и data
    """
    request_time = datetime.now().isoformat()

    add_to_db = """
        INSERT INTO expenses (date, category, amount, comment) VALUES (?, ?, ?, ?)
        """
    cur = conn.execute(add_to_db, (request_time, category, amount, comment))
    conn.commit()
    # """это функция добавления, теперь надо забрать id и date"""

    return {
        "id": cur.lastrowid,
        "date": request_time,
        "category": category,
        "amount": amount,
        "comment": comment,
    }


def get_sorted_expenses(
    conn, category: str | None = None, limit: int = 100, skip: int = 0):
    params = []
    query = "SELECT id, date, category, amount, comment FROM expenses"

    if category is not None:
        query += " WHERE category = ?"
        params.append(category)

    query += " ORDER BY date DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_summary(conn):
    query = """
        SELECT category, 
        SUM(amount) AS amount,
        COUNT(*) AS count,
        AVG(amount) AS average_bill
        FROM expenses
        GROUP BY category
        ORDER BY amount DESC
        """

    rows = conn.execute(query).fetchall()
    return [dict(r) for r in rows]


def get_id_expense(conn, expense_id):
    select_id = """
    SELECT id, date, category, amount, comment FROM expenses WHERE id = ?
    """

    expense = conn.execute(select_id, [expense_id]).fetchone()
    return dict(expense) if expense else None


def update_expense(conn, expense_id: int, update_data: dict):
    if not update_data:
        return False

    allowed = {"category", "amount", "comment"}

    parts = []
    values = []
    for key, value in update_data.items():
        if key not in allowed:
            continue

        parts.append(f"{key} = ?")
        values.append(value)

    set_clause = ", ".join(parts)
    query = f"UPDATE expenses SET {set_clause} WHERE id = ?"
    values.append(expense_id)

    cur = conn.execute(query, values)
    conn.commit()

    if cur.rowcount == 0:
        return None

    updated_data = """
    SELECT id, date, category, amount, comment FROM expenses WHERE id = ?
    """

    expense = conn.execute(updated_data, [expense_id]).fetchone()
    return dict(expense) if expense else None


def delete_expense(conn, expense_id):
    delete_id = """
    DELETE FROM expenses WHERE id = ?
    """
    cur = conn.execute(delete_id, [expense_id])
    conn.commit()
    return cur.rowcount
