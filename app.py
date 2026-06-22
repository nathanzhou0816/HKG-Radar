import streamlit as st
import requests
import json
import os
import datetime

# ==============================================================================
# 1. GLOBAL PAGE CONFIGURATION & STATE INITIALIZATION
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="for hkg use only currently", 
    page_icon="✈️"
)

if "active_flights" not in st.session_state:
    st.session_state.active_flights = []
if "scan_performed" not in st.session_state:
    st.session_state.scan_performed = False

# ==============================================================================
# 2. MASTER HEAVIES DATABASE MAP
# ==============================================================================
HEAVIES_DB = {
    "A332": "Airbus A330-200",
    "A333": "Airbus A330-300",
    "A339": "Airbus A330-900neo",
    "A343": "Airbus A340-300",
    "A346": "Airbus A340-600",
    "A359": "Airbus A350-900",
    "A35K": "Airbus A350-1000",
    "A388": "Airbus A380-800",
    "B772": "Boeing 777-200",
    "B773": "Boeing 777-300",
    "B77W": "Boeing 777-300ER",
    "B77F": "Boeing 777F",
    "B788": "Boeing 787-8 Dreamliner",
    "B789": "Boeing 787-9 Dreamliner",
    "B78X": "Boeing 787-10 Dreamliner",
    "B744": "Boeing 747-400",
    "B748": "Boeing 747-8i",
    "B74F": "Boeing 747 Freighter",
    "74F":  "Boeing 747 Freighter"
}

