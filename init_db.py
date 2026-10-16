from pathlib import Path

from sqlalchemy import inspect

from database import get_engine


SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def initialize_database() -> list[str]:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    engine = get_engine()

    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(schema)
            table_names = inspect(connection).get_table_names()
        return table_names
    finally:
        engine.dispose()


if __name__ == "__main__":
    tables = initialize_database()
    print("Таблицы базы данных: " + ", ".join(tables))