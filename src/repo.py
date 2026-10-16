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


def get_daily_totals(
    engine: Engine,
    start_date: date,
    end_date: date,
) -> list[dict]:
    query = text("""
        SELECT
            entry_date,
            SUM(calories * weight_grams / 100) AS calories,
            SUM(protein * weight_grams / 100) AS protein,
            SUM(fat * weight_grams / 100) AS fat,
            SUM(carbs * weight_grams / 100) AS carbs
        FROM diary_entries
        WHERE entry_date BETWEEN :start_date AND :end_date
        GROUP BY entry_date
        ORDER BY entry_date
    """)

    parameters = {
        "start_date": start_date,
        "end_date": end_date,
    }

    with engine.connect() as connection:
        result = connection.execute(query, parameters)
        return [dict(row) for row in result.mappings()]


def delete_diary_entry(
    engine: Engine,
    entry_id: int,
    entry_date: date,
) -> bool:
    query = text("""
        DELETE FROM diary_entries
        WHERE id = :entry_id AND entry_date = :entry_date
    """)

    parameters = {
        "entry_id": entry_id,
        "entry_date": entry_date,
    }

    with engine.begin() as connection:
        result = connection.execute(query, parameters)
        return result.rowcount == 1