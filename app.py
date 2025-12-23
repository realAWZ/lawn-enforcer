import streamlit as st
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Lawn Enforcer", page_icon="🚜", layout="centered")

st.title("🚜 The Lawn Enforcer")
st.markdown("### 🌎 Global Weather Command")

# --- 1. SETUP DEFAULTS ---
api_success = False
temp_val, wind_val, rain_val = 32, 5, 0.0 # Default to freezing for safety

# --- 2. SMART LOCATION SEARCH ---
st.info("🔎 Search by **City Name** (e.g., Newton) or **Zip Code**")
search_query = st.text_input("Enter Patrol Sector:", value="Newton")

if search_query:
    try:
        # Step A: Search for multiple cities
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={search_query}&count=10&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if "results" in geo_res:
            # Step B: Create a "Pick List"
            city_options = {}
            display_list = []
            
            for result in geo_res["results"]:
                city_name = result.get("name", "Unknown")
                state = result.get("admin1", "")
                country = result.get("country_code", "")
                label = f"{city_name}, {state} ({country})"
                
                city_options[label] = result
                display_list.append(label)
            
            # Step C: The Dropdown Menu
            selected_label = st.selectbox("📍 Confirm Specific Sector:", display_list)
            
            # Step D: Get Data
            final_data = city_options[selected_label]
            lat = final_data["latitude"]
            lon = final_data["longitude"]
            
            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph"
            w_res = requests.get(w_url).json()
            
            current = w_res['current']
            temp_val = current['temperature_2m']
            wind_val = current['wind_speed_10m']
            rain_val = current['rain']
            
            api_success = True
            
        else:
            st.warning("⚠️ No cities found. Try a Zip Code.")

    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")

# --- 3. DASHBOARD ---
if api_success:
    st.divider()
    st.markdown(f"**Current Status for: {selected_label}**")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ Temp", f"{temp_val}°F")
    col2.metric("🌬️ Wind", f"{wind_val} mph")
    col3.metric("🌧️ Rain", f"{rain_val} mm")

# --- 4. MANUAL OVERRIDES ---
st.divider()
st.caption("🚜 **Ground Conditions** (Visual Confirm)")

# UPDATED: Added "Snow Covered" option
grass_status = st.radio("How is the grass?", 
    ["Bone Dry", "Morning Dew", "Soaked / Wet", "Snow Covered ❄️"], 
    horizontal=True)

# --- 5. LOGIC ENGINE ---
if api_success: 
    status = "GO"
    reasons = []

    # Snow Logic (Immediate No Go)
    if grass_status == "Snow Covered ❄️":
        status = "NO GO"
        reasons.append("⛔ SNOW: Mowing Prohibited. Switch to Plowing Ops.")
    
    # Temperature Logic
    elif temp_val > 88:
        status = "NO GO"
        reasons.append("⛔ HEAT: Too hot (>88°F).")
    elif temp_val < 45:
        # Lowered slightly for winter/fall cleanups
        status = "CAUTION"
        reasons.append("⚠️ COLD: Grass dormant or brittle (<45°F).")

    # Wind Logic
    if wind_val > 20:
        status = "NO GO"
        reasons.append("⛔ WIND: Debris risk (>20mph).")

    # Moisture Logic
    if rain_val > 0.1 or grass_status == "Soaked / Wet":
        status = "NO GO"
        reasons.append("⛔ MOISTURE: Rain/Wet Ground.")
    elif grass_status == "Morning Dew":
        status = "CAUTION"
        reasons.append("⚠️ DEW: Wait 60 minutes.")

    # --- 6. VERDICT ---
    st.subheader("MISSION STATUS:")
    if status == "GO":
        st.success("## 🟢 GREEN LIGHT")
        st.markdown("**Conditions Optimal. Start Engines.**")
        if st.button("🚜 MOW"): st.balloons()
    elif status == "CAUTION":
        st.warning("## 🟡 CAUTION")
        for r in reasons: st.write(r)
    else:
        st.error("## 🔴 NO GO")
        for r in reasons: st.write(r)
