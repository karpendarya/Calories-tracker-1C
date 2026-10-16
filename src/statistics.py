from datetime import date, timedelta

import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.repo import get_daily_totals


def prepare_statistics(
    records: list[dict],
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    records_by_date = {record["entry_date"]: record for record in records}
    rows = []
    current_date = start_date

    while current_date <= end_date:
        record = records_by_date.get(current_date)

        rows.append({
            "Дата": current_date,
            "Ккал": float(record["calories"]) if record else 0.0,
            "Белки, г": float(record["protein"]) if record else 0.0,
            "Жиры, г": float(record["fat"]) if record else 0.0,
            "Углеводы, г": float(record["carbs"]) if record else 0.0,
            "Есть записи": record is not None,
        })

        current_date += timedelta(days=1)

    return pd.DataFrame(rows)


def show_statistics(engine: Engine) -> None:
    st.header("Статистика питания")

    today = date.today()
    start_column, end_column = st.columns(2)

    start_date = start_column.date_input(
        "Начало периода",
        value=today - timedelta(days=6),
        key="statistics_start",
    )
    end_date = end_column.date_input(
        "Конец периода", value=today, key="statistics_end"
    )

    if start_date > end_date:
        st.error("Начало периода не может быть позже его окончания.")
        return

    try:
        records = get_daily_totals(engine, start_date, end_date)
    except SQLAlchemyError:
        st.error("Не удалось загрузить статистику. Проверьте подключение к БД.")
        return

    if not records:
        st.info("За выбранный период записей пока нет.")
        return

    data = prepare_statistics(records, start_date, end_date)

    total_calories = sum(record["calories"] for record in records)
    calories_column, days_column = st.columns(2)

    calories_column.metric("Всего калорий, ккал", f"{total_calories:.2f}")
    days_column.metric("Дней с записями", len(records))

    st.subheader("Калории по дням")
    st.caption(
        "Дни без записей показаны как 0. "
        "Это означает отсутствие данных в дневнике."
    )

    if len(data) == 1:
        st.bar_chart(data, x="Дата", y="Ккал")
    else:
        st.line_chart(data, x="Дата", y="Ккал")

    st.subheader("Итоги по дням")

    st.dataframe(
        data,
        hide_index=True,
        column_config={
            "Дата": st.column_config.DateColumn("Дата", format="DD.MM.YYYY"),
            "Ккал": st.column_config.NumberColumn("Ккал", format="%.2f"),
            "Белки, г": st.column_config.NumberColumn(
                "Белки, г", format="%.2f"
            ),
            "Жиры, г": st.column_config.NumberColumn("Жиры, г", format="%.2f"),
            "Углеводы, г": st.column_config.NumberColumn(
                "Углеводы, г", format="%.2f"
            ),
            "Есть записи": st.column_config.CheckboxColumn("Есть записи"),
        },
    )