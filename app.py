import streamlit as st
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="The Lawn Enforcer", page_icon="🚜", layout="centered")

st.title("🚜 The Lawn Enforcer")
st.markdown("### 🌎 Mobile Weather Command")

# --- 1. LOCATION SELECTOR ---
# We use a text input so he can change it if he moves towns.
city = st.text_input("📍 Enter Patrol Sector (City, State):", value="Newton, NJ")

# --- 2. GET WEATHER (Geocoding + Weather API) ---
if city:
    try:
        # Step A: Find the City's Coordinates (Geocoding)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if "results" in geo_res:
            lat = geo_res["results"][0]["latitude"]
            lon = geo_res["results"][0]["longitude"]
            town_name = geo_res["results"][0]["name"]
            
            # Step B: Get Weather for those Coordinates
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph"
            weather_res = requests.get(weather_url).json()
            
            current = weather_res['current']
            temp_val = current['temperature_2m']
            wind_val = current['wind_speed_10m']
            rain_val = current['rain']
            
            # Show the Dashboard
            st.success(f"✅ Locked on: **{town_name}**")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ Temp", f"{temp_val}°F")
            col2.metric("🌬️ Wind", f"{wind_val} mph")
            col3.metric("🌧️ Rain", f"{rain_val} mm")
            
            api_success = True
        else:
            st.error("❌ City not found. Check spelling.")
            api_success = False

    except Exception as e:
        st.error(f"⚠️ Radar Offline: {e}")
        api_success = False
else:
    st.info("Enter a city above to load weather.")
    api_success = False

st.divider()

# --- 3. MANUAL OVERRIDES ---
st.caption("🚜 **Ground Conditions** (Manual Input)")
grass_status = st.radio("How is the grass?", ["Bone Dry", "Morning Dew", "Soaked / Wet"], horizontal=True)

# --- 4. LOGIC ENGINE ---
if api_success:
    status = "GO"
    reasons = []

    # Temperature Logic
    if temp_val > 88:
        status = "NO GO"
        reasons.append("⛔ HEAT: Too hot for operator safety (>88°F).")
    elif temp_val < 50:
        status = "CAUTION"
        reasons.append("⚠️ COLD: Grass may not cut cleanly (<50°F).")

    # Wind Logic
    if wind_val > 20:
        status = "NO GO"
        reasons.append("⛔ WIND: High wind debris risk (>20mph).")

    # Rain/Moisture Logic
    if rain_val > 0 or grass_status == "Soaked / Wet":
        status = "NO GO"
        reasons.append("⛔ MOISTURE: Rain detected or ground wet.")
    elif grass_status == "Morning Dew":
        status = "CAUTION"
        reasons.append("⚠️ DEW: Wait 60 minutes for sun drying.")

    # --- 5. FINAL VERDICT ---
    st.subheader("MISSION STATUS:")

    if status == "GO":
        st.success("## 🟢 GREEN LIGHT: PROCEED")
        st.markdown("**Conditions are optimal. Launch sequence authorized.**")
        if st.button("Start Engines"):
            st.balloons()
            
    elif status == "CAUTION":
        st.warning("## 🟡 YELLOW LIGHT: CAUTION")
        st.write("Proceed with care:")
        for r in reasons: st.write(r)
        
    else:
        st.error("## 🔴 RED LIGHT: STAND DOWN")
        st.write("Mission Aborted:")
        for r in reasons: st.write(r)
