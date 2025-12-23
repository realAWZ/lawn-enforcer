import streamlit as st
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Lawn Enforcer", page_icon="🚜", layout="centered")

st.title("🚜 The Lawn Enforcer")
st.markdown("### 🌎 Global Weather Command")

# --- 1. SETUP DEFAULTS ---
api_success = False
# We add variables for snow and past rain
temp_val, wind_val, rain_val, snow_depth, past_rain = 32, 5, 0.0, 0.0, 0.0

# --- 2. SMART LOCATION SEARCH ---
st.info("🔎 Search by **City Name** (e.g., Newton) or **Zip Code**")
search_query = st.text_input("Enter Patrol Sector:", value="Newton")

if search_query:
    try:
        # Step A: Find the City
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={search_query}&count=10&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if "results" in geo_res:
            # Step B: Pick List
            city_options = {}
            display_list = []
            
            for result in geo_res["results"]:
                city_name = result.get("name", "Unknown")
                state = result.get("admin1", "")
                country = result.get("country_code", "")
                label = f"{city_name}, {state} ({country})"
                city_options[label] = result
                display_list.append(label)
            
            # Step C: Select City
            selected_label = st.selectbox("📍 Confirm Specific Sector:", display_list)
            
            # Step D: Get Data
            final_data = city_options[selected_label]
            lat = final_data["latitude"]
            lon = final_data["longitude"]
            
            # UPDATED URL: We now ask for 'snow_depth' and 'precipitation_sum' (past 24h)
            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain,wind_speed_10m,snow_depth&daily=precipitation_sum&timezone=auto&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
            
            w_res = requests.get(w_url).json()
            
            # Parse Current Data
            current = w_res['current']
            temp_val = current['temperature_2m']
            wind_val = current['wind_speed_10m']
            rain_val = current['rain']
            snow_depth = current['snow_depth'] # In meters
            
            # Parse Past 24h Rain (Daily sum)
            if 'daily' in w_res and 'precipitation_sum' in w_res['daily']:
                # The first entry [0] is today's total forecast
                past_rain = w_res['daily']['precipitation_sum'][0]
            
            api_success = True
            
        else:
            st.warning("⚠️ No cities found. Try a Zip Code.")

    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")

# --- 3. AUTO-CALCULATE GROUND CONDITIONS ---
# This is the "Brain" that decides the status automatically
ground_status = "Unknown"

if api_success:
    # Convert snow depth from meters to inches for easier logic
    snow_inches = snow_depth * 39.37 
    
    if snow_inches > 0.5:
        ground_status = "Snow Covered ❄️"
    elif rain_val > 0.01:
        ground_status = "Raining Now 🌧️"
    elif past_rain > 0.5:
        ground_status = "Soaked / Muddy 💧"
    elif past_rain > 0.1:
        ground_status = "Damp / Dew 🌫️"
    else:
        ground_status = "Bone Dry ☀️"

# --- 4. DASHBOARD ---
if api_success:
    st.divider()
    st.markdown(f"**Sector Status: {selected_label}**")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌡️ Temp", f"{temp_val}°F")
    col2.metric("🌬️ Wind", f"{wind_val} mph")
    col3.metric("🌧️ Rain (24h)", f"{past_rain}\"")
    col4.metric("🏔️ Snow", f"{round(snow_inches, 1)}\"")

    st.info(f"🚜 **Auto-Detected Ground Condition:** {ground_status}")

# --- 5. LOGIC ENGINE ---
if api_success: 
    status = "GO"
    reasons = []

    # 1. Snow Check
    if "Snow" in ground_status:
        status = "NO GO"
        reasons.append(f"⛔ SNOW: {round(snow_inches, 1)} inches detected. Plowing Ops only.")

    # 2. Temperature Check
    if temp_val > 88:
        status = "NO GO"
        reasons.append("⛔ HEAT: Too hot (>88°F).")
    elif temp_val < 45 and "Snow" not in ground_status:
        status = "CAUTION"
        reasons.append("⚠️ COLD: Grass dormant (<45°F).")

    # 3. Wind Check
    if wind_val > 20:
        status = "NO GO"
        reasons.append("⛔ WIND: Debris risk (>20mph).")

    # 4. Moisture Check
    if "Raining" in ground_status:
        status = "NO GO"
        reasons.append("⛔ ACTIVE RAIN: Precipitation detected.")
    elif "Soaked" in ground_status:
        status = "NO GO"
        reasons.append(f"⛔ MUD: Heavy rain ({past_rain}\") detected in last 24h.")
    elif "Damp" in ground_status:
        status = "CAUTION"
        reasons.append("⚠️ MOISTURE: Ground is damp. Check for clumping.")

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
