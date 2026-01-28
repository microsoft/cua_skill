# argument_value_generator.py
import random
from typing import Iterable, Optional, Sequence, Union, Dict, Any, Tuple

# Minimal, realistic seed dataset (city, state/region, country, iata?, coords?)
# (You can freely add more rows; function works the same.)
_LOCATIONS: Sequence[Dict[str, Any]] = [
    # --- USA ---
    {"city":"San Francisco","state":"CA","country":"USA","iata":"SFO","coords":(37.7749,-122.4194)},
    {"city":"New York","state":"NY","country":"USA","iata":"JFK","coords":(40.7128,-74.0060)},
    {"city":"Los Angeles","state":"CA","country":"USA","iata":"LAX","coords":(34.0522,-118.2437)},
    {"city":"Seattle","state":"WA","country":"USA","iata":"SEA","coords":(47.6062,-122.3321)},
    {"city":"Chicago","state":"IL","country":"USA","iata":"ORD","coords":(41.8781,-87.6298)},
    {"city":"Austin","state":"TX","country":"USA","iata":"AUS","coords":(30.2672,-97.7431)},
    {"city":"Miami","state":"FL","country":"USA","iata":"MIA","coords":(25.7617,-80.1918)},
    {"city":"Boston","state":"MA","country":"USA","iata":"BOS","coords":(42.3601,-71.0589)},

    # --- Canada ---
    {"city":"Toronto","state":"ON","country":"Canada","iata":"YYZ","coords":(43.6532,-79.3832)},
    {"city":"Vancouver","state":"BC","country":"Canada","iata":"YVR","coords":(49.2827,-123.1207)},

    # --- UK ---
    {"city":"London","state":"England","country":"UK","iata":"LHR","coords":(51.5072,-0.1276)},
    {"city":"Manchester","state":"England","country":"UK","iata":"MAN","coords":(53.4808,-2.2426)},

    # --- Germany ---
    {"city":"Berlin","state":"Berlin","country":"Germany","iata":"BER","coords":(52.5200,13.4050)},
    {"city":"Munich","state":"Bavaria","country":"Germany","iata":"MUC","coords":(48.1351,11.5820)},

    # --- France ---
    {"city":"Paris","state":"Île-de-France","country":"France","iata":"CDG","coords":(48.8566,2.3522)},

    # --- Japan ---
    {"city":"Tokyo","state":"Tokyo","country":"Japan","iata":"HND","coords":(35.6762,139.6503)},
    {"city":"Osaka","state":"Osaka","country":"Japan","iata":"KIX","coords":(34.6937,135.5023)},

    # --- Australia ---
    {"city":"Sydney","state":"NSW","country":"Australia","iata":"SYD","coords":( -33.8688,151.2093)},
    {"city":"Melbourne","state":"VIC","country":"Australia","iata":"MEL","coords":(-37.8136,144.9631)},

    # --- India ---
    {"city":"Mumbai","state":"Maharashtra","country":"India","iata":"BOM","coords":(19.0760,72.8777)},
    {"city":"Bengaluru","state":"Karnataka","country":"India","iata":"BLR","coords":(12.9716,77.5946)},

    # --- Brazil ---
    {"city":"São Paulo","state":"SP","country":"Brazil","iata":"GRU","coords":(-23.5505,-46.6333)},

    # --- Mexico ---
    {"city":"Mexico City","state":"CDMX","country":"Mexico","iata":"MEX","coords":(19.4326,-99.1332)},

    # --- City-state ---
    {"city":"Singapore","state":"Singapore","country":"Singapore","iata":"SIN","coords":(1.3521,103.8198)},
]

# A few UK postal formats to sample verbatim (for realism)
_UK_SAMPLES = ["SW1A 1AA", "EC1A 1BB", "W1A 0AX", "M1 1AE", "B33 8TH", "CR2 6XH", "DN55 1PT"]

# Helper for Canadian postal code (A1A 1A1) – letters exclude D F I O Q U in first part typically
_CAN_LETTERS = [c for c in "ABCEGHJKLMNPRSTVWXYZ"]
def _canada_postal(rng: random.Random) -> str:
    return f"{rng.choice(_CAN_LETTERS)}{rng.randint(0,9)}{rng.choice(_CAN_LETTERS)} {rng.randint(0,9)}{rng.choice(_CAN_LETTERS)}{rng.randint(0,9)}"

def _random_coords(rng: random.Random) -> Tuple[float, float]:
    # Reasonable lat/lon spread for inhabited areas
    lat = rng.uniform(-55.0, 70.0)
    lon = rng.uniform(-160.0, 160.0)
    return (round(lat, 6), round(lon, 6))

def _postal_for(country: str, rng: random.Random) -> str:
    c = country.lower()
    if c in ("usa","united states","us"):
        return f"{rng.randint(10001, 99998)}"
    if c in ("canada","ca"):
        return _canada_postal(rng)
    if c in ("uk","united kingdom","gb","great britain"):
        return rng.choice(_UK_SAMPLES)
    # Generic numeric postal for others
    return str(rng.randint(1000, 99950))

