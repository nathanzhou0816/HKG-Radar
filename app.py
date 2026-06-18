import os
import json
from datetime import datetime
import streamlit as st
import requests
import threading
import time
import requests


st.set_page_config(layout="wide", page_title="Aviation Custom Radar", page_icon="✈️")


# --- BACKGROUND SELF-PING TO PREVENT APP SLEEP ---
def keep_app_alive(url, interval_seconds=3600):
    """Silently pings the app's own URL in the background to prevent cloud idling."""
    # We wait 30 seconds before the first ping to let the app fully deploy
    time.sleep(30)
    while True:
        try:
            # A simple GET request to keep the container warm
            requests.get(url, timeout=10)
        except Exception:
            pass  # Fail silently so it never crashes your main radar dashboard
        time.sleep(interval_seconds)

# Replace this with your actual deployed Streamlit URL once you hit "Deploy"
YOUR_APP_URL = "https://radar-hkg.streamlit.app/" 

# Start the keep-alive background worker only once per app boot
if "ping_thread_started" not in st.session_state:
    st.session_state["ping_thread_started"] = True
    # daemon=True ensures the thread exits cleanly when the app stops
    threading.Thread(target=keep_app_alive, args=(YOUR_APP_URL,), daemon=True).start()
# -------------------------------------------------

LIVERIES_FILE = "saved_liveries.json"

HEAVY_AND_RARE = [
    "B744", "B748", "B772", "B77L", "B773", "B77W", "B788", "B789", "B78X", "B763", "B764",
    "A388", "A359", "A35K", "A332", "A333", "A338", "A339", "A343", "A346",
    "MD11", "A306", "IL96"
]

AIRPORT_DB = {
    "HKG": {"lat": 22.308, "lon": 113.915, "name": "Hong Kong Intl"},
    "CAN": {"lat": 23.392, "lon": 113.299, "name": "Guangzhou Baiyun"},
    "SZX": {"lat": 22.639, "lon": 113.811, "name": "Shenzhen Bao'an"},
    "PVG": {"lat": 31.143, "lon": 121.805, "name": "Shanghai Pudong"},
    "PEK": {"lat": 40.080, "lon": 116.584, "name": "Beijing Capital"},
    "PKX": {"lat": 39.509, "lon": 116.410, "name": "Beijing Daxing"},
    "SIN": {"lat": 1.364, "lon": 103.991, "name": "Singapore Changi"},
    "LHR": {"lat": 51.470, "lon": -0.454, "name": "London Heathrow"}
}

