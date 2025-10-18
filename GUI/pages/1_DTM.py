#Liblaries
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import io 

#Configurations
st.set_page_config(
    page_title="Drag Temperature Model",
    page_icon='💫'
)

st.title("DTM")
# URL to npy file
url = "https://github.com/szsendrowski/satellite-space-weather/blob/feature/GUI/GUI/Test_Data/density_map_DOY288_alt525km_Kp4.3.npy"
response = requests.get(url)

data = np.load(io.BytesIO(response.content))

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
