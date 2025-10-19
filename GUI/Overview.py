#Liblaries
import streamlit as st

#Configurations
st.set_page_config(
    page_title="HANS",
    page_icon='💫'
)
st.markdown("""<style>
[data-testid="stMain"]{
    background-color: #001d49;
}
[data-testid="stSidebarNavLink"] {
        color: #003a6c !important;
        font-weight: bold !important;
        text-decoration: none !important;
    }
[data-testid="stSidebar"]{
            background-color: #003b94;
}
</style>
""", unsafe_allow_html=True)


#Page content
st.sidebar.header("HANS")


st.title("Helio Alert Notifications System")
