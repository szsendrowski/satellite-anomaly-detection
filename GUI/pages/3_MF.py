#Libraries
import streamlit as st
import plotly.express as px
import numpy as np
import requests
from io import BytesIO
from PIL import Image
#Page Config
st.set_page_config(
    page_title="TMF",
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

SRC = requests.get('https://raw.githubusercontent.com/Krzy-888/HANS_SRC/main/total_field_Map.png')
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
    title="Total Magnetic Field"
)

st.plotly_chart(fig, use_container_width=True)
fig_2 = requests.get('https://raw.githubusercontent.com/Krzy-888/HANS_SRC/main/total_field_fig.png')
balistics = Image.open(BytesIO(fig_2.content))
dat_2 = np.array(balistics)
dat_2 = np.flipud(dat_2)
dat_2 = np.fliplr(dat_2)
# Coordinates
height, width, _ = dat_2.shape
x = np.linspace(17.5, 45, width)
y = np.linspace(-0.25, 12.25, height)


fig_balistics = px.imshow(
    dat_2,
    x=x,
    y=y,
    origin='lower',
    aspect='y'
)

fig_balistics.update_layout(
    xaxis_title="Time [h]",
    yaxis_title="Magnetig Field intensity [μT]",
    paper_bgcolor='#001d49',
    plot_bgcolor='#001d49',
    title="Total Magnetic Field along ISS"
)

st.plotly_chart(fig_balistics, use_container_width=True)