import streamlit as st
import pandas as pd

df = pd.read_csv('discharge_data.csv')

# Streamlit UI
st.set_page_config(page_title="Spillway Discharge Calculation", page_icon="🚗", initial_sidebar_state="collapsed")

# Define custom CSS for background color and text color
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: black;
            color: white;
        }}
        .stMarkdown h1, h2, h3, h4, h5, h6, p {{
            color: white;
        }}
    </style>
    """, unsafe_allow_html=True
)


st.title('Used Car Price Prediction App')

# Sidebar with links
st.sidebar.header("Useful Links")
st.sidebar.markdown("[GitHub Repository](https://github.com/)")
st.sidebar.markdown("[Docker Image](https://hub.docker.com/r/your_docker_image)")


num_of_gates = st.slider('Select Number of Gates', min_value=1, max_value=16, value=1)

duration = st.number_input('Enter Duration (Hours)', min_value=0.1, value=1.0, step=0.1)

gate_height = st.slider('Enter Gate Opening Height (ft)', min_value=0.5, max_value=10.0, value=10.0, step=0.5)


rate_data = df[df['height'] == gate_height]

if not rate_data.empty:
    cfs_rate = rate_data.iloc[0, 1]
    cfs_rate_str = f"{cfs_rate:.0f}"
    st.text(f"The CFS rate for a gate height of {gate_height} is {cfs_rate_str} CFS.")
else:
    cfs_rate = 0
    st.text("No data available for the selected gate height.")

spd_1 = (num_of_gates * duration * cfs_rate) / (16*24)

st.success(f'SPD rate for entry 1: {spd_1:,.6f}')