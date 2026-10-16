from sqlalchemy import text
from sqlalchemy.engine import Engine


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