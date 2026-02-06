from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastf1
import pandas as pd
import os

app = FastAPI()

# Allow connection from anywhere (Simplifies Render/Vercel link)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use a temp folder for cache to avoid permission errors on servers
fastf1.Cache.enable_cache('/tmp')

@app.get("/api/race-telemetry/{year}/{gp}/{session}")
def get_telemetry(year: int, gp: str, session: str):
    try:
        # Load Session
        race = fastf1.get_session(year, gp, session)
        race.load(telemetry=True, laps=True)
        
        # Get Max vs Rival (Example: VER vs NOR)
        # In a real app, you can pass these as query params
        drivers = ['VER', 'NOR', 'HAM', 'LEC']
        grid_data = []

        for driver in drivers:
            try:
                lap = race.laps.pick_driver(driver).pick_fastest()
                tel = lap.get_telemetry().add_distance()
                
                # OPTIMIZATION: Downsample (Take 1 point every 20m)
                # This reduces JSON size from 5MB to 200KB for fast loading
                tel_small = tel.iloc[::20, :] 
                
                grid_data.append({
                    "driver": driver,
                    "color": fastf1.plotting.driver_color(driver),
                    "telemetry": tel_small[['Distance', 'Speed', 'nGear', 'Throttle', 'Brake']].to_dict(orient='records')
                })
            except:
                continue

        return {"track": race.event['EventName'], "data": grid_data}
    except Exception as e:
        return {"error": str(e)}