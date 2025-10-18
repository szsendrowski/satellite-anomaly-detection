import streamlit as st
import plotly.express as px
import numpy as np
import requests
import io

st.set_page_config(
    page_title="CME Risk Assasment",
    page_icon='💫'
)

# Poprawny URL do raw pliku .npy
url = "https://raw.githubusercontent.com/Krzy-888/MojeMapy/main/AIA.npy"
response = requests.get(url)

# Wczytanie z allow_pickle=True
data = np.load(io.BytesIO(response.content), allow_pickle=True)

# Jeśli data jest np. słownikiem z 'data', trzeba wydobyć tablicę
if isinstance(data, np.ndarray) and data.dtype == 'object':
    data = data.item()  # jeśli jest dict-like
    if "data" in data:
        data = data["data"]

# Wizualizacja w Plotly
fig = px.imshow(
    data,
    origin="lower",
    color_continuous_scale="hot"
)

st.plotly_chart(fig, use_container_width=True)

st.text_input(label="Text")