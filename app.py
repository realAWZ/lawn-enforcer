import streamlit as st
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Lawn Enforcer", page_icon="🚜", layout="centered")

st.title("🚜 The Lawn Enforcer")
st.markdown("### 🌎 Mobile Weather Command")

# --- 1. SETUP DEFAULTS ---
# Default to Newton, NJ if nothing is entered
temp_val, wind_val, rain_val = 75, 5, 0.0
api_success = False

# --- 2. LOCATION SELECTOR ---
city = st.text_input("📍 Enter Patrol Sector:", value="Newton, NJ")

if city:
    try:
        # A. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if "results" in geo_res:
            lat = geo_res["results"][0]["latitude"]
            lon = geo_res["results"][0]["longitude"]
            town_name = geo_res["results"][0]["name"]
            
            # B. Weather
            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph"
            w_res = requests.get(w_url).json()
            
            current = w_res['current']
            temp_val = current['temperature_2m']
            wind_val = current['wind_speed_10m']
            rain_val = current['rain']
            
            st.success(f"✅ Radar Locked: **{town_name}**")
            api_success = True
        else:
            st.warning("⚠️ City not found. Check spelling.")

    except Exception as e:
        st.error("⚠️ Radar Offline (Internet Issue)")

# --- 3. DASHBOARD ---
col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Temp", f"{temp_val}°F")
col2.metric("🌬️ Wind", f"{wind_val} mph")
col3.metric("🌧️ Rain", f"{rain_val} mm")

st.divider()

# --- 4. MANUAL OVERRIDES ---
st.caption("🚜 **Ground Conditions** (Manual Input)")
grass_status = st.radio("How is the grass?", ["Bone Dry", "Morning Dew", "Soaked / Wet"], horizontal=True)

# --- 5. LOGIC ENGINE ---
if api_success or city: # Only run logic if we have data
    status = "GO"
    reasons = []

    if temp_val > 88:
        status = "NO GO"
        reasons.append("⛔ HEAT: Too hot (>88°F).")
    elif temp_val < 50:
        status = "CAUTION"
        reasons.append("⚠️ COLD: Grass tearing risk (<50°F).")

    if wind_val > 20:
        status = "NO GO"
        reasons.append("⛔ WIND: Debris risk (>20mph).")

    if rain_val > 0.1 or grass_status == "Soaked / Wet":
        status = "NO GO"
        reasons.append("⛔ MOISTURE: Rain/Wet Ground.")
    elif grass_status == "Morning Dew":
        status = "CAUTION"
        reasons.append("⚠️ DEW: Wait
