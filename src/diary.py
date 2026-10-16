from datetime import date
from decimal import Decimal

import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.repo import add_diary_entry, get_diary_entries, get_dishes


def show_entry_form(
    engine: Engine,
    entry_date: date,
    dishes: list[dict],
) -> None:
    st.subheader("Добавить запись")

    dishes_by_id = {dish["id"]: dish for dish in dishes}

    with st.form("add_diary_entry_form"):
        dish_id = st.selectbox(
            "Выберите блюдо",
            options=list(dishes_by_id),
            format_func=lambda value: (
                f"{dishes_by_id[value]['name']} (ID: {value})"
            ),
            key="diary_dish_selector",
        )

        weight = st.number_input(
            "Вес порции, г",
            min_value=0.01,
            max_value=99999999.99,
            value=100.0,
            step=1.0,
            format="%.2f",
        )

        submitted = st.form_submit_button("Добавить в дневник")

    if not submitted:
        return

    try:
        added = add_diary_entry(
            engine, dish_id, entry_date, Decimal(str(weight))
        )
    except SQLAlchemyError:
        st.error("Не удалось сохранить запись. Проверьте подключение к БД.")
        return

    if not added:
        st.error("Блюдо не найдено. Обновите страницу.")
        return

    st.session_state["diary_message"] = "Запись добавлена в дневник."
    st.rerun()


def show_daily_entries(engine: Engine, entry_date: date) -> None:
    st.subheader("Записи за выбранный день")

    try:
        entries = get_diary_entries(engine, entry_date)
    except SQLAlchemyError:
        st.error("Не удалось загрузить дневник. Проверьте подключение к БД.")
        return

    if not entries:
        st.info("За выбранный день записей пока нет.")
        return

    st.caption("КБЖУ рассчитаны для указанного веса каждой порции.")

    st.dataframe(
        entries,
        hide_index=True,
        column_order=[
            "dish_name", "weight_grams", "calories",
            "protein", "fat", "carbs",
        ],
        column_config={
            "dish_name": st.column_config.TextColumn("Блюдо"),
            "weight_grams": st.column_config.NumberColumn(
                "Вес, г", format="%.2f"
            ),
            "calories": st.column_config.NumberColumn("Ккал", format="%.2f"),
            "protein": st.column_config.NumberColumn("Белки, г", format="%.2f"),
            "fat": st.column_config.NumberColumn("Жиры, г", format="%.2f"),
            "carbs": st.column_config.NumberColumn("Углеводы, г", format="%.2f"),
        },
    )

    st.subheader("Итого за день")
    columns = st.columns(4)
    nutrients = [
        ("calories", "Калории, ккал"),
        ("protein", "Белки, г"),
        ("fat", "Жиры, г"),
        ("carbs", "Углеводы, г"),
    ]

    for column, (field, label) in zip(columns, nutrients):
        total = sum((entry[field] for entry in entries), Decimal("0"))
        column.metric(label, f"{total:.2f}")


def show_diary(engine: Engine) -> None:
    st.header("Дневник питания")

    message = st.session_state.pop("diary_message", None)
    if message:
        st.success(message)

    entry_date = st.date_input(
        "Выберите дату", value=date.today(), key="diary_date"
    )

    try:
        dishes = get_dishes(engine)
    except SQLAlchemyError:
        st.error("Не удалось загрузить блюда. Проверьте подключение к БД.")
        return

    if dishes:
        show_entry_form(engine, entry_date, dishes)
    else:
        st.info("Для добавления записи сначала добавьте блюдо в каталог.")

    st.divider()
    show_daily_entries(engine, entry_date)