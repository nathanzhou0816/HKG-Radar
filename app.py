import streamlit as st
import requests
import json
import os
import datetime

# ==============================================================================
# 1. GLOBAL PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="Aviation Custom Radar", 
    page_icon="✈️"
)

# ==============================================================================
# 2. MASTER LIVERY DICTIONARY (162 Strict Aircraft Records)
# ==============================================================================
SPECIAL_LIVERIES_DB = {
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

# ==============================================================================
# 3. STORAGE LIFECYCLE MANAGEMENT
# ==============================================================================
JSON_FILE = "saved_liveries.json"
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(SPECIAL_LIVERIES_DB, f, indent=4)

with open(JSON_FILE, "r", encoding="utf-8") as f:
    LIVE_LIVERIES_DATABASE = json.load(f)

# ==============================================================================
# 4. SIDEBAR TRAFFIC FILTER
# ==============================================================================
with st.sidebar:
    st.markdown("### 🛠️ Custom Fleet Management")
    st.success(f"Database Operational: {len(LIVE_LIVERIES_DATABASE)} airframes actively loaded.")
    
    st.markdown("---")
    traffic_view = st.radio(
        "Show Traffic Selection:",
        options=["All Movements", "Heavies / Watchlist / Specials Only"],
        index=0
    )

# ==============================================================================
# 5. CORE LAYOUT INPUT HUB
# ==============================================================================
st.title("✈️ Global Live Spotting Radar Dashboard")

col1, col2 = st.columns(2)
with col1:
    airport_code = st.text_input("Enter Airport Code (IATA):", value="HKG").upper().strip()
with col2:
    spotting_date = st.date_input("Spotting Session Date:", value=datetime.date.today())

operation_focus = st.radio("Operation Focus", options=["Arrivals", "Departures"], horizontal=True)

# ==============================================================================
# 6. PIPELINE RUNTIME SCRAPER
# ==============================================================================
if st.button("Scan Current Movements"):
    
    # Calculate exact unix timestamp parameters for the chosen date boundaries
    unix_timestamp = int(datetime.datetime.combine(spotting_date, datetime.time.min).timestamp())
    
    DATA_FEED_URL = (
        f"https://api.flightradar24.com/common/v1/airport.json"
        f"?code={airport_code.lower()}"
        f"&plugin[]="
        f"&plugin-setting[schedule][mode]={operation_focus.lower()}"
        f"&plugin-setting[schedule][timestamp]={unix_timestamp}"
        f"&page=1&limit=100"
    )
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(DATA_FEED_URL, headers=headers, timeout=12)
        raw_json = response.json()
        
        schedule_data = raw_json.get("result", {}).get("response", {}).get("airport", {}).get("pluginData", {}).get("schedule", {})
        active_flights = schedule_data.get("arrivals", {}).get("data", []) if operation_focus.lower() == "arrivals" else schedule_data.get("departures", {}).get("data", [])
        
    except Exception as e:
        st.error(f"Feed Connection Issue: {e}")
        active_flights = []

    # ==============================================================================
    # 7. MULTI-CATEGORY SORTING ENGINE
    # ==============================================================================
    specials_list = []
    heavies_list = []
    boring_list = []
    
    # Define heavy widebody frames
    HEAVY_TYPES = [
        "A332", "A333", "A343", "A346", "A359", "A35K", "A388", 
        "B772", "B773", "B77W", "B788", "B789", "B78X", "B744", "B748", "74F"
    ]

    for item in active_flights:
        f = item.get("flight", {})
        flight_no = f.get("identification", {}).get("number", {}).get("default", "N/A")
        
        aircraft_info = f.get("aircraft", {}) or {}
        reg = aircraft_info.get("registration", "UNKNOWN").upper()
        aircraft_code = aircraft_info.get("model", {}).get("code", "UNKN").upper()
        airline_name = f.get("airline", {}).get("name", "Unknown Operator")
        
        # Look up across our 162-item asset rules dictionary
        special_desc = LIVE_LIVERIES_DATABASE.get(reg, None)
        
        flight_object = {
            "flight_no": flight_no,
            "airline": airline_name,
            "reg": reg,
            "type": aircraft_code,
            "special_desc": special_desc
        }
        
        # Sort item directly into one of the three priority categories
        if special_desc:
            specials_list.append(flight_object)
        elif aircraft_code in HEAVY_TYPES:
            heavies_list.append(flight_object)
        else:
            if traffic_view == "All Movements":
                boring_list.append(flight_object)

    # ==============================================================================
    # 8. LAYOUT RENDERING VIEWS
    # ==============================================================================
    
    # Helper rendering block function to ensure strict design uniformity across sections
    def render_flight_cards(flights, category_title, emoji):
        st.markdown(f"## {emoji} {category_title} ({len(flights)})")
        if not flights:
            st.markdown("*No movements tracked inside this category matrix.*")
            st.markdown("---")
            return
            
        for fl in flights:
            with st.container():
                col_img, col_info = st.columns([1, 4])
                with col_img:
                    st.caption("📷 No Photo")
                with col_info:
                    st.markdown(f"### **{fl['flight_no']}** ({fl['airline']}) | Reg: `{fl['reg']}` | Type: **{fl['type']}**")
                    if fl['special_desc']:
                        st.markdown(f"🎨 **Special Livery Scheme Match:** `{fl['special_desc']}`")
                    elif fl['type'] in HEAVY_TYPES:
                        st.markdown(f"✈️ Heavy Widebody ({fl['type']})")
                    else:
                        st.markdown("🔹 *Standard Scheme Framework*")
                st.markdown("---")

    # Render out each distinct tracking lane block
    render_flight_cards(specials_list, "Special Schemes & Watchlist", "🎨")
    render_flight_cards(heavies_list, "Heavy Widebodies", "✈️")
    
    if traffic_view == "All Movements":
        render_flight_cards(boring_list, "boring plen", "⚙️")
