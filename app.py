import streamlit as st
from src.utils.i18n import get_text

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

st.set_page_config(page_title="Rain Data", layout="wide")

col1, col2 = st.columns([6, 1])
with col2:
    lang_options = {"🇧🇷 Português": "pt", "🇺🇸 English": "en"}
    selected_lang = st.selectbox(
        get_text('language', st.session_state["lang"]),
        options=list(lang_options.keys()),
        index=list(lang_options.values()).index(st.session_state["lang"]),
        label_visibility="collapsed"
    )
    st.session_state["lang"] = lang_options[selected_lang]

home_title = get_text(
    'nav_home',
    st.session_state["lang"]
)

dataset_explorer_title = get_text(
    'nav_explorer',
    st.session_state["lang"]
)

data_analysis_title = get_text(
    'nav_analysis',
    st.session_state["lang"]
)

home_page = st.Page("pages/home.py", title=home_title, icon="🏠", default=True)
dataset_explorer_page = st.Page(
    "pages/explorer_page.py", title=dataset_explorer_title, icon="🌧️")
data_analysis_page = st.Page(
    "pages/data_analysis_page.py", title=data_analysis_title, icon="📊")

pg = st.navigation([home_page, dataset_explorer_page, data_analysis_page])
pg.run()
