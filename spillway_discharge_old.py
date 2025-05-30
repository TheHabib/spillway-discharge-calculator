import streamlit as st
import pandas as pd

df = pd.read_csv('discharge_data.csv')

# Streamlit UI
st.set_page_config(page_title="Spillway Discharge Calculation", page_icon="🌊", initial_sidebar_state="collapsed")

st.title('Spillway Discharge Calculation')

# Sidebar with links
st.sidebar.header("Useful Links")
st.sidebar.markdown("[GitHub Repository](https://github.com/)")
st.sidebar.markdown("[Docker Image](https://hub.docker.com/r/your_docker_image)")

# Initialize session state for calculations
if 'calculations' not in st.session_state:
    st.session_state.calculations = [{
        'num_of_gates': None,
        'duration': None,
        'gate_height': None
    }]

# Function to add a new calculation
def add_calculation():
    st.session_state.calculations.append({
        'num_of_gates': None,
        'duration': None,
        'gate_height': None
    })

# Display existing calculations and inputs
for i, calc in enumerate(st.session_state.calculations):
    st.write(f"**Calculation {i+1}**")
    
    calc['num_of_gates'] = st.slider(f'Select Number of Gates for Calculation {i+1}', min_value=1, max_value=16, value=calc['num_of_gates'] if calc['num_of_gates'] is not None else 1)
    
    calc['duration'] = st.number_input(f'Enter Duration (Hours) for Calculation {i+1}', min_value=0.1, value=calc['duration'] if calc['duration'] is not None else 1.0, step=0.1)
    
    calc['gate_height'] = st.slider(f'Enter Gate Opening Height (ft) for Calculation {i+1}', min_value=0.5, max_value=10.0, value=calc['gate_height'] if calc['gate_height'] is not None else 0.5, step=0.5)
    
    if calc['num_of_gates'] is not None and calc['duration'] is not None and calc['gate_height'] is not None:
        rate_data = df[df['height'] == calc['gate_height']]
        
        if not rate_data.empty:
            cfs_rate = rate_data.iloc[0, 1]
            cfs_rate_str = f"{cfs_rate:.0f}"
            st.text(f"The CFS rate for a gate height of {calc['gate_height']} is {cfs_rate_str} CFS.")
        else:
            cfs_rate = 0
            st.text("No data available for the selected gate height.")
        
        spd = (calc['num_of_gates'] * calc['duration'] * cfs_rate) / 384
        st.success(f'SPD rate for Calculation {i+1}: {spd:,.6f}')
    else:
        st.warning("Please enter all values for the calculation.")

# Add a button to allow adding more calculations
if len(st.session_state.calculations) < 16:
    if st.button('Add Another Calculation'):
        add_calculation()

# Calculate the total SPD rate
total_spd = sum((calc['num_of_gates'] * calc['duration'] * df[df['height'] == calc['gate_height']].iloc[0, 1]) / 384 for calc in st.session_state.calculations if calc['num_of_gates'] is not None and calc['duration'] is not None and calc['gate_height'] is not None and not df[df['height'] == calc['gate_height']].empty)

st.header(f'Total SPD rate: {total_spd:,.6f}')
