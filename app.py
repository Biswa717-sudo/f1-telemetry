import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt

# Setup aesthetics
fastf1.plotting.setup_mpl(misc_mpl_mods=False)
st.set_page_config(page_title="F1 Telemetry Lab", layout="wide")

st.title("🏎️ F1 Telemetry Lab: Verstappen vs. Rival")
st.write("Compare Max's fastest lap against any driver in any recent race.")

# Sidebar for inputs
with st.sidebar:
    year = st.selectbox("Select Year", [2024, 2023])
    gp = st.text_input("Grand Prix (e.g., Bahrain, Monaco)", "Silverstone")
    session_type = st.selectbox("Session", ["Q", "R", "FP3"])
    rival = st.text_input("Compare Max (VER) with:", "NOR").upper()

if st.button("Calculate Telemetry"):
    with st.spinner("Fetching data from FIA servers..."):
        # Load Session
        session = fastf1.get_session(year, gp, session_type)
        session.load()

        # Get fastest laps
        ver_lap = session.laps.pick_driver('VER').pick_fastest()
        riv_lap = session.laps.pick_driver(rival).pick_fastest()

        # Get telemetry
        ver_tel = ver_lap.get_telemetry().add_distance()
        riv_tel = riv_lap.get_telemetry().add_distance()

        # Innovative Plotting
        fig, ax = plt.subplots(3, 1, figsize=(10, 12))
        
        # Speed Trace
        ax[0].plot(ver_tel['Distance'], ver_tel['Speed'], color='#3671C6', label='Max (VER)')
        ax[0].plot(riv_tel['Distance'], riv_tel['Speed'], color='#FFFFFF', label=rival, linestyle='--')
        ax[0].set_ylabel('Speed (km/h)')
        ax[0].legend()

        # Throttle Trace
        ax[1].plot(ver_tel['Distance'], ver_tel['Throttle'], color='#3671C6')
        ax[1].plot(riv_tel['Distance'], riv_tel['Throttle'], color='#FFFFFF', alpha=0.5)
        ax[1].set_ylabel('Throttle %')

        # Brake Trace
        ax[2].plot(ver_tel['Distance'], ver_tel['Brake'], color='#3671C6')
        ax[2].plot(riv_tel['Distance'], riv_tel['Brake'], color='#FFFFFF', alpha=0.5)
        ax[2].set_ylabel('Brake (On/Off)')
        
        st.pyplot(fig)
        st.success(f"Analysis Complete! Max's Lap: {ver_lap['LapTime']} vs {rival}: {riv_lap['LapTime']}")