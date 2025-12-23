import streamlit as st
import requests
import random
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Lawn Enforcer", page_icon="🚜", layout="centered")

# --- DAD JOKE ENGINE ---
# We define these lists at the top so the app can pick random ones later
loading_jokes = [
    "📡 Contacting the Doppler Radar...",
    "👟 Lacing up the New Balance sneakers...",
    "📏 Measuring neighbor's grass height for comparison...",
    "🍺 Calibrating the cupholder gyroscopes...",
    "🤔 Consulting the Old Farmer's Almanac...",
    "🚜 Warming up the glow plugs...",
    "👀 Checking if the neighbors are watching..."
]

green_light_quotes = [
    "ALPHA DAD STATUS CONFIRMED.",
    "The neighbors aren't ready for stripes this straight.",
    "Execute Order 66 (Mow the Lawn).",
    "Show them why you're the HOA President (even if you aren't).",
    "Grass Stain Risk: Acceptable. Glory: Eternal.",
    "Zero-Turn Mode: ENGAGED.",
    "It's a beautiful day to ignore the rest of the chore list.",
    "Make sure the white shoes don't get green.",
    "Target acquired. Vegetation elimination authorized."
]

# --- APP HEADER ---
st.title("🚜 The Lawn Enforcer")
st.markdown("### 🌎 Global Tactical Command")

# --- 1. SETUP DEFAULTS ---
api_success = False
temp_val, wind_val, rain_val, snow_depth, past_rain, wind_gusts = 32, 5, 0.0, 0.0, 0.0, 0.0
pollen_status = "Low"
max_pollen_val = 0

# --- 2. SMART LOCATION SEARCH ---
st.info("🔎 **Target Acquisition:** Enter City (e.g. Newton) or Zip Code")
search_query = st.text_input("Enter Patrol Sector:", value="Newton")

if search_query:
    # RANDOM LOADING MESSAGE
    with st.spinner(random.choice(loading_jokes)):
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
                selected_label = st.selectbox("📍 Confirm Drop Zone:", display_list)
                
                # Step D: Get Data
                final_data = city_options[selected_label]
                lat = final_data["latitude"]
                lon = final_data["longitude"]
                
                # 1. WEATHER API
                w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain,wind_speed_10m,wind_gusts_10m,snow_depth&daily=precipitation_sum&timezone=auto&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
                w_res = requests.get(w_url).json()
                
                # 2. AIR QUALITY API (For Pollen)
                p_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,olive_pollen,ragweed_pollen&timezone=auto"
                p_res = requests.get(p_url).json()

                # Parse Weather
                current = w_res['current']
                temp_val = current['temperature_2m']
                wind_val = current['wind_speed_10m']
                wind_gusts = current['wind_gusts_10m']
                rain_val = current['rain']
                snow_depth = current['snow_depth'] # Meters
                
                if 'daily' in w_res and 'precipitation_sum' in w_res['daily']:
                    past_rain = w_res['daily']['precipitation_sum'][0]

                # Parse Pollen (With Safety Filter)
                if 'current' in p_res:
                    p_data = p_res['current']
                    raw_values = [
                        p_data.get('alder_pollen'),
                        p_data.get('birch_pollen'),
                        p_data.get('grass_pollen'),
                        p_data.get('ragweed_pollen'),
                        p_data.get('mugwort_pollen'),
                        p_data.get('olive_pollen')
                    ]
                    clean_values = [v for v in raw_values if v is not None]
                    max_pollen_val = max(clean_values) if clean_values else 0

                api_success = True
                
            else:
                st.warning("⚠️ Nowhere found. Did you spell it right? Even I can't find that.")

        except Exception as e:
            st.error(f"⚠️ Radar Jammed. Connection Error: {e}")

# --- 3. AUTO-CALCULATE CONDITIONS ---
ground_status = "Unknown"
leaf_status = "None"
pollen_alert = False