# Master Built-in Fleet Database for HKG & Regional Traffic
DEFAULT_MASTER_DB = {
    # --- CHINA EASTERN AIRLINES & CHINA CARGO ---
    "B-5943": "China Eastern Airlines Airbus A330-200 - eastday.com",
    "B-6452": "China Eastern Airlines Airbus A319 - Magnificent Qinghai",
    "B-6458": "China Eastern Airlines Airbus A319 - Magnificent Qinghai",
    "B-9942": "China Eastern Airlines Airbus A320 - Magnificent Qinghai",
    "B-9943": "China Eastern Airlines Airbus A320 - Magnificent Qinghai",
    "B-6635": "China Eastern Airlines Airbus A320 - Shanghai Disney Resort",
    "B-1837": "China Eastern Airlines Airbus A321 - SkyTeam",
    "B-1838": "China Eastern Airlines Airbus A321 - SkyTeam",
    "B-8976": "China Eastern Airlines Airbus A321 - SkyTeam",
    "B-8977": "China Eastern Airlines Airbus A321 - SkyTeam",
    "B-5908": "China Eastern Airlines Airbus A330-200 - SkyTeam",
    "B-5949": "China Eastern Airlines Airbus A330-200 - SkyTeam",
    "B-6538": "China Eastern Airlines Airbus A330-200 - SkyTeam",
    "B-5243": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-5276": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-5293": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-5802": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-5807": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-5809": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-5817": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-5819": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-5828": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-6141": "China Eastern Airlines Boeing 737-700 - Yunnan Peacock",
    "B-1788": "China Eastern Airlines Boeing 737-800 - Yunnan Peacock",
    "B-1789": "China Eastern Airlines Boeing 737-800 - Yunnan Peacock",
    "B-1790": "China Eastern Airlines Boeing 737-800 - Yunnan Peacock",
    "B-1792": "China Eastern Airlines Boeing 737-800 - Yunnan Peacock",
    "B-6143": "China Eastern Airlines Boeing 737-800 - Yunnan Peacock",
    "B-6507": "China Eastern Airlines Airbus A330-300 - Shanghai Disney Resort",
    "B-5976": "China Eastern Airlines Airbus A330-300 - Pixar Toy Story Land/Disneyland Shanghai",
    "B-5931": "China Eastern Airlines Airbus A330-200 - People's Daily Online",
    "B-5942": "China Eastern Airlines Airbus A330-200 - 60th Anniversary (sticker)",
    "B-1316": "China Eastern Airlines Boeing 737-800 - Shanghai Disneyland Resort - Duffy and Friends",
    "B-1317": "China Eastern Airlines Boeing 737-800 - Shanghai Disney Resort: Frozen",
    "B-2002": "China Eastern Airlines Boeing 777-300ER - China International Import Expo",
    "B-323H": "China Eastern Airlines Airbus A350-900 - 1st A350 delivered from China (sticker)",
    "B-5920": "China Eastern Airlines Airbus A330-200 - WorldSkills Shanghai 2026",
    "B-5969": "China Eastern Airlines Airbus A330-300 - China Telecom (sticker)",
    "B-919A": "China Eastern Airlines COMAC C919 - The World's First C919 (sticker)",
    "B-8119": "China Eastern Airlines Airbus A320 - Shanghai Disney Resort: Zootopia",
    "B-8393": "China Eastern Airlines Airbus A320 - Harbin 2025 Asian Winter Games",
    "B-220F": "China Cargo Airlines Boeing 777F - China Eastern Cold Chain (sticker)",
    "B-5937": "China Eastern Airlines Airbus A330-200 - Harbin 2025 Asian Winter Games",
    "B-658E": "China Eastern Airlines COMAC C919 - Shining Chinese Red (sticker)",
    "B-657T": "China Eastern Airlines COMAC C919 - Shining Chinese Red",
    "B-7349": "China Eastern Airlines Boeing 777-300ER - Shanghai Museum",
    "B-32EP": "China Eastern Airlines Airbus A320neo - Pop Mart DIMOO - Special Friend of China-Thailand Golden Jubilee (sticker)",
    "B-7882": "China Eastern Airlines Boeing 777-300ER - National Museum of China",

    # --- CATHAY PACIFIC & CATHAY CARGO ---
    "B-KQI": "Cathay Pacific Boeing 777-300ER - oneworld",
    "B-KQL": "Cathay Pacific Boeing 777-300ER - oneworld",
    "B-KQM": "Cathay Pacific Boeing 777-300ER - oneworld",
    "B-KQN": "Cathay Pacific Boeing 777-300ER - oneworld",
    "B-KPD": "Cathay Pacific Boeing 777-300ER - oneworld",
    "B-HLR": "Cathay Pacific Airbus A330-300 - Monitoring for Climate Change (sticker)",
    "B-LRJ": "Cathay Pacific Airbus A350-900 - 80th Anniversary Retro",
    "B-LJE": "Cathay Cargo Boeing 747-8F - 80th Anniversary Retro",
    "B-KQU": "Cathay Pacific Boeing 777-300ER - Spirit of Hong Kong - 80th Anniversary Edition",
    "B-KPO": "Cathay Pacific Boeing 777-300ER - 80 Years Together (sticker)",
    "B-LQG": "Cathay Pacific Airbus A350-900 - 80 Years Together (sticker)",
    "B-LRP": "Cathay Pacific Airbus A350-900 - 80 Years Together (sticker)",
    "B-HNF": "Cathay Pacific Boeing 777 - 80 Years Together (sticker)",
    "B-HPS": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HLW": "Cathay Pacific Airbus A330-300 - 80 Years Together (sticker)",
    "B-HNX": "Cathay Pacific Boeing 777-300 - 80 Years Together (sticker)",
    "B-HPE": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HPF": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HPG": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HPK": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HPQ": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HPT": "Cathay Pacific Airbus A330-300 - 80 Years Together (sticker)",
    "B-HYJ": "Cathay Pacific Airbus A330-300 - 80 Years Together (sticker)",
    "B-LAQ": "Cathay Pacific Airbus A330-300 - 80 Years Together (sticker)",
    "B-LBG": "Cathay Pacific Airbus A330-300 - 80 Years Together (sticker)",
    "B-LRM": "Cathay Pacific Airbus A350-900 - 80 Years Together (sticker)",
    "B-LRQ": "Cathay Pacific Airbus A350-900 - 80 Years Together (sticker)",
    "B-HNK": "Cathay Pacific Boeing 777-300 - 80 Years Together (sticker)",
    "B-HNN": "Cathay Pacific Boeing 777-300 - 80 Years Together (sticker)",
    "B-HPI": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HPN": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HPO": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HPP": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HPR": "Cathay Pacific Airbus A321neo - 80 Years Together (sticker)",
    "B-HYI": "Cathay Pacific Airbus A330-300 - 80 Years Together (sticker)",
    "B-LIE": "Cathay Pacific / Cathay Cargo Boeing 747-400ERF - 80 Years Together (sticker)",
    "B-LJF": "Cathay Pacific / Cathay Cargo Boeing 747-8F - 80 Years Together (sticker)",
    "B-LQD": "Cathay Pacific Airbus A350-900 - 80 Years Together (sticker)",
    "B-LRE": "Cathay Pacific Airbus A350-900 - 80 Years Together (sticker)",
    "B-LRR": "Cathay Pacific Airbus A350-900 - 80 Years Together (sticker)",

    # --- HONG KONG EXPRESS ---
    "B-KKE": "Hong Kong Express Airbus A321neo - AXA (sticker)",
    "B-LEE": "Hong Kong Express Airbus A321 - CR7 LIFE Museum Hong Kong (sticker)",

    # --- GREATER BAY AIRLINES ---
    "B-KJD": "Greater Bay Airlines Boeing 737-800 - Greater Bay Area (sticker)",
    "B-KJB": "Greater Bay Airlines Boeing 737-800 - Greater Bay Area (sticker)",

    # --- CHINA SOUTHERN AIRLINES ---
    "B-1168": "China Southern Airlines Boeing 787-9 - 787th Boeing 787",
    "B-6068": "China Southern Airlines Boeing 737-800 - Guizhou Province",
    "B-6069": "China Southern Airlines Boeing 737-800 - Guizhou",
    "B-1979": "China Southern Airlines Boeing 737-800 - Hometown Henan",
    "B-5940": "China Southern Airlines Airbus A330-300 - China International Import Expo",
    "B-1700": "China Southern Airlines Boeing 737-800 - Zhuhai City Of Youth",
    "B-1781": "China Southern Airlines Boeing 737-800 - Energetic Zhuhai",
    "B-2007": "China Southern Airlines Boeing 777-300ER - WorldSkills Shanghai 2022",
    "B-1625": "China Southern Airlines Airbus A321 - China International Consumer Products Expo",
    "B-7996": "China Southern Airlines Boeing 737-800 - Xinjiang Hotan Rural Revitalisation",
    "B-5598": "China Southern Airlines Boeing 737-800 - CAEXPO",
    "B-1832": "China Southern Airlines Airbus A321 - Hainan Island International Film Festival",
    "B-657X": "China Southern Airlines COMAC C919 - GAC Trumpchi",
    "B-308T": "China Southern Airlines Airbus A350-900 - 15th National Games – Vibrant Bay Area",
    "B-658W": "China Southern Airlines COMAC C919 - 15th National Games – Vibrant Bay Area",

    # --- AIR CHINA ---
    "B-6361": "Air China Airbus A321 - Beautiful Sichuan",
    "B-6365": "Air China Airbus A321 - Beautiful Sichuan II",
    "B-5390": "Air China Boeing 737-800 - Gold Peony",
    "B-2006": "Air China Boeing 777-300ER - Love China",
    "B-5422": "Air China Boeing 737-800 - Phoenix",
    "B-5214": "Air China Boeing 737-700 - Pink Peony",
    "B-2032": "Air China Boeing 777-300ER - Star Alliance",
    "B-5198": "Air China Boeing 737-800 - Yellow Peony",
    "B-5497": "Air China Boeing 737-800 - Star Alliance",
    "B-5425": "Air China Boeing 737-800 - Star Alliance",
    "B-6383": "Air China Airbus A321 - Star Alliance",
    "B-308M": "Air China Airbus A350-900 - Star Alliance",
    "B-5977": "Air China Airbus A330-300 - 50th A330 For Air China (sticker)",
    "B-6071": "Air China Airbus A330-200 - Jin Li",
    "B-5912": "Air China Airbus A330-300 - Star Alliance",
    "B-6101": "Air China Airbus A330-300 - Star Alliance",

    # --- STARLUX AIRLINES ---
    "B-58551": "Starlux Airlines Airbus A350-1000 - Carbon Fibre",
    "B-58552": "Starlux Airlines Airbus A350-1000 - Carbon Fibre",

    # --- EVA AIR ---
    "B-16333": "EVA Air Airbus A330-300 - Hello Kitty - Sanrio Characters",
    "B-16722": "EVA Air Boeing 777-300ER - Hello Kitty - My Melody and Kuromi",
    "B-16332": "EVA Air Airbus A330-300 - Sanrio Joyful Dream",
    "B-16715": "EVA Air Boeing 777-300ER - Star Alliance",
    "B-17812": "EVA Air Boeing 787-10 - Star Alliance",
    "B-16217": "EVA Air Airbus A321 - Hello Kitty - Pinky Jet",
    "B-16740": "EVA Air Boeing 777-300ER - Hello Kitty - Lolly Jet",

    # --- CHINA AIRLINES ---
    "B-18007": "China Airlines Boeing 777-300ER - Boeing",
    "B-18311": "China Airlines Airbus A330-300 - SkyTeam",
    "B-18918": "China Airlines Airbus A350-900 - Airbus/Carbon Fibre",
    "B-18101": "China Airlines Airbus A321neo - Pokemon Pikachu Jet",
    "B-18055": "China Airlines Boeing 777-300ER - 'Zootopia 2' movie",
    "B-18916": "China Airlines Airbus A350-900 - Pokemon Pikachu Jet CI2",

    # --- ALL NIPPON AIRWAYS (ANA) ---
    "JA614A": "All Nippon Airways Boeing 767-300ER - Star Alliance",
    "JA882A": "All Nippon Airways Boeing 787-9 - ANA's 50th 787 (sticker)",
    "JA899A": "All Nippon Airways Boeing 787-9 - Star Alliance",
    "JA381A": "All Nippon Airways Airbus A380 - Flying Honu Sea Turtle (Hawaiian Blue)",
    "JA382A": "All Nippon Airways Airbus A380 - Flying Honu Sea Turtle (Hawaiian Ocean)",
    "JA383A": "All Nippon Airways Airbus A380 - Flying Honu Sea Turtle (Hawaiian Sunset)",
    "JA871A": "All Nippon Airways Boeing 787-9 - ANA Future Promise",
    "JA874A": "All Nippon Airways Boeing 787-8 - ANA Future Promise",
    "JA872A": "All Nippon Airways Boeing 787-9 - Star Alliance",
    "JA875A": "All Nippon Airways Boeing 787-9 - Star Alliance",
    "JA894A": "All Nippon Airways Boeing 787-9 - Pokemon",
    "JA784A": "All Nippon Airways Boeing 777-300ER - Pokemon Eevee Jet",
    "JA58AN": "All Nippon Airways Boeing 737-800 - Furusato Jet",
    "JA880A": "All Nippon Airways Boeing 787-9 - Star Alliance",
    "JA921A": "All Nippon Airways Boeing 787-9 - Pokemon Monster Ball (sticker)",

    # --- JAPAN AIRLINES (JAL) ---
    "JA868J": "Japan Air Lines Boeing 787-9 - Contrail (sticker)",
    "JA01XJ": "Japan Airlines Airbus A350-900 - Airbus A350 (Red)",
    "JA02XJ": "Japan Airlines Airbus A350-900 - Airbus A350 (Silver)",
    "JA03XJ": "Japan Airlines Airbus A350-900 - Airbus A350 (Green)",
    "JA15XJ": "Japan Airlines Airbus A350-900 - oneworld",
    "JA861J": "Japan Airlines Boeing 787-9 - oneworld",
    "JA08XJ": "Japan Airlines Airbus A350-900 - Dream Sho Jet (Shohei Ohtani) (sticker)",
    "JA869J": "Japan Airlines Boeing 787-9 - oneworld",
    "JA339J": "Japan Airlines Boeing 737-800 - Tokyo DisneySea - Sparkling Jubilee"

}

