#Liblaries
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import io 
import cartopy.crs as ccrs
import cartopy.feature as cfeature

#Configurations
st.set_page_config(
    page_title="Drag Temperature Model",
    page_icon='💫'
)

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")
load_css('https://github.com/szsendrowski/satellite-space-weather/blob/feature/GUI/GUI/pages/assets/style.css')

st.title("DTM")
# URL to npy file
url = "https://github.com/Krzy-888/MojeMapy/blob/main/density_map_DOY288_alt525km_Kp4.3.npy"
response = requests.get(url)
data = np.load(io.BytesIO(response.content), allow_pickle=True)

# Coordinates
height, width = data.shape
lon = np.linspace(src.bounds.left, src.bounds.right, width)
lat = np.linspace(src.bounds.top, src.bounds.bottom, height)

# Plotly heatmap 
fig = px.imshow(
    data,
    x=lon,
    y=lat,
    origin='upper',
    color_continuous_scale='Viridis'
)

fig.update_layout(
    xaxis_title="Longitude",
    yaxis_title="Latitude",
    coloraxis_colorbar=dict(title="Wartość"),
    paper_bgcolor='#000e48',
    plot_bgcolor='#000e48'
)

st.plotly_chart(fig, use_container_width=True)
