import os
import time
import requests
import mysql.connector

HA_URL = os.environ.get("HA_URL")
HA_TOKEN = os.environ.get("HA_TOKEN")
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json"
}

ENTITIES = {
    "pv_power":      "sensor.sigen_plant_pv_power",
    "battery_power": "sensor.sigen_plant_battery_power",
    "battery_soc":   "sensor.sigen_plant_battery_state_of_charge",
    "grid_power":    "sensor.sigen_plant_grid_active_power",
    "load_power":    "sensor.sigen_plant_total_load_power",
}

def get_state(entity_id):
    try:
        r = requests.get(f"{HA_URL}/api/states/{entity_id}", headers=HEADERS, timeout=10)
        state = r.json().get("state")
        return float(state)
    except Exception as e:
        print(f"Error reading {entity_id}: {e}")
        return None

def write_row(values):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sigenergy (ts, pv_power, battery_power, battery_soc, grid_power, load_power)
            VALUES (NOW(), %s, %s, %s, %s, %s)
        """, (
            values["pv_power"],
            values["battery_power"],
            values["battery_soc"],
            values["grid_power"],
            values["load_power"],
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error writing to DB: {e}")

def poll():
    values = {}
    for key, entity_id in ENTITIES.items():
        values[key] = get_state(entity_id)
    
    if None in values.values():
        print("Skipping write — one or more entities unavailable")
        return

    write_row(values)
    print(f"Written: {values}")

while True:
    poll()
    time.sleep(30)