def load_liveries():
    # If a valid local file exists, read from it
    if os.path.exists(LIVERIES_FILE):
        with open(LIVERIES_FILE, "r") as f:
            try:
                data = json.load(f)
                if data:  # If file isn't empty
                    return data
            except json.JSONDecodeError:
                pass
                
    # Direct Fallback: write and return our embedded master list
    with open(LIVERIES_FILE, "w") as f:
        json.dump(DEFAULT_MASTER_DB, f, indent=4)
    return DEFAULT_MASTER_DB.copy()

@st.cache_data(show_spinner=False, ttl=1800)
def get_jetphotos_data_via_fr24(flight_id):
    fallback = {"thumbnail": None, "livery_note": None}
    if not flight_id:
        return fallback
    url = f"https://data-live.flightradar24.com/clickback/v1/aircraft.json?aircraft={flight_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.flightradar24.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            res_data = response.json()
            if "images" in res_data and res_data["images"].get("thumbnails"):
                fallback["thumbnail"] = res_data["images"]["thumbnails"][0].get("src")
            if "aircraft" in res_data and res_data["aircraft"].get("livery"):
                fallback["livery_note"] = res_data["aircraft"]["livery"]
    except Exception:
        pass
    return fallback

def fetch_airport_radar_feed(airport_code, type="arrivals"):
    airport_code = airport_code.upper().strip()
    if airport_code in AIRPORT_DB:
        loc = AIRPORT_DB[airport_code]
        max_lat, min_lat = loc["lat"] + 1.6, loc["lat"] - 1.6
        min_lon, max_lon = loc["lon"] - 1.6, loc["lon"] + 1.6
    else:
        max_lat, min_lat, min_lon, max_lon = 23.8, 20.8, 112.4, 115.4
        airport_code = "HKG"

    url = f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?faa=1&bounds={max_lat},{min_lat},{min_lon},{max_lon}&satellite=1&mlat=1&adsb=1&gnd=0&air=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.flightradar24.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return []
        data = response.json()
        processed_traffic = []
        for flight_id, fields in data.items():
            if not isinstance(fields, list) or len(fields) < 18:
                continue
            origin, destination = fields[11], fields[12]
            if type.lower() == "arrivals" and destination != airport_code:
                continue
            if type.lower() == "departures" and origin != airport_code:
                continue
            reg = fields[9] if fields[9] else "N/A"
            aircraft_type = fields[8] if fields[8] else "N/A"
            flight_no = fields[13] if fields[13] else "Unknown"
            airline = fields[18] if fields[18] else "Unknown"

            processed_traffic.append({
                "flight_id": flight_id,
                "flight_no": flight_no,
                "airline": airline,
                "aircraft_code": aircraft_type,
                "reg": reg.upper().strip(),
                "est_time": datetime.now().strftime('%H:%M Live Track')
            })
        return processed_traffic
    except Exception:
        return []

