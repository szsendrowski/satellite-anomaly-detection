#Liblaries
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

#Configurations
st.set_page_config(
    page_title="Drag Temperature Model",
    page_icon='💫'
)

st.title("DTM")
"""
raster_path = "example.tif" 
with rasterio.open(raster_path) as src:
    data = src.read(1)
    transform = src.transform
"""

# Współrzędne
height, width = data.shape
lon = np.linspace(src.bounds.left, src.bounds.right, width)
lat = np.linspace(src.bounds.top, src.bounds.bottom, height)

# Plotly heatmap z przezroczystym tłem
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
    paper_bgcolor='#000e48',   # przezroczyste tło całego wykresu
    plot_bgcolor='#000e48'     # przezroczyste tło obszaru wykresu
)

st.plotly_chart(fig, use_container_width=True)
