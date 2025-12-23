import streamlit as st
# The app will likely crash here if 'requests' is not in requirements.txt
import requests 

# --- PAGE CONFIG ---
st.set_page_config(page_title="The Lawn Enforcer", page_icon="🚜", layout="centered")

st.title("🚜 The Lawn Enforcer")
st.markdown("### 🌎 Mobile Weather Command")

# --- 1. SETUP DEFAULTS (Prevents Crashes) ---
# We set these first so if the internet fails, the app still runs.
temp_val = 75
wind_val = 5
rain_val = 0.0
api_success = False

# --- 2. LOCATION INPUT ---
city = st.text_input("📍 Enter Patrol Sector (City, State):", value="Newton, NJ")

# --- 3. WEATHER RADAR (The Try/Catch Block) ---
if city:
    try:
        # A. Geocoding (Find the Lat/Lon)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if "results" in geo_res:
            lat = geo_res["results"][0]["latitude"]
            lon = geo_res["results"][0]["longitude"]
            town_name = geo_res["results"][0]["name"]
            
            # B. Weather (Get Data)
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph"
            weather_res = requests.get(weather_url).json()
            
            current = weather_res['current']
            temp_val = current['temperature_2m']
            wind_val = current['wind_speed_10m']
            rain_val = current['rain']
            
            st.success(f"✅ Radar Locked: **{town_name}**")
            api_success = True
        else:
            st.warning("⚠️ City not found. Using default sensors.")

    except Exception as e:
        st.error(f"⚠️ Radar Offline: {e}")

# --- 4. DASHBOARD (Always Shows) ---
col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Temp", f"{temp_val}°F")
col2.metric("🌬️ Wind", f"{wind_val} mph")
col3.metric("🌧️ Rain", f"{rain_val} mm")

st.divider()

# --- 5. MANUAL OVERRIDES ---
st.caption("🚜 **Ground Conditions** (Manual Input)")
grass_status = st.radio("How is the grass?", ["Bone Dry", "Morning Dew", "Soaked / Wet"], horizontal=True)

# --- 6. LOGIC ENGINE ---
status = "GO"
reasons = []

# Heat
if temp_val > 88:
    status = "NO GO"
    reasons.append("⛔ HEAT: Too hot (>88°F).")
elif temp_val < 50:
    status = "CAUTION"
    reasons.append("⚠️ COLD: Grass tearing risk (<50°F).")

# Wind
if wind_val > 20:
    status = "NO GO"
    reasons.append("⛔ WIND: Debris risk (>20mph).")

# Moisture
if rain_val > 0.5: # If raining more than 0.5mm
    status = "NO GO"
    reasons.append("⛔ RAIN: Precipitation detected.")
    
if grass_status == "Soaked / Wet":
    status = "NO GO"
    reasons.append("⛔ GROUND: Turf is saturated.")
elif grass_status == "Morning Dew":
    status = "CAUTION"
    reasons.append("⚠️ DEW: Wait for drying.")

# --- 7. FINAL VERDICT ---
st.subheader("MISSION STATUS:")

if status == "GO":
    st.success("## 🟢 GREEN LIGHT")
    st.markdown("**Conditions Optimal. Engines Start.**")
    if st.button("🚜 MOW"):
        st.balloons()
        
elif status == "CAUTION":
    st.warning("## 🟡 CAUTION")
    for r in reasons: st.write(r)
    
else:
    st.error("## 🔴 NO GO")
    st.markdown("**Stand Down.**")
    for r in reasons: st.write(r)