def render_flight_card(f, status_text, bg_color, photo_url, spotting_date):
    if photo_url and str(photo_url).startswith("http"):
        media_html = f'<img src="{photo_url}" style="width:140px; height:93px; object-fit:cover; border-radius:6px; margin-right:15px; border: 1px solid rgba(255,255,255,0.1);" />'
    else:
        media_html = f'<div style="min-width:140px; max-width:140px; height:93px; background: rgba(255,255,255,0.03); border-radius:6px; margin-right:15px; display:flex; justify-content:center; align-items:center; border:1px dashed rgba(255,255,255,0.1);"><span style="color:#666; font-size:0.8em; font-weight:500;">No Photo</span></div>'
        
    html_card = f"""
<div style="background-color: {bg_color}; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center;">
{media_html}
<div>
<strong style="font-size: 1.1em; color: #FFF;">{f['flight_no']}</strong> ({f['airline']}) | <strong>Reg:</strong> <a href="https://www.jetphotos.com/registration/{f['reg']}" target="_blank" style="color: #3296FF; text-decoration: none; font-weight:bold;">{f['reg']}</a> | <strong>Type:</strong> {f['aircraft_code']}<br>
<span style="font-size: 0.9em; color: #aaa;">{status_text} — {f['est_time']} ({spotting_date.strftime('%Y-%m-%d')})</span>
</div>
</div>
"""
    st.markdown(html_card, unsafe_allow_html=True)

