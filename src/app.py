import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.database import get_engine
from src.repo import add_dish, get_dishes


@st.cache_resource
def get_database_engine() -> Engine:
    return get_engine()


def show_add_dish_form(engine: Engine) -> None:
    st.subheader("Добавить блюдо")
    st.caption("Укажите пищевую ценность на 100 г блюда.")

    with st.form("add_dish_form"):
        name = st.text_input("Название блюда", max_chars=200)

        calories = st.number_input(
            "Калорийность, ккал",
            min_value=0.0,
            max_value=999999.99,
            step=1.0,
        )

        protein_column, fat_column, carbs_column = st.columns(3)

        protein = protein_column.number_input(
            "Белки, г", min_value=0.0, max_value=100.0, step=0.1
        )
        fat = fat_column.number_input(
            "Жиры, г", min_value=0.0, max_value=100.0, step=0.1
        )
        carbs = carbs_column.number_input(
            "Углеводы, г", min_value=0.0, max_value=100.0, step=0.1
        )

        submitted = st.form_submit_button("Добавить блюдо")

    if not submitted:
        return

    if not name.strip():
        st.error("Введите название блюда.")
        return

    dish = {
        "name": name.strip(),
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
    }

    try:
        add_dish(engine, dish)
    except SQLAlchemyError:
        st.error("Не удалось сохранить блюдо. Проверьте подключение к БД.")
        return

    st.success(f"Блюдо «{dish['name']}» добавлено.")


def show_dish_catalog(engine: Engine) -> None:
    st.subheader("Сохраненные блюда")
    search = st.text_input("Поиск по названию", max_chars=200)

    try:
        dishes = get_dishes(engine, search)
    except SQLAlchemyError:
        st.error("Не удалось загрузить каталог. Проверьте подключение к БД.")
        return

    if not dishes:
        if search.strip():
            st.info("По этому запросу блюда не найдены.")
        else:
            st.info("Каталог пока пуст. Добавьте первое блюдо.")
        return

    st.caption("Все значения КБЖУ указаны на 100 г.")

    st.dataframe(
        dishes,
        hide_index=True,
        column_order=["name", "calories", "protein", "fat", "carbs"],
        column_config={
            "name": st.column_config.TextColumn("Блюдо"),
            "calories": st.column_config.NumberColumn("Ккал", format="%.2f"),
            "protein": st.column_config.NumberColumn("Белки, г", format="%.2f"),
            "fat": st.column_config.NumberColumn("Жиры, г", format="%.2f"),
            "carbs": st.column_config.NumberColumn("Углеводы, г", format="%.2f"),
        },
    )


def main() -> None:
    st.set_page_config(page_title="Дневник питания", layout="wide")

    st.title("Дневник питания")
    st.write("Приложение для учета питания и расчета КБЖУ.")

    engine = get_database_engine()

    catalog_tab, diary_tab, statistics_tab = st.tabs(
        ["Каталог блюд", "Дневник питания", "Статистика"]
    )

    with catalog_tab:
        show_add_dish_form(engine)
        st.divider()
        show_dish_catalog(engine)

    with diary_tab:
        st.header("Дневник питания")
        st.info("Здесь будут доступны записи о питании и итоги за день.")

    with statistics_tab:
        st.header("Статистика")
        st.info("Здесь появится график потребления калорий за период.")