def generate_location(
    allowed_countries: Optional[Iterable[str]] = None,
    prefer_countries: Optional[Iterable[str]] = None,
    allowed_formats: Optional[Sequence[str]] = None,
    as_dict: bool = False,
    include_coords: bool = False,
    seed: Optional[int] = None,
) -> Union[str, Dict[str, Any]]:
    """
    Flexible location generator (not limited to 'city, state, country').

    Args:
        allowed_countries: restrict sampling to these (e.g., ["USA","UK"]).
        prefer_countries: bias sampling probability toward these.
        allowed_formats: any subset of:
            - "city_state_country"  -> "San Francisco, CA, USA"
            - "city_country"        -> "London, UK"
            - "city_only"           -> "Paris"
            - "state_country"       -> "NSW, Australia" / "CA, USA"
            - "country_only"        -> "Japan"
            - "coords"              -> "35.6762, 139.6503"
            - "coords_bbox"         -> {"lat":..,"lon":..,"radius_km":..}  (dict if as_dict=True, else "lat,lon (R=…km)")
            - "postal_country"      -> "94105, USA" / "SW1A 1AA, UK" / "M5V 3L9, Canada"
            - "iata_airport"        -> "LHR, London, UK"
            - "neighborhood_city"   -> "Brooklyn, New York" (synthetic; uses city for neighborhood-like output)
            - "address_like"        -> "123 Market St, San Francisco, CA"
        as_dict: if True, return a dict with fields & "format"; else return a display string.
        include_coords: when True, include coords in dict output when available (or random fallback).
        seed: RNG seed.

    Returns:
        str or dict describing a location in a chosen format.
    """
    rng = random.Random(seed)

    # 1) Filter & weight by country
    pool = list(_LOCATIONS)
    if allowed_countries:
        allowed = {c.lower() for c in allowed_countries}
        pool = [r for r in pool if r["country"].lower() in allowed] or list(_LOCATIONS)

    if prefer_countries:
        pref = {c.lower() for c in prefer_countries}
        weighted = []
        for rec in pool:
            weighted.extend([rec] * (3 if rec["country"].lower() in pref else 1))
        pool = weighted

    rec = rng.choice(pool)
    city, state, country = rec["city"], rec["state"], rec["country"]
    latlon = rec.get("coords") or _random_coords(rng)
    iata = rec.get("iata")

    # 2) Choose output format
    default_formats = [
        "city_state_country","city_country","city_only","state_country",
        "country_only","coords","postal_country","iata_airport","neighborhood_city","address_like"
    ]
    fmt = rng.choice(allowed_formats or default_formats)

    # 3) Render
    def as_output(text: str, extra: Dict[str, Any] = None) -> Union[str, Dict[str, Any]]:
        if not as_dict:
            return text
        data = {"format": fmt, "text": text, "city": city, "state": state, "country": country}
        if include_coords:
            data["lat"], data["lon"] = float(latlon[0]), float(latlon[1])
        if iata:
            data["iata"] = iata
        if extra:
            data.update(extra)
        return data

    if fmt == "city_state_country":
        return as_output(f"{city}, {state}, {country}")

    if fmt == "city_country":
        return as_output(f"{city}, {country}")

    if fmt == "city_only":
        return as_output(city)

    if fmt == "state_country":
        return as_output(f"{state}, {country}")

    if fmt == "country_only":
        return as_output(country)

    if fmt == "coords":
        return as_output(f"{latlon[0]}, {latlon[1]}")

    if fmt == "coords_bbox":
        radius = rng.choice([2, 5, 10, 15])
        if as_dict:
            return as_output(f"{latlon[0]}, {latlon[1]} (R≈{radius}km)", {"radius_km": radius})
        return as_output(f"{latlon[0]}, {latlon[1]} (R≈{radius}km)")

    if fmt == "postal_country":
        postal = _postal_for(country, rng)
        return as_output(f"{postal}, {country}", {"postal_code": postal} if as_dict else None)

    if fmt == "iata_airport":
        code = iata or rng.choice(["SFO","JFK","LAX","SEA","ORD","BOS","YYZ","YVR","LHR","CDG","BER","HND","SYD","MEL","BLR","BOM","GRU","MEX","SIN"])
        return as_output(f"{code}, {city}, {country}", {"iata": code} if as_dict else None)

    if fmt == "neighborhood_city":
        # Synthetic neighborhood prefixes
        hood = rng.choice(["Downtown","Old Town","Financial District","Soho","Midtown","West End","Brooklyn","South Bank","Harborfront"])
        return as_output(f"{hood}, {city}")

    if fmt == "address_like":
        num = rng.randint(10, 9999)
        street = rng.choice(["Market St","Main St","Broadway","Queen St","Oxford St","Elm St","Mission St","King St","1st Ave","Bay St"])
        return as_output(f"{num} {street}, {city}, {state}")

    # Fallback
    return as_output(f"{city}, {state}, {country}")
