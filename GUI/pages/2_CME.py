#Liblaries
import streamlit as st
import plotly.express as px
import numpy as np
import requests
import io

st.set_page_config(
    page_title="CME Risk Assasment",
    page_icon='💫'
)

# URL to npy file
url = "https://raw.githubusercontent.com/Krzy-888/MojeMapy/main/AIA.npy"
response = requests.get(url)

data = np.load(io.BytesIO(response.content), allow_pickle=True)

if isinstance(data, np.ndarray) and data.dtype == 'object':
    data = data.item()
    if "data" in data:
        data = data["data"]
import streamlit as st

# Tło tylko dla tej strony
st.markdown(
    """
    <style>
    .reportview-container {
        background: #000000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Strona z własnym tłem")
# Visualization
fig = px.imshow(
    data,
    origin="lower",
    color_continuous_scale="YlOrBr_r"
)

st.plotly_chart(fig, use_container_width=True)

st.text_input(label="Text")