if api_success:
    # A. Ground Status
    if snow_depth > 0.01:
        ground_status = "Snow Covered ❄️"
    elif rain_val > 0.01:
        ground_status = "Raining Now 🌧️"
    elif past_rain > 0.5:
        ground_status = "Soaked / Muddy 💧"
    elif past_rain > 0.1:
        ground_status = "Damp / Dew 🌫️"
    else:
        ground_status = "Bone Dry ☀️"

    # B. Leaf Status
    current_month = datetime.now().month
    if current_month in [10, 11]:
        leaf_status = "Season"
        if wind_gusts > 15 or past_rain > 0.2:
            leaf_status = "Active Fall"

    # C. Pollen Status
    if max_pollen_val > 50: 
        pollen_alert = True
        pollen_status = "HIGH 🔴"
    elif max_pollen_val > 20:
        pollen_status = "Medium 🟡"

# --- 4. DASHBOARD ---
if api_success:
    st.divider()
    st.markdown(f"**Sitrep for: {selected_label}**")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ Temp", f"{temp_val}°F")
    col2.metric("🌬️ Wind", f"{wind_val} mph")
    col3.metric("🌧️ Rain (24h)", f"{past_rain}\"")

    st.info(f"🚜 **Ground Intel:** {ground_status}")
    
    # --- ALERTS SECTION ---
    if leaf_status == "Active Fall":
         st.warning("🍂 **LEAF GOBLIN ALERT:** High winds detected. The trees are fighting back.")
    elif leaf_status == "Season":
         st.caption("🍂 **Tactical Note:** Leaf Season. Watch for rocks/toys/hidden gnomes.")
         
    if pollen_alert:
        st.warning(f"😷 **BIOHAZARD:** Pollen count is {max_pollen_val}. Don't sneeze on the windshield.")

# --- 5. LOGIC ENGINE ---
if api_success: 
    status = "GO"
    reasons = []

    # 1. Snow
    if "Snow" in ground_status:
        status = "NO GO"
        reasons.append("⛔ SNOW: Unless you attached the plow, go back inside.")

    # 2. Temp
    if temp_val > 92:
        status = "NO GO"
        reasons.append("⛔ HEAT: Too hot. Risk of sweating through the good shirt.")
    elif temp_val < 45 and "Snow" not in ground_status:
        status = "CAUTION"
        reasons.append("⚠️ COLD: Flannel jacket required. Coffee recommended.")

    # 3. Wind
    if wind_val > 20:
        status = "NO GO"
        reasons.append("⛔ WIND: High debris risk (and it ruins the stripe pattern).")

    # 4. Moisture
    if "Raining" in ground_status:
        status = "NO GO"
        reasons.append("⛔ RAIN: You will rust the deck. Abort.")
    elif "Soaked" in ground_status:
        status = "NO GO"
        reasons.append(f"⛔ MUD: {past_rain}\" rain yesterday. You'll leave tire tracks.")
    elif "Damp" in ground_status:
        status = "CAUTION"
        reasons.append("⚠️ DAMP: Check for clumping. Clean deck after.")

    # 5. Leaves
    if status != "NO GO":
        if leaf_status == "Active Fall":
            status = "CAUTION"
            reasons.append("🍂 LEAVES: Heavy accumulation. Mulch mode engaged.")
        elif leaf_status == "Season":
            status = "CAUTION"
            reasons.append("🍂 LEAF SEASON: Watch out for the dog's hidden toys.")

    # --- 6. VERDICT ---
    st.subheader("MISSION STATUS:")
    if status == "GO":
        # RANDOM QUOTE PICKER
        random_quote = random.choice(green_light_quotes)
        st.success(f"## 🟢 GREEN LIGHT: {random_quote}")
        st.markdown("**Conditions Optimal.**")
        
        if st.button("🚜 START ENGINES"):
            st.balloons()
            st.toast("Dad Reflexes: Activated.", icon="⚡")
        
    elif status == "CAUTION":
        st.warning("## 🟡 YELLOW LIGHT: PROCEED WITH CARE")
        st.markdown("**Don't tell Mom if you mess it up:**")
        for r in reasons: st.write(r)
        
    else:
        st.error("## 🔴 RED LIGHT: MISSION SCRUBBED")
        st.markdown("**Retreat to Couch. Grab Remote.**")
        for r in reasons: st.write(r)
