import streamlit as st

st.set_page_config(page_title="Rain Data", layout="wide")

if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"

idioma_selecionado = st.sidebar.selectbox(
    "Language / Idioma", ["Português", "English"], index=0 if st.session_state["lang"] == "pt" else 1)
if idioma_selecionado == "Português":
    st.session_state["lang"] = "pt"
else:
    st.session_state["lang"] = "en"
lang = st.session_state["lang"]

titulos_menu = {
    "pt": {
        "home": "Início",
        "raindata": "Explorador de Chuva"
    },
    "en": {
        "home": "Home",
        "raindata": "Rain Explorer"
    }
}

home_page = st.Page(
    "pages/home.py", title=titulos_menu[lang]["home"], icon="🏠", default=True)
raindata_page = st.Page("pages/raindata.py",
                        title=titulos_menu[lang]["raindata"], icon="🌧️")

pg = st.navigation([home_page, raindata_page])
pg.run()