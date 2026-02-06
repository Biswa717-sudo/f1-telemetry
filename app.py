import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
import os

# --- INITIAL SETUP ---
fastf1.plotting.setup_mpl(misc_mpl_mods=False)
st.set_page_config(page_title="Verstappen Telemetry Lab", layout="wide")

# Enable caching to speed up data loading and stay within memory limits
if not os.path.exists('cache'):
    os.makedirs('cache')
fastf1.Cache.enable_cache('cache')

st.title("🏎️ Verstappen Telemetry Lab")
st.markdown("### Compare Max's performance against the grid.")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Race Settings")
    year = st.selectbox("Year", [2025, 2024, 2023], index=1)
    gp = st.text_input("Grand Prix Name", "Silverstone")
    session_type = st.selectbox("Session", ["Q", "R", "FP3", "FP2", "FP1"])
    rival_code = st.text_input("Rival Driver Code (e.g., NOR, HAM, LEC)", "NOR").upper()
    
    st.info("Note: First load might take 30-60s while we pull data from FIA servers.")

# --- DATA PROCESSING ---
if st.button("Analyze Lap Data"):
    try:
        with st.spinner(f"Downloading {year} {gp} data..."):
            session = fastf1.get_session(year, gp, session_type)
            session.load()

            # Get fastest laps
            ver_lap = session.laps.pick_driver('VER').pick_fastest()
            riv_lap = session.laps.pick_driver(rival_code).pick_fastest()

            # Get telemetry
            ver_tel = ver_lap.get_telemetry().add_distance()
            riv_tel = riv_lap.get_telemetry().add_distance()

        # --- TELEMETRY CHART ---
        st.subheader(f"Speed Trace: VER vs {rival_code}")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(ver_tel['Distance'], ver_tel['Speed'], color='#3671C6', label='Max Verstappen', linewidth=2)
        ax.plot(riv_tel['Distance'], riv_tel['Speed'], color='#FFFFFF', label=rival_code, linestyle='--', alpha=0.7)
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Speed (km/h)')
        ax.legend()
        ax.grid(True, alpha=0.2)
        st.pyplot(fig)

        # --- INNOVATIVE TRACK MAP ---
        st.subheader("Interactive Track Map: Where is Max Gaining?")
        
        # We use Verstappen's coordinates for the track shape
        x = ver_tel['X'].values
        y = ver_tel['Y'].values
        
        # Calculate speed difference (Delta)
        # Resampling so the arrays match length for comparison
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        # Color track by Max's speed
        fig_track, ax_track = plt.subplots(figsize=(10, 10))
        lc = LineCollection(segments, cmap='winter', norm=plt.Normalize(ver_tel['Speed'].min(), ver_tel['Speed'].max()))
        lc.set_array(ver_tel['Speed'])
        lc.set_linewidth(5)
        
        ax_track.add_collection(lc)
        ax_track.axis('equal')
        ax_track.set_axis_off()
        
        cbar = plt.colorbar(lc, ax=ax_track)
        cbar.set_label('Verstappen Speed (km/h)')
        
        st.pyplot(fig_track)
        
        st.success(f"Comparison Live! Max: {ver_lap['LapTime']} | {rival_code}: {riv_lap['LapTime']}")

    except Exception as e:
        st.error(f"Error: {e}")
        st.write("Double check the GP name or if the session has happened yet!")