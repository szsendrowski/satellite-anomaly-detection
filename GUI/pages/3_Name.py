#Libraries
import streamlit as st
#Page Config
st.set_page_config(
    page_title="Module #3",
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
st.text_input(label="Text")