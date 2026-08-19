import streamlit as st

from src.utils.i18n import get_text


# Default language
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"


st.set_page_config(
    page_title="RainData",
    layout="wide"
)


# Language selector
col1, col2 = st.columns([6, 1])

with col2:
    lang_options = {
        "🇧🇷 Português": "pt",
        "🇺🇸 English": "en"
    }

    selected_lang = st.selectbox(
        get_text(
            'language',
            st.session_state["lang"]
        ),
        options=list(lang_options.keys()),
        index=list(lang_options.values()).index(
            st.session_state["lang"]
        ),
        label_visibility="collapsed"
    )

st.session_state["lang"] = lang_options[selected_lang]


# Navigation titles
home_title = (
    "Início"
    if st.session_state["lang"] == "pt"
    else "Home"
)

dataset_explorer_title = (
    "Explorador"
    if st.session_state["lang"] == "pt"
    else "Dataset Explorer"
)

data_analysis_title = (
    "Análise Hidrológica"
    if st.session_state["lang"] == "pt"
    else "Hydrological Analysis"
)


# Pages
home_page = st.Page(
    "pages/home.py",
    title=home_title,
    icon="🏠",
    default=True
)

dataset_explorer_page = st.Page(
    "pages/explorer_page.py",
    title=dataset_explorer_title,
    icon="🌧️"
)

data_analysis_page = st.Page(
    "pages/data_analysis_page.py",
    title=data_analysis_title,
    icon="📊"
)


# Navigation
pg = st.navigation(
    [
        home_page,
        dataset_explorer_page,
        data_analysis_page
    ]
)

pg.run()