# --- MAIN APP LAYOUT ---
st.set_page_config(layout="wide", page_title="Aviation Custom Radar")
st.title("spotting thing")

special_liveries_db = load_liveries()

# --- SIDEBAR INTERFACE ---
st.sidebar.title("🛠️ Custom Fleet Management")
st.sidebar.success(f"📦 Database Operational: {len(special_liveries_db)} airframes actively loaded.")
st.sidebar.markdown("---")
traffic_filter = st.sidebar.radio("Show Traffic Selection:", ["All Movements", "Heavies / Watchlist / Specials Only"])

# --- CONTROLS ---
col1, col2 = st.columns([2, 1])
with col1:
    airport = st.text_input("Enter Airport Code (IATA):", "HKG").upper().strip()
with col2:
    spotting_date = st.date_input("Spotting Session Date:", datetime.today())

schedule_type = st.radio("Operation Focus", ["Arrivals", "Departures"])

if st.button("Scan Current Movements"):
    airport_name = AIRPORT_DB[airport]['name'] if airport in AIRPORT_DB else airport
    status_msg = st.empty()
    status_msg.info(f"🛰️ Syncing radar coverage loop for {airport_name} Airspace...")
    
    raw_flights = fetch_airport_radar_feed(airport, type=schedule_type.lower())

    if raw_flights:
        watchlist_hits, special_hits, heavy_hits, normal_hits = [], [], [], []
        
        with st.spinner("Filtering aircraft profiles against registry..."):
            for f in raw_flights:
                reg, aircraft_code, f_id = f["reg"], f["aircraft_code"], f["flight_id"]
                
                watchlist_desc = special_liveries_db.get(reg, None)
                is_heavy = aircraft_code in HEAVY_AND_RARE
                
                fr24_meta = get_jetphotos_data_via_fr24(f_id)
                f["photo_url"] = fr24_meta["thumbnail"]
                api_livery = fr24_meta["livery_note"]

                if watchlist_desc:
                    f["watchlist_desc"] = watchlist_desc
                    watchlist_hits.append(f)
                elif api_livery:
                    f["special_desc"] = api_livery
                    special_hits.append(f)
                elif is_heavy:
                    heavy_hits.append(f)
                else:
                    if traffic_filter == "All Movements":
                        normal_hits.append(f)
                        
        status_msg.empty()

        # Render Sectors
        st.subheader(f"🎨 specially cool plens({len(watchlist_hits) + len(special_hits)})")
        
        if watchlist_hits:
            for f in watchlist_hits:
                render_flight_card(f, f"🎯 MATCHED SPECIAL LIVERY: {f['watchlist_desc']}", "rgba(50, 150, 255, 0.12)", f["photo_url"], spotting_date)
                
        if special_hits:
            for f in special_hits:
                render_flight_card(f, f"🌈 FR24 AUTO-DETECT: {f['special_desc']}", "rgba(155, 89, 182, 0.12)", f["photo_url"], spotting_date)
                
        if not watchlist_hits and not special_hits:
            st.write("*No custom or special themed paint schemes currently inside this tracking sweep window.*")

        st.markdown("---")
        st.subheader(f"⭐ big plen ({len(heavy_hits)})")
        if heavy_hits:
            for f in heavy_hits:
                render_flight_card(f, f"✈️ Heavy Widebody ({f['aircraft_code']})", "rgba(255, 200, 0, 0.08)", f["photo_url"], spotting_date)
        else:
            st.write("*No heavy aircraft currently match this layout.*")

        if traffic_filter == "All Movements" and normal_hits:
            st.markdown("---")
            st.subheader(f"⚙️ boring plen ({len(normal_hits)})")
            for f in normal_hits:
                render_flight_card(f, "Standard Scheme Framework", "transparent", f["photo_url"], spotting_date)
    else:
        status_msg.empty()
        st.warning(f"No active flight movements located inside live vectors for {airport}.")
