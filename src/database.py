import tomllib
from pathlib import Path

from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine


CONFIG_PATH = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"

def get_engine() -> Engine:
    with CONFIG_PATH.open("rb") as config_file:
        settings = tomllib.load(config_file)["database"]

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=settings["user"],
        password=settings["password"],
        host=settings["host"],
        port=settings["port"],
        database=settings["name"],
    )

    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )


def check_connection() -> str:
    engine = get_engine()

    try:
        with engine.connect() as connection:
            query = text("SELECT current_database()")
            database_name = connection.execute(query).scalar_one()
        return database_name
    finally:
        engine.dispose()


if __name__ == "__main__":
    connected_database = check_connection()
    print(f"Подключение успешно. База данных: {connected_database}")