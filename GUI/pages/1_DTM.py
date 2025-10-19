#Liblaries
import streamlit as st
import plotly.express as px
import numpy as np
import requests
from io import BytesIO
from PIL import Image
#Configurations
st.set_page_config(
    page_title="Drag Temperature Model",
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
st.title("DTM")
# URL to npy file
SRC = requests.get('https://raw.githubusercontent.com/Krzy-888/HANS_SRC/main/DTM2020KP4.3SIATKA5_content.png')
Map = Image.open(BytesIO(SRC.content))
data = np.array(Map)
data = np.flipud(data)
# Coordinates
height, width, _ = data.shape
lon = np.linspace(-180, 180, width)
lat = np.linspace(90, -90, height)


fig = px.imshow(
    data,
    x=lon,
    y=lat,
    origin='upper',
    aspect='auto'
)

fig.update_layout(
    xaxis_title="Longitude [°]",
    yaxis_title="Latitude [°]",
    paper_bgcolor='#001d49',
    plot_bgcolor='#001d49',
    title="Density Map (DTM)"
)

st.plotly_chart(fig, use_container_width=True)
SRC = requests.get('https://raw.githubusercontent.com/Krzy-888/HANS_SRC/main/Ballistic coefficient.png')
Map = Image.open(BytesIO(SRC.content))
data = np.array(Map)
data = np.flipud(data)
# Coordinates
height, width, _ = data.shape
lon = np.linspace(600, 100, width)
lat = np.linspace(275, -5, height)


fig = px.imshow(
    data,
    x=lon,
    y=lat,
    origin='upper',
    aspect='auto'
)

fig.update_layout(
    xaxis_title="Height [km]",
    yaxis_title="Time [days]",
    paper_bgcolor='#001d49',
    plot_bgcolo='#001d49',
    title="Ballisrtic coefficient"
)

st.plotly_chart(fig, use_container_width=True)