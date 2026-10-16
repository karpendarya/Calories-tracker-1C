from sqlalchemy import text
from sqlalchemy.engine import Engine
from datetime import date
from decimal import Decimal


def add_dish(engine: Engine, dish: dict) -> None:
    query = text("""
        INSERT INTO dishes (name, calories, protein, fat, carbs)
        VALUES (:name, :calories, :protein, :fat, :carbs)
    """)

    with engine.begin() as connection:
        connection.execute(query, dish)


def get_dishes(engine: Engine, search: str = "") -> list[dict]:
    query = text("""
        SELECT id, name, calories, protein, fat, carbs
        FROM dishes
        WHERE strpos(lower(name), lower(:search)) > 0
        ORDER BY lower(name), id
    """)

    with engine.connect() as connection:
        result = connection.execute(query, {"search": search.strip()})
        return [dict(row) for row in result.mappings()]


def update_dish(engine: Engine, dish_id: int, dish: dict) -> bool:
    query = text("""
        UPDATE dishes
        SET name = :name,
            calories = :calories,
            protein = :protein,
            fat = :fat,
            carbs = :carbs
        WHERE id = :dish_id
    """)

    parameters = {**dish, "dish_id": dish_id}

    with engine.begin() as connection:
        result = connection.execute(query, parameters)
        return result.rowcount == 1


def add_diary_entry(
    engine: Engine,
    dish_id: int,
    entry_date: date,
    weight_grams: Decimal,
) -> bool:
    query = text("""
        INSERT INTO diary_entries (
            dish_id, entry_date, weight_grams,
            dish_name, calories, protein, fat, carbs
        )
        SELECT
            id, :entry_date, :weight_grams,
            name, calories, protein, fat, carbs
        FROM dishes
        WHERE id = :dish_id
        RETURNING id
    """)

    parameters = {
        "dish_id": dish_id,
        "entry_date": entry_date,
        "weight_grams": weight_grams,
    }

    with engine.begin() as connection:
        entry_id = connection.execute(query, parameters).scalar_one_or_none()
        return entry_id is not None


def get_diary_entries(engine: Engine, entry_date: date) -> list[dict]:
    query = text("""
        SELECT
            id,
            dish_name,
            weight_grams,
            calories * weight_grams / 100 AS calories,
            protein * weight_grams / 100 AS protein,
            fat * weight_grams / 100 AS fat,
            carbs * weight_grams / 100 AS carbs
        FROM diary_entries
        WHERE entry_date = :entry_date
        ORDER BY id
    """)

    with engine.connect() as connection:
        result = connection.execute(query, {"entry_date": entry_date})
        return [dict(row) for row in result.mappings()]