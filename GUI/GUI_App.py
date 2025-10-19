#Liblaries
import streamlit as st

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")
load_css('GUI\assets\style.css')

#Configurations
st.sidebar.header("HANS")

st.set_page_config(
    page_title="HANS",
    page_icon='💫'
)
st.title("Helio Alert Notifications System")
