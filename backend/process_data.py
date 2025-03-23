import sys
import json
from astropy.time import Time
from astropy.coordinates import EarthLocation, get_body, AltAz
from astropy import units as u
import pytz
from datetime import datetime
import numpy as np
import kundli_analyzer

# Zodiac signs (sidereal)
zodiac_signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Planet names
planet_names = {
    "sun": "Sun",
    "moon": "Moon",
    "mars": "Mars",
    "mercury": "Mercury",
    "jupiter": "Jupiter",
    "venus": "Venus",
    "saturn": "Saturn",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluto"
}

# Lahiri Ayanamsa for 2001 (~23.75°)
ayanamsa = 23.75

# Convert ecliptic longitude to sidereal zodiac
def to_sidereal_zodiac(longitude):
    sidereal_long = (longitude - ayanamsa) % 360
    sign_index = int(sidereal_long // 30)
    degrees = sidereal_long % 30
    return zodiac_signs[sign_index], degrees


# Calculate Kundli
def calculate_kundli(birth_date, birth_time, timezone, latitude, longitude):
    dt_local = datetime.strptime(f"{birth_date} {birth_time}", "%d %b %Y %H:%M:%S")
    local_tz = pytz.timezone(timezone)
    dt_local = local_tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.UTC)
    
    
    time = Time(dt_utc)
    location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg)
    
    kundli = {}
    for planet in planet_names:
        try:
            body = get_body(planet, time, location)
            ecliptic = body.geocentrictrueecliptic
            longitude = ecliptic.lon.deg
            sign, degrees = to_sidereal_zodiac(longitude)
            kundli[planet_names[planet]] = {"Sign": sign, "Degrees": degrees}
        except KeyError as e:
            if planet == "pluto":
                pluto_tropical = 248.5  # Static value for 2001-10-29
                sign, degrees = to_sidereal_zodiac(pluto_tropical)
                kundli["Pluto"] = {"Sign": sign, "Degrees": degrees}
            else:
                print(f"Error calculating {planet}: {e}")
    
    moon = get_body("moon", time, location)
    moon_ecliptic = moon.geocentrictrueecliptic
    moon_long = moon_ecliptic.lon.deg
    rahu_long = (moon_long + 180) % 360
    ketu_long = moon_long % 360
    rahu_sign, rahu_deg = to_sidereal_zodiac(rahu_long)
    ketu_sign, ketu_deg = to_sidereal_zodiac(ketu_long)
    kundli["Rahu"] = {"Sign": rahu_sign, "Degrees": rahu_deg}
    kundli["Ketu"] = {"Sign": ketu_sign, "Degrees": ketu_deg}
    
    altaz_frame = AltAz(obstime=time, location=location)
    lst = time.sidereal_time('mean', longitude * u.deg).deg
    asc_long = (lst + 90) % 360  # Simplified Ascendant
    asc_sign, asc_deg = to_sidereal_zodiac(asc_long)
    kundli["Ascendant"] = {"Sign": asc_sign, "Degrees": asc_deg}
    
    return kundli


# Display Kundli
def display_kundli(kundli):
    print("\n=== Kundli Chart ===")
    for planet, details in kundli.items():
        print(f"{planet}: {details['Sign']} {details['Degrees']:.2f}°")


def process_data(data):
    # Your birth details
    birth_date = data.get('date')
    birth_time = data.get('time')
    timezone = data.get('timezone')
    latitude = float(data.get('lat'))
    longitude = float(data.get('lng'))

    # Generate, display, and analyze Kundli
    kundli = calculate_kundli(birth_date, birth_time, timezone, latitude, longitude)

    # Pass to analyzer
    strongest, strong_desc, weakest, weak_desc, rarity_desc, guna_desc = kundli_analyzer.analyze_kundli(kundli)

    # Example processing: modify each parameter and add a processed flag
    processed_data = {
        "processed": True,
        "original_data": data,
        "Strongest Point" : f"{strongest}",
        "Good Line" : f"{strong_desc}",
        "Weakest Point" : f"{weakest}",
        "Bad Line" : f"{weak_desc}",
        "Rarity" : f"{rarity_desc}",
        "Guna" : f"{guna_desc}",
        "timestamp": "2025-03-23"  # Using a static date for demonstration
    }
    
    return processed_data

if __name__ == "__main__":
    # Read input from stdin (sent by Node.js)
    input_data = sys.stdin.read()
    
    try:
        # Parse the JSON input
        data = json.loads(input_data)
        
        # Process the data
        result = process_data(data)
        
        # Return the processed data as JSON
        print(json.dumps(result))
    except Exception as e:
        # Handle any errors
        error_response = {
            "error": str(e),
            "success": False
        }
        print(json.dumps(error_response))
        sys.exit(1)