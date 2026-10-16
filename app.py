import streamlit as st


st.set_page_config(page_title="Дневник питания", layout="wide")

st.title("Дневник питания")
st.write("Приложение для учета питания и расчета КБЖУ.")

catalog_tab, diary_tab, statistics_tab = st.tabs(
    ["Каталог блюд", "Дневник питания", "Статистика"]
)

with catalog_tab:
    st.header("Каталог блюд")
    st.info("Здесь можно будет добавлять, искать и редактировать блюда.")

with diary_tab:
    st.header("Дневник питания")
    st.info("Здесь можно будет записывать порции и смотреть итоги за день.")

with statistics_tab:
    st.header("Статистика")
    st.info("Здесь появится график потребления калорий за выбранный период.")