import streamlit as st
import requests

st.set_page_config(page_title="Lawn Enforcer", page_icon="🚜")

st.title("🚜 Lawn Enforcer (Rebooted)")

# 1. Simple Connection Test
st.write("Testing Internet Connection...")
try:
    # Just ping Google to see if 'requests' is installed and working
    test = requests.get("https://google.com")
    st.success("✅ Internet & 'Requests' Library are working!")
except Exception as e:
    st.error(f"❌ CRITICAL ERROR: {e}")
    st.stop() # Stop the app so you can see the error

# 2. The Actual App
city = st.text_input("Enter City (e.g. Newton, NJ):", "Newton, NJ")

if city:
    # We use a broad try/except to catch ANY crash and show it on screen
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json"
        res = requests.get(url).json()
        
        if "results" in res:
            lat = res["results"][0]["latitude"]
            lon = res["results"][0]["longitude"]
            
            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph"
            w_data = requests.get(w_url).json()
            
            temp = w_data['current']['temperature_2m']
            wind = w_data['current']['wind_speed_10m']
            
            col1, col2 = st.columns(2)
            col1.metric("Temp", f"{temp}°F")
            col2.metric("Wind", f"{wind} mph")
            
            # Simple Logic
            if temp > 88:
                st.error("⛔ TOO HOT")
            elif wind > 20:
                st.error("⛔ TOO WINDY")
            else:
                st.success("🟢 GO FOR MOW")
                if st.button("Start Engines"):
                    st.balloons()
        else:
            st.warning("City not found.")
            
    except Exception as e:
        st.error(f"Something crashed here: {e}")
