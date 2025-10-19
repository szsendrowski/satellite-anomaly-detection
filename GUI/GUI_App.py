#Liblaries
import streamlit as st

st.markdown("""<style>
[data-testid="stMain"]{
    background-color: #001d49;
}
[data-testid="stSidebarNavLink"] {
        color: #003a6c !important;
        font-weight: bold !important;
        text-decoration: none !important;
    }

</style>
""", unsafe_allow_html=True)


#Configurations
st.sidebar.header("HANS")

st.set_page_config(
    page_title="HANS",
    page_icon='💫'
)
st.title("Helio Alert Notifications System")
