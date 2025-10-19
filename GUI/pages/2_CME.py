#Liblaries
import streamlit as st
import plotly.express as px
import numpy as np
import requests
import io

st.set_page_config(
    page_title="CME Risk Assessment",
    page_icon='💫'
)

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")
load_css('https://github.com/szsendrowski/satellite-space-weather/blob/feature/GUI/GUI/assets/style.css')

# URL to npy file
url = "https://raw.githubusercontent.com/Krzy-888/MojeMapy/main/AIA.npy"
response = requests.get(url)

data = np.load(io.BytesIO(response.content), allow_pickle=True)

if isinstance(data, np.ndarray) and data.dtype == 'object':
    data = data.item()
    if "data" in data:
        data = data["data"]
import streamlit as st

st.title("CME Risk Assessment")

custom_scale = ["#000000","#D25400" , "#FF6600", "#FF9147","#FFFFFF"]  
# Visualization
fig = px.imshow(
    data,
    origin="lower",
    color_continuous_scale=custom_scale
)
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
st.plotly_chart(fig, use_container_width=True)

st.write("✅ **LOW risk** – CME likely to dissipate before reaching Earth")