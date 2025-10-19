#Liblaries
import streamlit as st

#Configurations
st.sidebar.header("HANS")

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")
st.set_page_config(
    page_title="HANS",
    page_icon='💫'
)
st.title("Helio Alert Notifications System")
