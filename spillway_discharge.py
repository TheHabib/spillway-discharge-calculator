import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Spillway Discharge Calculator",
    page_icon="🌊",
    layout="wide"
)

class StreamlitSpillwayCalculator:
    def __init__(self):
        self.csv_filename = "discharge_list.csv"
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize session state variables."""
        if 'calculations' not in st.session_state:
            st.session_state.calculations = []
        if 'total_discharge' not in st.session_state:
            st.session_state.total_discharge = 0.0
        if 'discharge_data' not in st.session_state:
            st.session_state.discharge_data = None
            
    def create_sample_csv(self):
        """Create a sample CSV file with the provided data."""
        sample_data = {
            'height': [0.50, 1.00, 1.50, 2.00, 2.50, 3.00],
            'cfs': [9000, 18000, 29000, 38000, 49000, 58000]
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(self.csv_filename, index=False)
        return df
        
    def load_discharge_data(self):
        """Load discharge data from CSV file."""
        try:
            if not os.path.exists(self.csv_filename):
                st.warning(f"CSV file '{self.csv_filename}' not found. Creating sample file...")
                return self.create_sample_csv()
            
            df = pd.read_csv(self.csv_filename)
            return df
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")
            return self.create_sample_csv()
    
    def get_cfs_for_height(self, height, discharge_data):
        """Get CFS value for a given height from the dataset."""
        # Find exact match first
        exact_match = discharge_data[discharge_data['height'] == height]
        if not exact_match.empty:
            return exact_match['cfs'].iloc[0], True
        
        # If no exact match, find the closest height
        closest_idx = (discharge_data['height'] - height).abs().idxmin()
        closest_height = discharge_data.loc[closest_idx, 'height']
        closest_cfs = discharge_data.loc[closest_idx, 'cfs']
        
        return closest_cfs, False
    
    def calculate_discharge(self, num_gates, duration, gate_height, discharge_data):
        """Calculate total discharge using the formula."""
        cfs_value, exact_match = self.get_cfs_for_height(gate_height, discharge_data)
        
        # Apply the formula: (no of gates * duration * cfs_value) / (16*24)
        # Step 7: Add all discharge values for multiple calculations
        discharge = (num_gates * duration * cfs_value) / (16 * 24)
        
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'num_gates': num_gates,
            'duration': duration,
            'gate_height': gate_height,
            'cfs_value': cfs_value,
            'discharge': discharge,
            'exact_match': exact_match
        }
    
    def display_discharge_chart(self, discharge_data):
        """Display a chart of height vs CFS values."""
        fig = px.line(
            discharge_data, 
            x='height', 
            y='cfs',
            title='Discharge Rate vs Gate Height',
            labels={'height': 'Gate Height', 'cfs': 'Discharge (CFS)'},
            markers=True
        )
        fig.update_layout(
            xaxis_title="Gate Height",
            yaxis_title="Discharge (CFS)",
            hovermode='x unified'
        )
        return fig
    
    def display_calculations_chart(self):
        """Display a chart of all calculations performed."""
        if len(st.session_state.calculations) > 0:
            df = pd.DataFrame(st.session_state.calculations)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"Calc {i+1}" for i in range(len(df))],
                y=df['discharge'],
                name='Individual Discharge',
                text=[f"{val:,.1f}" for val in df['discharge']],
                textposition='auto',
            ))
            
            fig.update_layout(
                title='Discharge Calculations Summary',
                xaxis_title='Calculation Number',
                yaxis_title='Discharge',
                showlegend=False
            )
            return fig
        return None

def main():
    calculator = StreamlitSpillwayCalculator()
    
    # Header
    st.title("🌊 Spillway Discharge Calculator")
    st.markdown("---")
    
    # Load discharge data
    discharge_data = calculator.load_discharge_data()
    st.session_state.discharge_data = discharge_data
    
    # Input section in main screen
    st.header("📊 Calculation Parameters")
    
    # Input fields in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_gates = st.number_input(
            "Number of Gates",
            min_value=1,
            max_value=50,
            value=1,
            step=1,
            help="Enter the number of spillway gates"
        )
    
    with col2:
        duration = st.number_input(
            "Duration (hours)",
            min_value=0.1,
            max_value=1000.0,
            value=1.0,
            step=0.1,
            help="Enter the duration in hours"
        )
    
    with col3:
        gate_height = st.number_input(
            "Gate Opening Height",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Enter the gate opening height"
        )
    

    
    # Calculate and Clear buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🧮 Calculate Discharge", type="primary", use_container_width=True):
            result = calculator.calculate_discharge(
                num_gates, duration, gate_height, discharge_data
            )
            
            # Step 7: Add to session state and accumulate total discharge
            st.session_state.calculations.append(result)
            st.session_state.total_discharge += result['discharge']
            
            st.success(f"✅ Calculation completed! Individual discharge: {result['discharge']:,.2f}")
            
            # Show warning if height was approximated
            if not result['exact_match']:
                closest_height = discharge_data.loc[(discharge_data['height'] - gate_height).abs().idxmin(), 'height']
                st.warning(f"⚠️ Using closest available height: {closest_height} (CFS: {result['cfs_value']:,})")
    
    with col_btn2:
        if st.button("🗑️ Clear All Calculations", use_container_width=True):
            st.session_state.calculations = []
            st.session_state.total_discharge = 0.0
            st.success("🧹 All calculations cleared!")
    
    st.markdown("---")
    
    # Results section
    st.header("📋 Calculation Results")
    
    if len(st.session_state.calculations) > 0:
        # Summary metrics
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            st.metric("Total Calculations", len(st.session_state.calculations))
        with col_y:
            st.metric("Total Discharge", f"{st.session_state.total_discharge:,.2f}")
        with col_z:
            avg_discharge = st.session_state.total_discharge / len(st.session_state.calculations)
            st.metric("Average Discharge", f"{avg_discharge:,.2f}")
        
        # Results table
        results_df = pd.DataFrame(st.session_state.calculations)
        results_df = results_df[['timestamp', 'num_gates', 'duration', 'gate_height', 'cfs_value', 'discharge']]
        results_df.columns = ['Timestamp', 'Gates', 'Duration (hrs)', 'Height', 'CFS Value', 'Discharge']
        
        # Format the dataframe
        results_df['CFS Value'] = results_df['CFS Value'].apply(lambda x: f"{x:,}")
        results_df['Discharge'] = results_df['Discharge'].apply(lambda x: f"{x:,.2f}")
        
        st.dataframe(results_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"spillway_calculations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("👆 Enter parameters above and click 'Calculate Discharge' to see results!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        **Formula Used:** `Total Discharge = (Number of Gates × Duration × CFS Value) ÷ (16 × 24)`
        
        **Note:** If exact height match is not found in the dataset, the closest available value is used.
        """
    )

if __name__ == "__main__":
    main()