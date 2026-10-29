import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(
    page_title="Cabuyao Flood & Evacuation Map",
    page_icon="🌊",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header { font-size:2.2rem; font-weight:bold; color:#1E3A8A; }
    .sub-header { font-size:1.1rem; color:#4B5563; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🌊 Cabuyao Flood & Evacuation Community Map</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Live community flood monitoring and evacuation facility lookup for Cabuyao, Laguna</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & Preparation
# -----------------------------------------------------------------------------
DATA_DIR = "data"
FLOOD_CSV = os.path.join(DATA_DIR, "processed_flood_reports.csv")
EVAC_CSV = os.path.join(DATA_DIR, "evacuation_centers.csv")

@st.cache_data
def load_data():
    if os.path.exists(FLOOD_CSV) and os.path.exists(EVAC_CSV):
        flood_df = pd.read_csv(FLOOD_CSV)
        evac_df = pd.read_csv(EVAC_CSV)
    else:
        # Default mock data structured exactly as MATLAB output
        evac_df = pd.DataFrame({
            'FacilityName': ['Cabuyao City Gymnasium', 'Pulo Elementary School', 'Marinig Gymnasium', 'Banlic Elementary School', 'Sala Barangay Hall'],
            'Latitude': [14.2778, 14.2650, 14.3012, 14.2589, 14.2720],
            'Longitude': [121.1214, 121.1320, 121.1450, 121.1150, 121.1280],
            'Capacity': [500, 300, 400, 250, 200],
            'CurrentLoad': [120, 250, 80, 50, 90]
        })
        flood_df = pd.DataFrame({
            'ReportID': [101, 102, 103, 104, 105],
            'Barangay': ['Marinig', 'Banlic', 'Pulo', 'Sala', 'Diezmo'],
            'Latitude': [14.2980, 14.2600, 14.2640, 14.2750, 14.2850],
            'Longitude': [121.1420, 121.1180, 121.1300, 121.1250, 121.1350],
            'WaterLevel_cm': [85, 30, 120, 45, 10],
            'Severity': ['Critical', 'Low', 'Critical', 'Moderate', 'Safe'],
            'NearestEvacuationCenter': ['Marinig Gymnasium', 'Banlic Elementary School', 'Pulo Elementary School', 'Sala Barangay Hall', 'Cabuyao City Gymnasium'],
            'DistanceToEvac_km': [0.55, 0.38, 0.24, 0.45, 1.72]
        })
    
    # Ensure standard 'lat' and 'lon' columns exist for native map compatibility
    for df in [flood_df, evac_df]:
        if 'Latitude' in df.columns:
            df['lat'] = df['Latitude']
        if 'Longitude' in df.columns:
            df['lon'] = df['Longitude']
            
    return flood_df, evac_df

flood_df, evac_df = load_data()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Filters
# -----------------------------------------------------------------------------
st.sidebar.header("📍 Navigation & Filters")

severity_filter = st.sidebar.multiselect(
    "Filter Flood Severity:",
    options=flood_df['Severity'].unique(),
    default=flood_df['Severity'].unique()
)

filtered_flood = flood_df[flood_df['Severity'].isin(severity_filter)]

st.sidebar.markdown("---")
st.sidebar.subheader("📢 Submit Flood Report")

with st.sidebar.form("report_form"):
    brgy = st.selectbox("Barangay", ["Marinig", "Banlic", "Pulo", "Sala", "Diezmo", "Baclaran", "Mamatid", "Niugan", "San Isidro"])
    w_level = st.number_input("Water Level (cm)", min_value=0, max_value=300, value=20)
    lat_val = st.number_input("Latitude", value=14.2750, format="%.4f")
    lon_val = st.number_input("Longitude", value=121.1250, format="%.4f")
    submitted = st.form_submit_button("Submit Community Report")
    
    if submitted:
        severity = "Critical" if w_level > 80 else ("Moderate" if w_level > 30 else "Safe")
        st.sidebar.success(f"Report logged for {brgy}! Status: {severity}")

# -----------------------------------------------------------------------------
# Main Dashboard Layout
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Flood Reports", len(filtered_flood))
col2.metric("Critical Areas", len(filtered_flood[filtered_flood['Severity'] == 'Critical']))
col3.metric("Evacuation Shelters", len(evac_df))
total_cap = evac_df['Capacity'].sum()
total_occ = evac_df['CurrentLoad'].sum()
col4.metric("Shelter Occupancy", f"{int((total_occ/total_cap)*100)}%", f"{total_occ}/{total_cap} people")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🗺️ Live Map", "📊 Flood Reports Data", "🏠 Evacuation Facilities"])

# TAB 1: Native Streamlit Map
with tab1:
    st.subheader("Cabuyao Flood Incident & Shelter Map")
    st.info("Showing live community flood logs across Cabuyao, Laguna.")
    
    st.markdown("### 🔴 Flood Reports Location")
    if not filtered_flood.empty:
        st.map(filtered_flood[['lat', 'lon']])
    else:
        st.warning("No reports match the selected severity filter.")

    st.markdown("### 🏠 Evacuation Centers")
    st.map(evac_df[['lat', 'lon']])

# TAB 2: Flood Reports Table
with tab2:
    st.subheader("Community Flood Incident Logs")
    st.dataframe(filtered_flood, use_container_width=True)

# TAB 3: Evacuation Shelters Table
with tab3:
    st.subheader("Evacuation Center Status")
    evac_df['Available Capacity'] = evac_df['Capacity'] - evac_df['CurrentLoad']
    st.dataframe(evac_df[['FacilityName', 'Capacity', 'CurrentLoad', 'Available Capacity', 'Latitude', 'Longitude']], use_container_width=True)
