#Liblaries
import streamlit as st
import plotly.express as px
import numpy as np
import requests
import pandas as pd
import io
#Page Config
st.set_page_config(
    page_title="CME Risk Assessment",
    page_icon='💫'
)
st.markdown("""<style>
[data-testid="stMain"]{
    background-color: #0e1117;
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

# Page content

# URL to npy file
url = "https://raw.githubusercontent.com/Krzy-888/HANS_SRC/main/Sun.npy"
response = requests.get(url)

data = np.load(io.BytesIO(response.content), allow_pickle=True)

st.title("CME Risk Assessment")

custom_scale = ["#000000","#D25400" , "#FF6600", "#FF9147","#FFFFFF"]

# Visualization
brightness_factor = 1.2
contrast_factor = 1.5
mean_val = np.mean(data)
enhanced = (data - mean_val) * contrast_factor + mean_val * brightness_factor
enhanced = np.clip(enhanced, 0, np.max(data))
enhanced_norm = (enhanced - np.min(enhanced)) / (np.max(enhanced) - np.min(enhanced))

fig = px.imshow(
    enhanced_norm,
    origin="lower",
    color_continuous_scale=custom_scale
)
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
st.plotly_chart(fig, use_container_width=True)
Tab = pd.DataFrame(
    {
        "col1": [85],
        "col2": [2],
        "col3": [1],
        "col4": [0]
    },
    index=["col1", "col2", "col3", "col4"],
)
st.table(Tab)

st.write("✅ **LOW risk** – CME likely to dissipate before reaching Earth")