# ==============================================================================
# 3. SEED LIVERY DICTIONARY (Initial Built-in Special Liveries)
# ==============================================================================
SEED_LIVERIES_DB = {
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
    "B-2032": "Air China Boeing 777-300ER - Love China",
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
    "JA339J": "Japan Airlines Boeing 737-800 - Tokyo DisneySea - Sparkling Jubilee",

    # --- Cargolux ---
    "LX-VCC": "Cargolux Boeing 747-8i - 50th Anniversary Livery",
    "LX-NCL": "Cargolux Boeing 747-400 - Retro Livery",
    "LX-VCF": "Cargolux Boeing 747-8i - Not Without My Mask Livery",

    # --- Lufthansa ---
    "D-ABPU": "Lufthansa Boeing 787-9 - 100th Anniversary Livery",
    "D-ABYN": "Lufthansa Boeing 747-8i - 100th Anniversary Livery",
    "D-AIXL": "Lufthamsa Airbus A350-900 - 100th Anniversary Livery",
    "D-AIMH": "Lufthansa Airbus A380-800 - 100th Anniversary Livery",
    "D-ABYT": "Lufthansa Boeing 747-8i - Retro Livery",
    
    # --- DELTA AIR LINES ---
    "N845MH": "Delta Air Lines Boeing 767-400ER - Breast Cancer Research Foundation",
    "N3758Y": "Delta Air Lines Boeing 737-800 - SkyTeam",
    "N3761R": "Delta Air Lines Boeing 737-800 - SkyTeam",
    "N381DN": "Delta Air Lines Boeing 737-800 - SkyTeam",
    "N841MH": "Delta Air Lines Boeing 767-400ER - Relay For Life (sticker)",
    "N391DN": "Delta Air Lines Airbus A321 - Thank You / Employees\\' Names",
    "N502DN": "Delta Air Lines Airbus A350-900 - The Delta Spirit (sticker)",
    "N411DX": "Delta Air Lines Airbus A330-900neo - #TeamUSA Beijing Winter Olympics (sticker)",
    "N3746H": "Delta Air Lines Boeing 737-800 - World Series Champions 2021 (sticker)",
    "N521DN": "Delta Air Lines Airbus A350-900 - Team USA Olympic & Paralympic team",
    "N522DZ": "Delta Air Lines Airbus A350-900 - #LA28 Los Angeles Olympic Games 2028",
    "N6712B": "Delta Air Lines Boeing 757-200 - Atlanta - Where You Belong (sticker)",
    "N589DT": "Delta Air Lines Airbus A321neo - 100 Years",
    "N527DN": "Delta Air Lines Airbus A350-900 - 100 Years",
    "N191DN": "Delta Air Lines Boeing 767-300ER - Delta 100 Years (sticker)",
    "N694DL": "Delta Air Lines Boeing 757-200 - The Spirit of Freedom (sticker)",
    "N531DN": "Delta Air Lines Airbus A350-900 - Team USA Olympic & Paralympic team",
    "N553NW": "Delta Air Lines Boeing 757-200 - America250 (sticker)",

    # --- AIR CANADA & CANADIAN OPERATORS ---
    "C-GHLM": "Air Canada Airbus A330-300 - Star Alliance",
    "C-GMXB": "Sunwing Airlines Boeing 737 MAX 8 - Royalton Luxury Resorts",
    "C-FAXD": "Sunwing Airlines Boeing 737 MAX 8 - Planet Hollywood",
    "C-GEGI": "Air Canada Airbus A330-300 - Star Alliance",
    "C-GEGP": "Air Canada Airbus A330-300 - Star Alliance",
    "C-GNBN": "Air Canada Airbus A220-300 - Trans-Canada Air Lines (TCA) Retro",
    "C-FVGY": "Air North ATR 42-300F - Vuntut Gwitchin",
    "C-FBKB": "Kenn Borek Air Basler BT-67 - Celebrating 50 years: 1971-2021 (sticker)",
    "C-GOFV": "Air Canada Airbus A330-300 - Star Alliance",
    "C-GXZD": "Air Canada Airbus A330-300 - Star Alliance",
    "C-GEFA": "Air Canada Airbus A330-300 - Proudly contributing to climate research (sticker)",
    "C-FDFK": "Calm Air ATR 72-500 - Northern Lights",
    "C-FDHG": "Air Canada Airbus A330-300 - Star Alliance",
    "C-FDYL": "Harbour Air DHC-6 Twin Otter - Canadian Flag",
    "C-FLUJ": "Flair Airlines Boeing 737 MAX 8 - On-Time Guarantee (sticker)",
    "C-FSBV": "Air Canada Boeing 787-9 - 2025 Employee Excellence Awards Recipients",
    "C-GEGC": "Air Canada Airbus A330-300 - Fly The Flag / Canadian Olympic team",
    "C-GOKG": "Air Transat Airbus A321neo - CF Montreal football team",
    "C-GFOF": "Flair Airlines Boeing 737 MAX 8 - Canada\\'s Most Reliable Airline (sticker)",
    "C-FIVM": "Air Canada Boeing 777-300ER - 2026 Employee Excellence Awards recipients",

    # --- EMIRATES ---
    "A6-EEU": "Emirates Airbus A380-800 - Destination Dubai (was Dubai Expo2020)",
    "A6-EOT": "Emirates Airbus A380-800 - Destination Dubai (was Dubai Expo2020)",
    "A6-EES": "Emirates Airbus A380-800 - Destination Dubai (was Dubai Expo2020)",
    "A6-EEW": "Emirates Airbus A380-800 - Destination Dubai (was Dubai Expo2020)",
    "A6-EOD": "Emirates Airbus A380-800 - NBA Official Partner",
    "A6-EET": "Emirates Airbus A380-800 - Emirates Courier Express",
    "A6-EUE": "Emirates Airbus A380-800 - Emirates Skywards 25th Anniversary",
    "A6-EUH": "Emirates Airbus A380-800 - Proud Partner of Grand Slam Tennis",
    "A6-EVG": "Emirates Airbus A380-800 - This Flag Will Always Fly",
    "A6-EOE": "Emirates Airbus A380-800 - Arsenal Champions",

    # --- QATAR AIRWAYS ---
    "A7-AHL": "Qatar Airways Airbus A320 - oneworld",
    "A7-AHO": "Qatar Airways Airbus A320 - oneworld",
    "A7-BAA": "Qatar Airways Boeing 777-300ER - oneworld",
    "A7-BAB": "Qatar Airways Boeing 777-300ER - oneworld",
    "A7-BAF": "Qatar Airways Boeing 777-300ER - oneworld",
    "A7-BAG": "Qatar Airways Boeing 777-300ER - oneworld",
    "A7-ALZ": "Qatar Airways Airbus A350-900 - oneworld",
    "A7-ANE": "Qatar Airways Airbus A350-1000 - oneworld",
    "A7-AHG": "Qatar Airways Airbus A320 - 25 Years Of Excellence (sticker)",
    "A7-BEE": "Qatar Airways Boeing 777-300ER - 25 Years Of Excellence (sticker)",
    "A7-LAD": "Qatar Airways Airbus A320 - 25 Years Of Excellence (sticker)",
    "A7-BAC": "Qatar Airways Boeing 777-300ER - Retro",
    "A7-BBC": "Qatar Airways Boeing 777-200LR - 25 Years Of Excellence (sticker)",
    "A7-BOC": "Qatar Airways Boeing 777-300ER - Retro",
    "A7-BCZ": "Qatar Airways Boeing 787-8 - 25 Years Of Excellence (sticker)",
    "A7-BCX": "Qatar Airways Boeing 787-8 - 25 Years Of Excellence (sticker)",
    "A7-AHH": "Qatar Airways Airbus A320 - 25 Years Of Excellence (sticker)",
    "A7-BCW": "Qatar Airways Boeing 787-8 - 25 Years Of Excellence (sticker)",
    "A7-LAB": "Qatar Airways Airbus A320 - 25 Years Of Excellence (sticker)",
    "A7-LAC": "Qatar Airways Airbus A320 - 25 Years Of Excellence (sticker)",
    "A7-BFG": "Qatar Airways Cargo Boeing 777F - Moved by People",
    "A7-AHT": "Qatar Airways Airbus A320 - 25 Years Of Excellence (sticker)",
    "A7-BOI": "Qatar Airways Boeing 777-300ER - 25 Years Of Excellence (sticker)",
    "A7-BOH": "Qatar Airways Boeing 777-300ER - 25 Years Of Excellence (sticker)",
    "A7-BOG": "Qatar Airways Boeing 777-300ER - 25 Years Of Excellence (sticker)",
    "A7-BEL": "Qatar Airways Boeing 777-300ER - Official Global Airline Partner of Formula 1",
    "A7-BEK": "Qatar Airways Boeing 777-300ER - Paris St Germain football club (sticker)",
    "A7-BCY": "Qatar Airways Boeing 787-8 - 25 Years Of Excellence (sticker)",
    "A7-BDA": "Qatar Airways Boeing 787-8 - 25 Years Of Excellence (sticker)",
    "A7-BED": "Qatar Airways Boeing 777-300ER - UEFA Champions League",
    "A7-BEG": "Qatar Airways Boeing 777-300ER - Formula 1 Official Partner",
    "A7-BEH": "Qatar Airways Boeing 777-300ER - FIFA Official Airline of the Journey",

    # --- ETIHAD AIRWAYS ---
    "A6-BLV": "Etihad Airways Boeing 787-9 - Abu Dhabi Grand Prix 2021",
    "A6-BND": "Etihad Airways Boeing 787-9 - Manchester City Football Club",
    "A6-BMH": "Etihad Airways Boeing 787-10 - Greenliner",
    "A6-AEN": "Etihad Airways Airbus A321neo - 20 Years",
    "A6-BMA": "Etihad Airways Boeing 787-10 - Warner Bros. World Abu Dhabi",
    "A6-EJB": "Etihad Airways Airbus A320neo - Chennai Super Kings cricket team",

    # --- ATLAS AIR ---
    "N860GT": "Atlas Air Boeing 747-8F - 30th Anniversary (sticker)",
    "N862GT": "Atlas Air Boeing 747-8F - Inspire 747 / 30th Anniversary / Kuehne+Nagel (stickers)",
    "N863GT": "Atlas Air Boeing 747-8F - Joe Sutter - Forever Incredible / Apex Logistics (stickers)",
    "N664GT": "Atlas Air Boeing 767-300ER - 30th Anniversary (sticker)",
    "N641GT": "Atlas Air Boeing 767-300ER - 30th Anniversary (sticker)",
    "EP-SAJ": "Atlas Air Iran Antonov An-26B - Rasul Gamzatov (sticker)",
    "N485MC": "Atlas Air Boeing 747-400F - Flexport",
    "N486MC": "Atlas Air Boeing 747-400F - Apex Logistics (sticker)",
    "N419MC": "Atlas Air Boeing 747-400F - Apex Logistics (sticker)",
    "N704GT": "Atlas Air Boeing 777F - YunExpress (sticker)",
    "N861GT": "Atlas Air Boeing 747-8F - 30th Anniversary (sticker)",
    "N249BA": "Atlas Air Boeing 747-400LCF - Boeing Dreamlifter",
    "N718BA": "Atlas Air Boeing 747-400LCF - Boeing Dreamlifter",
    "N747BC": "Atlas Air Boeing 747-400LCF - Boeing Dreamlifter",
    "N780BA": "Atlas Air Boeing 747-400LCF - Boeing Dreamlifter",
    "N856GT": "Atlas Air Boeing 747-8F - In Memory Of Rogier Fetter (sticker)",
    "N640GT": "Atlas Air Boeing 767-300ER - America250 (sticker)",
    "N418MC": "Atlas Air Boeing 747-400F - America250 (sticker) (New June 2026)",
    "N481MC": "Atlas Air Boeing 747-400 - America250 (sticker) (New June 2026)",
    "N482MC": "Atlas Air Boeing 747-400 - America250 (sticker) (New June 2026)",

    # --- UPS AIRLINES ---
    "N616UP": "UPS Airlines Boeing 747-8F - 747 50th Anniversary (sticker)",
    "N633UP": "UPS Airlines Boeing 747-8F - Celebrating the Queen of the Skies (sticker)",

    # --- FEDEX EXPRESS ---
    "N277FE": "FedEx Express Boeing 767-300ER(F) - 100th Boeing 767 (sticker)",
    "N874FD": "FedEx Express Boeing 777F - FedEx 50th Boeing 777 (sticker)",
    "N870FD": "FedEx Express Boeing 777F - FedEx 50 (sticker, underside)",
    "N899FD": "FedEx Express Boeing 777F - FedEx founder F W Smith (sticker; underside/belly)",
    "N872FD": "FedEx Express Boeing 777F - FedEx founder F W Smith (sticker; underside/belly)",
    "N867FD": "FedEx Express Boeing 777F - FedEx founder F W Smith (sticker; underside/belly)",
    "N244FE": "FedEx Express Boeing 767-300F - 150th Boeing 767 FedEx (sticker)",

    # --- NATIONAL AIRLINES ---
    "N936CA": "National Airlines Boeing 747-400F - 30th Anniversary",

    # --- THAI AIRWAYS ---
    "HS-TOA": "Thai Airways Airbus A321neo - First A321neo (sticker)",
    "HS-TKQ": "Thai Airways Boeing 777-300ER - Star Alliance",
    "HS-TEO": "Thai Airways Airbus A330-300 - Star Alliance",

    # --- SINGAPORE AIRLINES & SCOOT ---
    "9V-SMF": "Singapore Airlines Airbus A350-900 - 10000th Airbus Aircraft (sticker)",
    "9V-SWI": "Singapore Airlines Boeing 777-300ER - Star Alliance (White)",
    "9V-SWJ": "Singapore Airlines Boeing 777-300ER - Star Alliance (White)",
    "9V-SWM": "Singapore Airlines Boeing 777-300ER - Star Alliance (White)",
    "9V-OJJ": "Scoot Boeing 787-9 - Pokemon",
    "9V-MBL": "Singapore Airlines Boeing 737 MAX 8 - Star Alliance (White)",
    "9V-SCP": "Singapore Airlines Boeing 787-10 - 1000th 787 Dreamliner (sticker)",

    # --- QANTAS & QANTAS FREIGHT / LINK ---
    "VH-XZJ": "Qantas Boeing 737-800 - Mendoowoorrji",
    "VH-EBV": "Qantas Airbus A330-200 - oneworld",
    "VH-XZP": "Qantas Boeing 737-800 - Qantas Retro",
    "VH-ZND": "Qantas Boeing 787-9 - Yam Dreaming",
    "VH-ZNJ": "Qantas Boeing 787-9 - 100 Years",
    "VH-EBL": "Qantas Airbus A330-200 - Pride is in the air / Sydney Mardi Gras",
    "VH-NJZ": "Qantas Freight BAe 146-300QT - StarTrack Partnership (sticker)",
    "VH-NJM": "Qantas Freight BAe 146-300QT - StarTrack Partnership (sticker)",
    "VH-NJF": "Qantas Freight BAe 146-300QT - StarTrack Partnership (sticker)",
    "VH-X4A": "QantasLink Airbus A220-300 - Minyma Kutjara Tjukurpa",
    "VH-EBN": "Qantas Airbus A330-200 - oneworld",
    "VH-EBS": "Qantas Airbus A330-200 - oneworld",
    "VH-VYK": "Qantas Boeing 737-800 - Pride Is In The Air / Sydney Mardi Gras",
    "VH-OGG": "Qantas Airbus A321XLR - Great Barrier Reef Foundation",

    # --- UNITED AIRLINES ---
    "N475UA": "United Airlines Airbus A320 - 85th Anniversary Retro",
    "N75435": "United Airlines Boeing 737-900 - Continental Airlines Retro",
    "N26210": "United Airlines Boeing 737-800 - Star Alliance",
    "N76516": "United Airlines Boeing 737-800 - Star Alliance",
    "N14120": "United Airlines Boeing 757-200 - Star Alliance",
    "N653UA": "United Airlines Boeing 767-300ER - Star Alliance",
    "N76055": "United Airlines Boeing 767-400ER - Star Alliance",
    "N218UA": "United Airlines Boeing 777-200ER - Star Alliance",
    "N76021": "United Airlines Boeing 777-200ER - Star Alliance",
    "N77022": "United Airlines Boeing 777-200ER - Star Alliance",
    "N794UA": "United Airlines Boeing 777-200ER - Star Alliance",
    "N14219": "United Airlines Boeing 737-800 - Star Alliance",
    "N27261": "United Airlines Boeing 737 MAX 8 - United Together / Being United",
    "N78017": "United Airlines Boeing 777-200ER - Star Alliance",
    "N27255": "United Airlines Boeing 737 MAX 8 - Aviate (sticker)",
    "N76522": "United Airlines Boeing 737-800 - Star Alliance",
    "N33284": "United Airlines Boeing 737-800 - Star Alliance",
    "N76523": "United Airlines Boeing 737-800 - Star Alliance",
    "N24988": "United Airlines Boeing 787-9 - The Future Is SAF",
    "N47345": "United Airlines Boeing 737 MAX 8 - ecoDemonstrator Explorer (sticker)",
    "N44550": "United Airlines Airbus A321neo - 100 Years (sticker)",
    "N61101": "United Airlines Boeing 787-9 - 100 Years (sticker)",
    "N78285": "United Airlines Boeing 737-800 - America250",
    "N91007": "United Airlines Boeing 787-10 - America250",

    # --- SOUTHWEST AIRLINES ---
    "N945WN": "Southwest Airlines Boeing 737-700 - Florida One",
    "N214WN": "Southwest Airlines Boeing 737-700 - Maryland One",
    "N280WN": "Southwest Airlines Boeing 737-700 - Missouri One",
    "N955WN": "Southwest Airlines Boeing 737-700 - Arizona One",
    "N906WN": "Southwest Airlines Boeing 737-700 - Charles E Taylor (America's First Mechanic) (sticker)",
    "N500WR": "Southwest Airlines Boeing 737-800 - Freedom One",
    "N8619F": "Southwest Airlines Boeing 737-800 - Illinois One",
    "N871HK": "Southwest Airlines Boeing 737 MAX 8 - Desert Gold Retro",
    "N872CB": "Southwest Airlines Boeing 737 MAX 8 - Canyon Blue Retro",
    "N8710M": "Southwest Airlines Boeing 737 MAX 8 - Imua One",
    "N8646B": "Southwest Airlines Boeing 737-800 - Nevada One",
    "N8655D": "Southwest Airlines Boeing 737-800 - New Mexico One",
    "N8653A": "Southwest Airlines Boeing 737-800 - California One",
    "N8660A": "Southwest Airlines Boeing 737-800 - Lone Star One",
    "N8681M": "Southwest Airlines Boeing 737-800 - Triple Crown One",
    "N938WN": "Southwest Airlines Boeing 737-700 - Heroes of the Heart Meteorology (sticker)",
    "N8977G": "Southwest Airlines Boeing 737 MAX 8 - Louisiana One",
    "N8690A": "Southwest Airlines Boeing 737-800 - Colorado One",
    "N8555Z": "Southwest Airlines Boeing 737-800 - Tennessee One",
    "N8719Q": "Southwest Airlines Boeing 737 MAX 8 - Liberty One",
    "N1776R": "Southwest Airlines Boeing 737 MAX 8 - America250 / Independence One"
}

