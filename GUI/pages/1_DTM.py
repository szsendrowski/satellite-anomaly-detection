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
url = "https://raw.githubusercontent.com/Krzy-888/MojeMapy/15f9902c22377c53848e926c78cc9ab3311a2ece/density_map_DOY288_alt525km_Kp4.3.npy"
response = requests.get(url)
data = np.load(io.BytesIO(response.content), allow_pickle=True)

# Coordinates
height, width = data.shape
lon = np.linspace(-180, 180, width)
lat = np.linspace(90, -90, height)


fig = px.imshow(
    data,
    x=lon,
    y=lat,
    origin='upper',
    color_continuous_scale='Viridis',
    aspect='auto'
)

fig.update_layout(
    xaxis_title="Longitude [°]",
    yaxis_title="Latitude [°]",
    coloraxis_colorbar=dict(title="Density"),
    paper_bgcolor='#000e48',
    plot_bgcolor='#000e48',
    title="Density Map (DTM)"
)

st.plotly_chart(fig, use_container_width=True)
