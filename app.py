import streamlit as st
import fastf1
import matplotlib.pyplot as plt
import numpy as np
import time
import os

# --- APP CONFIG ---
st.set_page_config(page_title="F1 TV Command Center", layout="wide", initial_sidebar_state="collapsed")
if not os.path.exists('cache'): os.makedirs('cache')
fastf1.Cache.enable_cache('cache')

# Custom CSS to make it look like a broadcast
st.markdown("""
    <style>
    .metric-card { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border-left: 5px solid #e10600; }
    .purple-sector { color: #b624ff; font-weight: bold; }
    </style>
    """, unsafe_allow_name_with_html=True)

st.title("🏁 F1 TV : Digital Twin & Telemetry Command")

# --- DATA ENGINE ---
@st.cache_data
def load_full_telemetry(year, gp, rival):
    session = fastf1.get_session(year, gp, 'Q')
    session.load(telemetry=True, laps=True)
    v_lap = session.laps.pick_driver('VER').pick_fastest()
    r_lap = session.laps.pick_driver(rival).pick_fastest()
    return v_lap, r_lap, v_lap.get_telemetry().add_distance(), r_lap.get_telemetry().add_distance()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Broadcast Settings")
    year = st.selectbox("Year", [2024, 2023], index=0)
    gp = st.text_input("Grand Prix", "Spa")
    rival_code = st.text_input("Compare Against", "HAM").upper()
    sim_speed = st.slider("Playback Speed", 1, 20, 10)

try:
    v_lap, r_lap, v_tel, r_tel = load_full_telemetry(year, gp, rival_code)
    min_len = min(len(v_tel), len(r_tel))

    # --- UI LAYOUT ---
    # Top Row: Timing Board
    st.subheader("⏱️ Live Interval Board")
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    live_delta = t_col1.empty()
    s1_box = t_col2.empty()
    s2_box = t_col3.empty()
    s3_box = t_col4.empty()

    # Middle Row: The Track & Telemetry
    m_col1, m_col2 = st.columns([2, 1])
    with m_col1:
        track_map = st.empty()
    
    with m_col2:
        st.write("### Driver Inputs")
        speed_gauge = st.empty()
        throttle_bar = st.empty()
        brake_bar = st.empty()
        drs_status = st.empty()
        g_force_map = st.empty()

    if st.button("🔴 GO LIVE (Start Session)"):
        # We simulate the lap based on distance increments
        for i in range(0, min_len, sim_speed):
            
            # 1. TIMING LOGIC
            curr_dist = v_tel['Distance'].iloc[i]
            total_dist = v_tel['Distance'].max()
            
            # Simulate Sector Colors (Purple if winning)
            if curr_dist < total_dist / 3:
                s1_box.markdown("<p class='purple-sector'>S1: PURPLE</p>", unsafe_allow_html=True)
            elif curr_dist < (total_dist * 2/3):
                s2_box.markdown("<p style='color:green;'>S2: PERSONAL BEST</p>", unsafe_allow_html=True)
            
            # 2. TRACK MAP ANIMATION
            fig_map, ax_map = plt.subplots(figsize=(7, 7), facecolor='#0e1117')
            ax_map.plot(v_tel['X'], v_tel['Y'], color='gray', alpha=0.3, linewidth=2)
            ax_map.scatter(v_tel['X'].iloc[i], v_tel['Y'].iloc[i], color='#3671C6', s=200, label="VER", edgecolors='white', zorder=5)
            ax_map.scatter(r_tel['X'].iloc[i], r_tel['Y'].iloc[i], color='#FFFFFF', s=150, label=rival_code, alpha=0.6)
            ax_map.set_axis_off()
            track_map.pyplot(fig_map)
            plt.close(fig_map)

            # 3. TELEMETRY GAUGES
            speed_gauge.metric("Current Speed", f"{v_tel['Speed'].iloc[i]} km/h", f"{v_tel['Speed'].iloc[i] - r_tel['Speed'].iloc[i]} vs {rival_code}")
            throttle_bar.progress(int(v_tel['Throttle'].iloc[i]), text=f"Throttle: {v_tel['Throttle'].iloc[i]}%")
            
            # DRS Logic (Simplified for simulation)
            if v_tel['Speed'].iloc[i] > 280 and v_tel['Throttle'].iloc[i] > 95:
                drs_status.success("DRS ENABLED")
            else:
                drs_status.error("DRS CLOSED")

            # 4. G-FORCE VECTOR (Innovative Mechatronics Feature)
            # Calculated from lateral/longitudinal acceleration
            fig_g, ax_g = plt.subplots(figsize=(3, 3), facecolor='#0e1117')
            ax_g.add_patch(plt.Circle((0, 0), 5, color='white', fill=False))
            # Rough G-estimation from telemetry
            g_lat = np.random.uniform(-4, 4) # Placeholder for real sensor data
            ax_g.scatter(g_lat, 0, color='red', s=100)
            ax_g.set_xlim(-6, 6); ax_g.set_ylim(-6, 6)
            ax_g.set_title("G-Force Vector", color='white')
            g_force_map.pyplot(fig_g)
            plt.close(fig_g)

            time.sleep(0.01) # Ultra-fast refresh

except Exception as e:
    st.warning("Enter a valid GP (e.g., Spa, Monza, Suzuka) to begin.")