# ==============================================================================
# 4. STORAGE PERSISTENCE ENGINE & DATA CORRUPTION AUTO-RECOVERY
# ==============================================================================
JSON_FILE = "saved_liveries.json"

if not os.path.exists(JSON_FILE):
    STORAGE_DATA = {"specials": SEED_LIVERIES_DB, "watchlist": {}}
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(STORAGE_DATA, f, indent=4)
else:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        try:
            STORAGE_DATA = json.load(f)
        except Exception:
            STORAGE_DATA = {"specials": SEED_LIVERIES_DB, "watchlist": {}}

# Corruption defense loop to fix old leaked schemas
if "watchlist" not in STORAGE_DATA or "B-5943" in STORAGE_DATA.get("watchlist", {}):
    STORAGE_DATA = {"specials": SEED_LIVERIES_DB, "watchlist": {}}
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(STORAGE_DATA, f, indent=4)

STORAGE_DATA["specials"] = SEED_LIVERIES_DB

WATCHLIST_DB = STORAGE_DATA.get("watchlist", {})
SPECIALS_DB = STORAGE_DATA.get("specials", {})

# ==============================================================================
# 5. SIDEBAR DESIGN
# ==============================================================================
with st.sidebar:
    st.markdown("### 🛠️ Custom Fleet Management")
    
    # --- FORM A: ADD TARGET ---
    st.markdown("#### ➕ Add Registration to Watchlist")
    with st.form("watchlist_form", clear_on_submit=True):
        new_reg = st.text_input("Registration (e.g., B-18055):").upper().strip()
        new_desc = st.text_input("Livery Notes (Optional):").strip()
        submitted = st.form_submit_button("Add to Watchlist")
        
        if submitted:
            if new_reg:
                # DYNAMIC LOOKUP ON CREATION:
                # Check if it exists in our core special liveries database first
                if not new_desc:
                    if new_reg in SEED_LIVERIES_DB:
                        final_desc = SEED_LIVERIES_DB[new_reg]
                    else:
                        final_desc = "Custom Watchlist Tracked Target"
                else:
                    final_desc = new_desc

                WATCHLIST_DB[new_reg] = final_desc
                STORAGE_DATA["watchlist"] = WATCHLIST_DB
                with open(JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump(STORAGE_DATA, f, indent=4)
                st.toast(f"🚨 {new_reg} added to Watchlist!", icon="🎯")
                st.rerun()
            else:
                st.error("Registration is required.")

    # --- FIXED FORM B: REMOVE TARGET ---
    if WATCHLIST_DB:
        st.markdown("#### ❌ Remove From Watchlist")
        with st.form("remove_form"):
            remove_selection = st.selectbox(
                "Select target to drop:",
                options=list(WATCHLIST_DB.keys())
            )
            remove_submitted = st.form_submit_button("Delete Registration")
            
            if remove_submitted:
                del WATCHLIST_DB[remove_selection]
                STORAGE_DATA["watchlist"] = WATCHLIST_DB
                with open(JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump(STORAGE_DATA, f, indent=4)
                st.toast(f"🗑️ {remove_selection} purged from radar memory.", icon="👋")
                st.rerun()

    # --- WATCHLIST LIVE READOUT ---
    st.markdown("#### 📋 Current Watchlist Active Targets")
    if WATCHLIST_DB:
        for r, d in WATCHLIST_DB.items():
            # SIDEBAR LIVE FALLBACK:
            # If the stored file has an old generic placeholder, fix it dynamically on screen
            display_desc = d
            if d == "Custom Watchlist Tracked Target" and r in SEED_LIVERIES_DB:
                display_desc = SEED_LIVERIES_DB[r]
                
            st.markdown(f"- **`{r}`**: *{display_desc}*")
    else:
        st.caption("No custom registrations tracked on sidebar watchlist.")

    st.markdown("---")
    traffic_view = st.radio(
        "Show Traffic Selection:",
        options=["All Movements", "Watchlist / Heavies / Specials Only"],
        index=0
    )
# ==============================================================================
# 6. CORE LAYOUT INPUT HUB
# ==============================================================================
st.title("✈️ for hkg use only currently")

col1, col2 = st.columns(2)
with col1:
    airport_code = st.text_input("Enter Airport Code (IATA):", value="HKG").upper().strip()
with col2:
    spotting_date = st.date_input("Spotting Session Date:", value=datetime.date.today())

operation_focus = st.radio("Operation Focus", options=["Arrivals", "Departures"], horizontal=True)

# ==============================================================================
# 7. PIPELINE RUNTIME SCRAPER
# ==============================================================================
if st.button("Scan Current Movements"):
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
        if schedule_data:
            st.session_state.active_flights = schedule_data.get("arrivals", {}).get("data", []) if operation_focus.lower() == "arrivals" else schedule_data.get("departures", {}).get("data", [])
            st.session_state.scan_performed = True
        else:
            st.session_state.active_flights = []
            st.session_state.scan_performed = True
            st.warning("No flight data returned from API.")
        
    except Exception as e:
        st.error(f"Feed Connection Issue: {e}")
        st.session_state.active_flights = []
        st.session_state.scan_performed = True

# ==============================================================================
    # 8. STRUCTURAL SORTING LAYER
    # ==============================================================================
    watchlist_matches = []
    specials_list = []
    heavies_list = []
    boring_list = []

    for item in st.session_state.active_flights:
        if not item:
            continue
        f = item.get("flight", {}) or {}
        
        flight_no = f.get("identification", {}).get("number", {}).get("default", "N/A")
        aircraft_info = f.get("aircraft", {}) or {}
        reg = aircraft_info.get("registration", "UNKNOWN").upper()
        aircraft_code = aircraft_info.get("model", {}).get("code", "UNKN").upper()
        
        airline_dict = f.get("airline", {}) or {}
        airline_name = airline_dict.get("name", "Unknown Operator")
        
        watchlist_desc = WATCHLIST_DB.get(reg, None)
        special_desc = SPECIALS_DB.get(reg, None)
        heavy_desc = HEAVIES_DB.get(aircraft_code, None)
        
        # --- DYNAMIC WATCHLIST DETAIL RESOLUTION ---
        # If a custom target was added without explicit notes, look up its real 
        # details in the specials or heavies database rather than showing the default fallback.
        if watchlist_desc == "Custom Watchlist Tracked Target":
            if special_desc:
                watchlist_desc = special_desc
            elif heavy_desc:
                watchlist_desc = f"{airline_name} {heavy_desc}"
            else:
                watchlist_desc = f"{airline_name} ({aircraft_code})"
        
        flight_object = {
            "flight_no": flight_no,
            "airline": airline_name,
            "reg": reg,
            "type": aircraft_code,
            "watchlist_desc": watchlist_desc,
            "special_desc": special_desc,
            "heavy_desc": heavy_desc
        }
        
        if WATCHLIST_DB.get(reg, None) is not None:
            watchlist_matches.append(flight_object)
        elif special_desc:
            specials_list.append(flight_object)
        elif heavy_desc:
            heavies_list.append(flight_object)
        else:
            if traffic_view == "All Movements":
                boring_list.append(flight_object)

    # ==============================================================================
    # 9. MAIN OUTPUT LANE RENDERER
    # ==============================================================================
    def render_flight_cards(flights, category_title, emoji, alert_type="info"):
        st.markdown(f"## {emoji} {category_title} ({len(flights)})")
        if not flights:
            st.markdown("*No movements tracked inside this category lane.*")
            return
            
        for fl in flights:
            card_text = f"**{fl['flight_no']}** ({fl['airline']}) | Reg: **{fl['reg']}** | Type: **{fl['type']}**"
            
            if alert_type == "error":
                card_text += f"\n\n🚨 **WATCHLIST TARGET FOUND:** `{fl['watchlist_desc']}`"
                st.error(card_text)
            elif alert_type == "info":
                card_text += f"\n\n🎨 **SPECIALLY COOL LIVERY MATCH:** `{fl['special_desc']}`"
                st.info(card_text)
            elif alert_type == "success":
                card_text += f"\n\n✈️ **Heavy Widebody:** `{fl['heavy_desc']}`"
                st.success(card_text)
            else:
                card_text += f"\n\n🔹 *Regular Traffic*"
                st.warning(card_text)

    # Render display blocks in sorted order
    render_flight_cards(watchlist_matches, "watchlist plens", "🚨", alert_type="error")
    render_flight_cards(specials_list, "specially cool plens", "🎨", alert_type="info")
    render_flight_cards(heavies_list, "big plen", "⭐", alert_type="success")
    
    if traffic_view == "All Movements":
        render_flight_cards(boring_list, "boring plen", "⚙️", alert_type="warning")
