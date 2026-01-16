import streamlit as st

if st.session_state["lang"] == "pt":
    st.title("Bem-vindo")
    st.write("Esta é a página inicial do RainData.")
else:
    st.title("Welcome")
    st.write("This is the home page of RainData.")