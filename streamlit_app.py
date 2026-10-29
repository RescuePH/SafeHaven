import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Page Configuration
st.set_page_config(
    page_title="Community Flood Emergency Map",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 Community Flood Emergency Map")
st.markdown("""
*A GIS and crowdsourcing platform* designed for Philippine city communities to crowdsource, verify, and visualize localized emergency flood data in real time[cite: 1, 2]. 
Note: Built with a Streamlit frontend and integrated with MATLAB backend analytics.
""")

# Initialize Session State for Crowdsourced Reports
if "reports" not in st.session_state:
    st.session_state.reports = pd.DataFrame([
        {"Location": "Barangay Holy Spirit, QC", "Lat": 14.6760, "Lon": 121.0830, "WaterLevel": 1.2, "Status": "Passable (Light Vehicles)", "Shelter": "Active (Cap: 250)"},
        {"Location": "Project 8, QC", "Lat": 14.6570, "Lon": 121.0250, "WaterLevel": 2.1, "Status": "Impassable", "Shelter": "Full"},
        {"Location": "Commonwealth Ave", "Lat": 14.6820, "Lon": 121.0800, "WaterLevel": 0.5, "Status": "Passable to All", "Shelter": "Active (Cap: 500)"}
    ])

# Sidebar: Submit Community Flood Report
st.sidebar.header("📍 Submit Flood Report")
with st.sidebar.form("report_form"):
    loc_name = st.text_input("Location / Barangay Name")
    lat = st.number_input("Latitude", value=14.6760, format="%.4f")
    lon = st.number_input("Longitude", value=121.0830, format="%.4f")
    water_level = st.slider("Water Level (Meters)", 0.0, 3.0, 0.5, 0.1)
    status = st.selectbox("Road Status", ["Passable to All", "Passable (Light Vehicles)", "Impassable"])
    shelter = st.text_input("Evacuation Shelter Status", "Active (Cap: 300)")
    
    submitted = st.form_submit_button("Submit Emergency Report")
    if submitted:
        new_row = pd.DataFrame([{
            "Location": loc_name, 
            "Lat": lat, 
            "Lon": lon, 
            "WaterLevel": water_level, 
            "Status": status, 
            "Shelter": shelter
        }])
        st.session_state.reports = pd.concat([st.session_state.reports, new_row], ignore_index=True)
        st.success("Report submitted and broadcasted to local responders!")

# Main Dashboard Metrics
col1, col2, col3 = st.columns(3)
df = st.session_state.reports

avg_water = df["WaterLevel"].mean()
max_water = df["WaterLevel"].max()
total_reports = len(df)

col1.metric("Total Active Reports", f"{total_reports}")
col2.metric("Average Water Level", f"{avg_water:.2f} m")
col3.metric("Peak Water Level", f"{max_water:.2f} m")

st.markdown("---")

# MATLAB Backend Integration Status
st.subheader("⚙️ MATLAB Analytics Engine Status")
st.markdown("""
*Data flows into flood_analysis.m to calculate water thresholds and community risk indices.*
""")

# Risk evaluation logic matching the MATLAB backend
if avg_water > 1.5:
    matlab_risk = "CRITICAL 🔴 (Immediate Evacuation Required)"
elif avg_water > 0.8:
    matlab_risk = "HIGH 🟠 (Exercise Extreme Caution)"
elif avg_water > 0.3:
    matlab_risk = "MODERATE 🟡 (Monitor Weather Advisories)"
else:
    matlab_risk = "LOW 🟢 (Normal Conditions)"

st.info(f"*MATLAB Computed Community Risk Index:* {matlab_risk}")

# Interactive GIS Map (PyDeck)
st.subheader("🗺️ Live Community Flood Map")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[Lon, Lat]',
    get_color='[WaterLevel * 80, 255 - (WaterLevel * 60), 50, 160]',
    get_radius='WaterLevel * 300 + 200',
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=df["Lat"].mean(),
    longitude=df["Lon"].mean(),
    zoom=12,
    pitch=30,
)

r = pdk.Deck(
    layers=[layer], 
    initial_view_state=view_state, 
    tooltip={
        "text": "Location: {Location}\nWater Level: {WaterLevel}m\nRoad Status: {Status}\nShelter: {Shelter}"
    }
)
st.pydeck_chart(r)

# Detailed Incident Table for Officials
st.subheader("📋 Verified Incident Reports Table")
st.dataframe(df, use_container_width=True)
