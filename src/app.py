import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.database import get_engine
from src.repo import add_dish, get_dishes, update_dish
from src.diary import show_diary
from src.statistics import show_statistics


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


def show_edit_dish_form(engine: Engine, dishes: list[dict]) -> None:
    st.subheader("Редактировать блюдо")

    dishes_by_id = {dish["id"]: dish for dish in dishes}

    dish_id = st.selectbox(
        "Выберите блюдо",
        options=list(dishes_by_id),
        format_func=lambda value: (
            f"{dishes_by_id[value]['name']} (ID: {value})"
        ),
        key="edit_dish_selector",
    )

    dish = dishes_by_id[dish_id]

    with st.form(f"edit_dish_form_{dish_id}"):
        name = st.text_input(
            "Название блюда", value=dish["name"], max_chars=200
        )

        calories = st.number_input(
            "Калорийность, ккал",
            min_value=0.0,
            max_value=999999.99,
            value=float(dish["calories"]),
            step=1.0,
        )

        protein_column, fat_column, carbs_column = st.columns(3)

        protein = protein_column.number_input(
            "Белки, г",
            min_value=0.0,
            max_value=100.0,
            value=float(dish["protein"]),
            step=0.1,
        )
        fat = fat_column.number_input(
            "Жиры, г",
            min_value=0.0,
            max_value=100.0,
            value=float(dish["fat"]),
            step=0.1,
        )
        carbs = carbs_column.number_input(
            "Углеводы, г",
            min_value=0.0,
            max_value=100.0,
            value=float(dish["carbs"]),
            step=0.1,
        )

        submitted = st.form_submit_button("Сохранить изменения")

    if not submitted:
        return

    if not name.strip():
        st.error("Введите название блюда.")
        return

    updated_dish = {
        "name": name.strip(),
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
    }

    try:
        updated = update_dish(engine, dish_id, updated_dish)
    except SQLAlchemyError:
        st.error("Не удалось обновить блюдо. Проверьте подключение к БД.")
        return

    if not updated:
        st.error("Блюдо не найдено. Обновите страницу.")
        return

    st.session_state["catalog_message"] = "Изменения сохранены."
    st.rerun()


def show_dish_catalog(engine: Engine) -> None:
    st.subheader("Сохраненные блюда")

    message = st.session_state.pop("catalog_message", None)
    if message:
        st.success(message)

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
        column_order=["id", "name", "calories", "protein", "fat", "carbs"],
        column_config={
            "id": st.column_config.NumberColumn("ID", format="%d"),
            "name": st.column_config.TextColumn("Блюдо"),
            "calories": st.column_config.NumberColumn("Ккал", format="%.2f"),
            "protein": st.column_config.NumberColumn("Белки, г", format="%.2f"),
            "fat": st.column_config.NumberColumn("Жиры, г", format="%.2f"),
            "carbs": st.column_config.NumberColumn("Углеводы, г", format="%.2f"),
        },
    )

    st.divider()
    show_edit_dish_form(engine, dishes)


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
        show_diary(engine)

    with statistics_tab:
        show_statistics(engine)