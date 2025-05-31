from venv import logger
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random
import math
from math import cos, sin, atan2, sqrt, radians, degrees, asin
import datetime
import logging
from typing import Dict, List, NamedTuple
import logging
from fuzzywuzzy import fuzz

from geographiclib.geodesic import Geodesic
import scipy.optimize as optimize
from cal_func import calculate_geodesic
import firebase_admin
from firebase_admin import credentials, firestore
# Import these libraries if available in your environment
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "airplane-49087",
    "private_key_id": "84e969bd2c76953bb01f12cea7c94c37b338dcc6",
    "private_key": """-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCdsdQ2iNJsEzH6\nzzK7pLYaTn/u1cTla1RUkCda9AOQdA7DPN7Opyht4m40t7RRrJYozj8Ky4HStfv3\n5dOaL4356P0qIqbMjV34RYZtEe5jyHWosXPQNGaV+pBlL+fuSVSeDFEuYeqiAjqK\n4XkVBpkagpoDKRLHIGRNoAnqKY8X7iD2B/lNvEaQo0F9io/f5lvwJuZQAAA5kPK9\nK4+re0wcZGgbkpdCfmGULvMBfE+i+ExjkuIfX9nh0wIjP5zy//dHl+5tDvl0iOew\n5RcXsAzOGR0UwNohF7cNruBAGpW08OpkTkW658NQwS0mxGy5mn3tMz5DiIihl1y0\nNYdOfW//AgMBAAECggEAHTeaAIKoLgL+cyBZn3+ch9I8jNVJllIk/Uf6KrVkRarj\nI1RPWc2JxZY64gSZYbqO1b+k2YysIIy8Qwlvg7VE4mVDJr/l1KdqnjnPdrzoRM+a\n0ScTtKNI0IfsofrWx4UJqwDQN75HmT29eAbfhsBCtLE29Nfy1TcQrns06xBJJV8c\nd6dt2rfvWgXc4tHmPaiAQtL1RXIUx64jTxvY2OlCASxpzqhxJe100eU0DAq5BQpi\nj6FwvO/OsiMfaZMsYYs5Hoh8IhIbnRXdGQnCYMUsGIEl1rLf3G7n01xLfYXlto0Q\nzXZ+H1vEf7pNRRWmXsLvZF65Xj3kJPmYRg7knvZBQQKBgQDQA8Oynh2iLxldogZ2\nr0rciC8RBaV9iSU7T4H0Zf7fZ7YoZEh95TUXeqPB/eSiQrddkLyOuRnJ4SrrCo0E\nm4ZWN58kwAahX1LlGBY5fKNZlzWbG0R4G8v39CwPYfXlFGtna3F5w2FfIQ4HyPQx\nysMBjiaaz/PoZUQ9+5Ed+dDVvwKBgQDCEm5TcCdighYSmulpTdAR3Nj0hC/wcQwN\ngUQyx12PmXxAQzuj50L4Slmt54Z+SssOTNV0H3R8AwWPf0Zoowt6S8LNJJQZZiuJ\n4LxTL03UBAq/FjesFteCtmBWfCQ4nQFd2t2gsn23/cIoNw3V6nCDaseTgMCAgjL7\n+9ydaKR1wQKBgQCTPFbksy5egd/+epUApQrkFjDaZ5i/xrdnx9tAVoGVOB+jb3gw\nRHDT8aa/xSpz/60yuSP+Ed7DGnH6dDlkrYDkvfITXShUSNiv9+CjSCmHXJRA+Yf5\nTBOPqnEVYk1enJl5Vn+3pCfj4c3AjOjr5Y0qKKgCpHcMY8Ft7gbFpPHAmQKBgQCL\nixsfDa6UCzt5xz97w0KQBX9OWdnqhi6Ha2IxLN7eSRtpTa6NjNS/mR5gh/BR0M+u\niZqVs6RbIwUViAuFY272UZFRVjLTDH7T1e8z1PieMQXVHlGLgKUXTLF6niqhNmts\nI9pmGNGCwYigx+0/2iFqrRWxvssr2/Jy80dPO5W9QQKBgHxVkgeNeD8B9GOFH3mA\nMn05bNqKWFiJU2kBp4rTnzUy+0DiT15NL8SEGyHKRno0Mcm6//DdBTJexomccVvt\nYdVz6J3t67GQCD+FnCZSZvubaygog8/PSNdizRQrIHuLX11Urj9q4BeLA6vuYVRy\npY+B7jrN1sp81hvYQRsDKLbm\n-----END PRIVATE KEY-----\n""",  # ✅ Use triple quotes for multi-line strings
    "client_email": "firebase-adminsdk-fbsvc@airplane-49087.iam.gserviceaccount.com",
    "client_id": "107082013090178902883",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40airplane-49087.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})

# 🔹 Step 2: Initialize Firebase App
firebase_admin.initialize_app(cred)

# 🔹 Step 3: Now safely use Firestore
db = firestore.client()
print("✅ Firebase & Firestore initialized successfully!")
try:
    from pygeomag import GeoMag
    geo = GeoMag()
    has_pygeomag = True
except ImportError:
    has_pygeomag = False
    logging.warning("pygeomag library not found. Magnetic variation calculations will be disabled.")

from allclass import *
from sample_airport import *

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:5000"]}})

# ---- Adding wind effect and ground speed calculation functions from first code ----
class Navigation:
    def get_track_angle(self, dep, arr, magnetic=True, date=None):
        # Validate inputs
        if not (-90 <= dep.lat <= 90 and -180 <= dep.long <= 180 and 
                -90 <= arr.lat <= 90 and -180 <= arr.long <= 180):
            raise ValueError("Invalid latitude or longitude")
        if (dep.lat, dep.long) == (arr.lat, arr.long):
            return 0.0

        # Calculate true bearing using great-circle formula
        lat1 = math.radians(dep.lat)
        lon1 = math.radians(dep.long)
        lat2 = math.radians(arr.lat)
        lon2 = math.radians(arr.long)
        
        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        true_bearing = math.degrees(math.atan2(y, x))
        true_bearing = (true_bearing + 360) % 360
        
        if not magnetic:
            return round(true_bearing, 2)
        
        # Convert to magnetic bearing
        magnetic_variation = self.get_magnetic_variation(dep.lat, dep.long, date)
        magnetic_bearing = (true_bearing - magnetic_variation + 360) % 360
        
        return round(magnetic_bearing, 2)

    def get_magnetic_variation(self, lat, lon, date=None):
        if geo is None:
            print("GeoMag unavailable. Using fallback magnetic variation (-12.0 for New York).")
            return -12.0  # Fallback for New York, 2023
        try:
            date = date or datetime.datetime.utcnow()
            dec_year = self.decimal_year(date)
            result = geo.calculate(glat=lat, glon=lon, alt=0, time=dec_year)
            return float(result.dec)
        except Exception as e:
            print(f"Error calculating magnetic variation: {e}")
            return -12.0  # Fallback for New York

    def decimal_year(self, date):
        """Convert a datetime object to decimal year."""
        year_start = datetime.datetime(date.year, 1, 1)
        year_end = datetime.datetime(date.year + 1, 1, 1)
        year_length = (year_end - year_start).total_seconds()
        seconds_into_year = (date - year_start).total_seconds()
        return date.year + seconds_into_year / year_length

    def get_midpoint(self, dep, arr):
        """Calculate the geographic midpoint between two points."""
        # Convert to radians
        lat1 = math.radians(dep.lat)
        lon1 = math.radians(dep.long)
        lat2 = math.radians(arr.lat)
        lon2 = math.radians(arr.long)
        
        # Convert to Cartesian coordinates
        x1 = math.cos(lat1) * math.cos(lon1)
        y1 = math.cos(lat1) * math.sin(lon1)
        z1 = math.sin(lat1)
        x2 = math.cos(lat2) * math.cos(lon2)
        y2 = math.cos(lat2) * math.sin(lon2)
        z2 = math.sin(lat2)
        
        # Average coordinates
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        z = (z1 + z2) / 2
        
        # Convert back to lat/long
        lon = math.atan2(y, x)
        hyp = math.sqrt(x * x + y * y)
        lat = math.atan2(z, hyp)
        
        # Convert to degrees
        mid_lat = math.degrees(lat)
        mid_lon = math.degrees(lon)
        
        return Point(round(mid_lat, 4), round(mid_lon, 4))

    def get_route_magnitude(self, dep, arr, unit='km'):
        """Calculate great-circle distance between two points."""
        # Earth's radius (km)
        R = 6371.0  # Use 3440.1 for nautical miles, 3958.8 for statute miles
        
        lat1 = math.radians(dep.lat)
        lon1 = math.radians(dep.long)
        lat2 = math.radians(arr.lat)
        lon2 = math.radians(arr.long)
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        if unit == 'nm':
            distance *= 0.539957  # Convert km to nautical miles
        elif unit == 'mi':
            distance *= 0.621371  # Convert km to statute miles
            
        return round(distance, 2)

def decimal_year(date: datetime.datetime) -> float:
    """Calculate decimal year from datetime object."""
    year_start = datetime.datetime(date.year, 1, 1)
    next_year_start = datetime.datetime(date.year + 1, 1, 1)
    year_length = (next_year_start - year_start).total_seconds()
    elapsed = (date - year_start).total_seconds()
    return date.year + elapsed / year_length


import random
def find_airport_by_name(name, reference, airports):
    """
    Find airport in airports list by matching either name or reference (case insensitive partial match).
    
    Parameters:
        name (str): Partial or full airport name to search.
        reference (str): Additional reference string to match.
        airports (list): List of airport objects (assumed to have a 'name' attribute).

    Returns:
        Airport object if a match is found, else None.
    """
    name_lower = name.lower()
    reference_lower = reference.lower()

    for airport in airports:
        airport_name_lower = airport.name.lower()
        if name_lower in airport_name_lower and reference_lower in airport_name_lower:
            return airport  # Return the first matched Airport object
    return None

def find_airport_by_name(name, reference, airports):
    """
    Find airport in airports list by matching either name or reference with improved accuracy.
         
    Parameters:
        name (str): Partial or full airport name to search.
        reference (str|list): Additional reference string(s) to match (L1, L2, etc.).
        airports (list): List of Airport objects with code, name, lat, long, reference attributes.
     
    Returns:
        Airport object if a match is found, else None.
    """
    if not name or not airports:
        logger.debug("Invalid input: name or airports list is empty")
        return None
    
    # Normalize name for comparison
    name_lower = name.lower().strip()
    name_upper = name.upper().strip()
    
    # Handle reference parameter (normalize to uppercase)
    reference_list = []
    if isinstance(reference, list):
        reference_list = [ref.upper().strip() for ref in reference if isinstance(ref, str) and ref.strip()]
    elif isinstance(reference, str) and reference.strip():
        reference_list = [reference.upper().strip()]
    
    # List to store potential matches with scores
    candidates = []
    
    for airport in airports:
        score = 0
        details = {"airport": airport, "match_type": []}
        
        # Normalize airport attributes
        airport_name_clean = airport.name.lower().strip()
        airport_code_lower = airport.code.lower().strip()
        airport_reference = airport.reference.upper().strip() if airport.reference else ""
        
        # Priority 1: Exact name match
        if name_lower == airport_name_clean:
            score += 100
            details["match_type"].append("exact_name")
        
        # Priority 2: Exact airport code match
        if name_upper == airport.code:
            score += 95
            details["match_type"].append("exact_code")
        
        # Priority 3: Exact reference match
        if reference_list and airport_reference in reference_list:
            score += 90
            details["match_type"].append("exact_reference")
        
        # Priority 4: Name starts with search term
        if airport_name_clean.startswith(name_lower):
            score += 85
            details["match_type"].append("name_starts_with")
        
        # Priority 5: Airport code starts with search term
        if airport_code_lower.startswith(name_lower):
            score += 80
            details["match_type"].append("code_starts_with")
        
        # Priority 6: Fuzzy matching for name
        fuzzy_score = fuzz.ratio(name_lower, airport_name_clean)
        if fuzzy_score >= 80:
            score += fuzzy_score * 0.75
            details["match_type"].append(f"fuzzy_name (score: {fuzzy_score})")
        
        # Priority 7: Name contains all words from search term
        name_words = name_lower.split()
        if len(name_words) > 1 and all(word in airport_name_clean for word in name_words):
            score += 70
            details["match_type"].append("contains_all_words")
        
        # Priority 8: Partial name match
        if name_lower in airport_name_clean:
            score += 65
            details["match_type"].append("partial_name")
        
        # Priority 9: Partial code match
        if name_lower in airport_code_lower or airport_code_lower in name_lower:
            score += 60
            details["match_type"].append("partial_code")
        
        # Priority 10: Reference partial match in name
        if reference_list:
            for ref in reference_list:
                if ref.lower() in airport_name_clean:
                    score += 55
                    details["match_type"].append(f"reference_in_name ({ref})")
        
        # Priority 11: Cross-reference matching
        if reference_list:
            for ref in reference_list:
                if ref.lower() in airport_name_clean:
                    score += 50
                    details["match_type"].append(f"reference_matches_name ({ref})")
                if name_upper == airport_reference:
                    score += 50
                    details["match_type"].append("name_matches_reference")
        
        if score > 0:
            details["score"] = score
            candidates.append(details)
        
        if details["match_type"]:
            logger.debug(f"Airport: {airport.name} ({airport.code}), Score: {score}, Match Types: {details['match_type']}")
    
    if candidates:
        best_candidate = max(candidates, key=lambda x: x["score"])
        logger.debug(f"Best match: {best_candidate['airport'].name} ({best_candidate['airport'].code}), Score: {best_candidate['score']}, Match Types: {best_candidate['match_type']}")
        return best_candidate["airport"]
    
    logger.debug("No match found")
    return None

def get_track_angle(self, dep, arr, magnetic=True):
    # Calculate true bearing using great-circle formula
        lat1 = math.radians(dep.lat)
        lon1 = math.radians(dep.long)
        lat2 = math.radians(arr.lat)
        lon2 = math.radians(arr.long)
        
        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        true_bearing = math.degrees(math.atan2(y, x))
        true_bearing = (true_bearing + 360) % 360
        
        if not magnetic:
            return true_bearing
        
        # Convert true bearing to magnetic bearing using your existing function
        magnetic_variation = self.get_magnetic_variation(dep.lat, dep.long)
        magnetic_bearing = (true_bearing + magnetic_variation) % 360
        
        return magnetic_bearing

def get_magnetic_variation( lat, lon, date=None):
        date = date or datetime.datetime.utcnow()
        dec_year = decimal_year(date)
        result = geo.calculate(glat=lat, glon=lon, alt=0, time=dec_year)
        return result.d
PREDEFINED_2_MARK_QUESTIONS = [
    {
        "text_template": "Q1.Refer to ERC {reference}.\n\nYou are planning a flight from {dep_name_text} to {arr_name_text} on {track_name}. TAS is {tas} and W/V {wind_dir_display}M/{wind_speed} kt\n.The question asks for the position of the Critical Point (CP) between {etp_dest1_name_text} and {etp_dest2_name_text} along the {dep_name_text} to {arr_name_text} track ,  as a distance from {dep_name_text}, is closest to -",
        "dep_name_text": "Launceston",
        "arr_name_text": "East sale",
        "track_name": "W-218",
        "etp_dest1_name_text": "East sale",
        "etp_dest2_name_text": "Latrobe Valley",
        "reference": "L1",
    },
    {
        "text_template": "Q2.Refer to ERC {reference}.\n\nYou are planning a flight from {dep_name_text} to {arr_name_text} on {track_name}. TAS is {tas} and W/V {wind_dir_display}M/{wind_speed} kt\n.The question asks for the position of the Critical Point (CP) between {etp_dest1_name_text} and {etp_dest2_name_text} along the {dep_name_text} to {arr_name_text} track ,  as a distance from {dep_name_text}, is closest to -",
        "reference": "L2",
        "dep_name_text": "Griffith",
        "arr_name_text": "Mildura",
        "track_name": "W-415",
        "etp_dest1_name_text": "Mildura",
        "etp_dest2_name_text": "Swan Hill",
    },
    {
        "text_template": "Q3.Refer to ERC {reference}.\n\nYou are planning a flight from {dep_name_text} to {arr_name_text} on {track_name}. TAS is {tas} and W/V {wind_dir_display}M/{wind_speed} kt\n.The question asks for the position of the Critical Point (CP) between {etp_dest1_name_text} and {etp_dest2_name_text} along the {dep_name_text} to {arr_name_text} track ,  as a distance from {dep_name_text}, is closest to -",
        "dep_name_text": "Grafton",
        "arr_name_text": "Inverell",
        "track_name": "W-623",
        "etp_dest1_name_text": "Inverell",
        "etp_dest2_name_text": "Armidale",
        "reference": "L2",
    },
    {
        "text_template": "Q4.Refer to ERC {reference}.\n\nYou are planning a flight from {dep_name_text} to {arr_name_text} on {track_name}.  TAS is {tas} and W/V {wind_dir_display}M/{wind_speed} kt\n.The question asks for the position of the Critical Point (CP) between {etp_dest1_name_text} and {etp_dest2_name_text} along the {dep_name_text} to {arr_name_text} track ,  as a distance from {dep_name_text}, is closest to -",
        "dep_name_text": "Emerald",
        "arr_name_text": "Charleville",
        "track_name": "W-806",
        "etp_dest1_name_text": "Charleville",
        "etp_dest2_name_text": "Roma",
        "reference": "L4",
    }
]
# Initialize generator
generator = AirportQuestionGenerator(sample_airports)
def find(name,airports):
    """Find airport in airports_list by name (case insensitive partial match)"""
    name_lower = name.lower()
    for airport in airports:
        if name_lower in airport.name.lower():
            return airport  # Return the Airport object directly
    return None
# Modify calculate_geodesic function to include ground speed calculations
@app.route('/generate_question', methods=['POST'])
def generate_question_endpoint():
    try:
        # Parse the JSON request data
        data = request.get_json()
        if not data or 'reference' not in data or 'num_airports' not in data or 'marks' not in data:
            return jsonify({'error': 'Missing required parameters: reference, num_airports, and marks are required'}), 400
        
        # Extract parameters
        reference = data['reference']
        num_airports = int(data['num_airports'])
        marks = int(data['marks'])
        show_map = data.get('show_map', False)  # New parameter for map display

        # Validate reference
        if not reference.startswith('L') or not reference[1:].isdigit() or int(reference[1:]) < 1 or int(reference[1:]) > 8:
            return jsonify({'error': 'Invalid reference format. Must be L1 through L8'}), 400
        
        # Validate num_airports
        if num_airports not in [3, 4]:
            return jsonify({'error': 'Number of airports must be 3 or 4'}), 400
        
        # Validate marks
        if marks not in [2, 3]:
            return jsonify({'error': 'Marks must be 2 or 3'}), 400

        # For 2-mark questions, use predefined questions
        if marks == 2:
            # Select a random predefined question
            predefined_question = random.choice(PREDEFINED_2_MARK_QUESTIONS)
            
            # Find airports in sample_airports
            dep = find(predefined_question['dep_name_text'], sample_airports)
            arr = find(predefined_question['arr_name_text'], sample_airports)
            land1 = find(predefined_question['etp_dest1_name_text'], sample_airports)
            land2 = find(predefined_question['etp_dest2_name_text'], sample_airports)
            
            if not all([dep, arr, land1, land2]):
                return jsonify({'error': 'Could not find all airports in sample data'}), 400
            
            def generate_three_digit_multiple_of_10():
                # Three-digit numbers range from 100 to 999
                # We need multiples of 10 that are less than 360
                # So we need numbers from 100 to 350
                # We can generate a random number between 10 and 35 and multiply by 10
                base_number = random.randint(10, 35)
                return base_number * 10

            # Generate random wind and TAS values
            wind_dir = generate_three_digit_multiple_of_10()
            
            def generate_wind_strength():
                # Find how many multiples of 5 are less than 90
                # 5, 10, 15, ..., 85 (17 values)
                num_multiples = 90 // 5
                # Generate a random index between 0 and num_multiples-1
                random_index = random.randint(0, num_multiples - 1)
                # Return the corresponding multiple of 5
                return (random_index + 1) * 5
            
            wind_speed = generate_wind_strength()
            
            def random_multiple_of_5(min_value, max_value):
                # Find the first multiple of 5 >= min_value
                lower_bound = min_value if min_value % 5 == 0 else min_value + (5 - min_value % 5)
        
                # Find the last multiple of 5 <= max_value
                upper_bound = max_value if max_value % 5 == 0 else max_value - (max_value % 5)
        
                # Calculate how many multiples of 5 are in the range
                num_multiples = (upper_bound - lower_bound) // 5 + 1
        
                # Generate a random index and calculate the corresponding multiple of 5
                random_index = random.randint(0, num_multiples - 1)
                result = lower_bound + random_index * 5
        
                return result
            
            tas = random_multiple_of_5(100, 300)
            # Format wind direction for display (e.g., "270M")
            wind_dir_display = f"{wind_dir:03d}M"
            
            # Format the question text
            question_text = predefined_question['text_template'].format(
                dep_name_text=predefined_question['dep_name_text'],
                arr_name_text=predefined_question['arr_name_text'],
                track_name=predefined_question['track_name'],
                etp_dest1_name_text=predefined_question['etp_dest1_name_text'],
                etp_dest2_name_text=predefined_question['etp_dest2_name_text'],
                wind_dir_display=wind_dir_display,
                wind_speed=wind_speed,
                tas=tas,
                reference=predefined_question['reference'],
            )
            
            dep1 = find_airport_by_name(dep.name, reference, airports)
            arr1 = find_airport_by_name(arr.name, reference, airports)
            land1_map = find_airport_by_name(land1.name, reference, airports)
            land2_map = find_airport_by_name(land2.name, reference, airports)
            
            # Calculate geodesic data
            P1 = (dep.lat, dep.long)
            P2 = (arr.lat, arr.long)
            P3 = (land1.lat, land1.long)
            P4 = (land2.lat, land2.long)
            P5 = (dep1.lat, dep1.long)
            P6 = (arr1.lat, arr1.long)
            P7 = (land1_map.lat, land1_map.long)
            P8 = (land2_map.lat, land2_map.long)
            reference = predefined_question['reference']
           
            geodesic_results = calculate_geodesic1(P1, P2, P3, P4, tas, wind_speed, wind_dir)
            
            # Only calculate map geodesic if show_map is True
            geodesic_results_1 = None
            if show_map:
                geodesic_results_1 = calculate_geodesic(P5, P6, P7, P8, tas, wind_speed, wind_dir, chart_id=reference)
            
            distance_p3 = geodesic_results['distance_to_P3_nm_1']
            distance_p4 = geodesic_results['distance_to_P4_nm']
            critical_point_data = geodesic_results.get('critical_point')
            
            if isinstance(critical_point_data, (list, tuple)) and len(critical_point_data) == 2:
                critical_point_obj = Point(critical_point_data[0], critical_point_data[1])
            elif isinstance(critical_point_data, dict) and 'lat' in critical_point_data and 'long' in critical_point_data:
                critical_point_obj = Point(critical_point_data['lat'], critical_point_data['long'])
            else:
                raise ValueError(f"Invalid critical_point_data format: {critical_point_data}")   
            
            land1_obj = Point(land1.lat, land1.long)
            land2_obj = Point(land2.lat, land2.long)        

            nav = Navigation()  
            mid_house = nav.get_midpoint(critical_point_obj, land1_obj)
            mid_land1 = nav.get_midpoint(critical_point_obj, land2_obj) 
            course_from_home = nav.get_track_angle(mid_house, land2_obj)
            course_from_land1 = nav.get_track_angle(mid_land1, land2_obj)
            
            def calculate_ground_speed(true_course, tas, wind_dir, wind_speed):
                """
                Calculate ground speed given true course, true airspeed, wind direction, and wind speed.
                
                Args:
                    true_course (float): Intended flight path in degrees (clockwise from north).
                    tas (float): True airspeed in knots.
                    wind_dir (float): Direction wind is coming from in degrees (clockwise from north).
                    wind_speed (float): Wind speed in knots.
                
                Returns:
                    float: Ground speed in knots.
                """
                tc_rad = math.radians(true_course)
                wd_rad = math.radians(wind_dir)
                wca_rad = math.asin((wind_speed / tas) * math.sin(wd_rad - tc_rad))
                gs = tas * math.cos(wca_rad) - wind_speed * math.cos(wd_rad - tc_rad)
                return gs
            
            gs = calculate_ground_speed(course_from_home, tas, wind_dir, wind_speed)
            cs = calculate_ground_speed(course_from_land1, tas, wind_dir, wind_speed)
            time_p3 = distance_p3/gs
            time_p4 = distance_p4/cs
            time = (time_p3-time_p4)*3600

            if not geodesic_results:
                logging.error("Geodesic calculation failed after retries")
                return jsonify({'error': 'Failed to generate valid geodesic configuration. Please try again.'}), 500
                
            # Add distance between P3 and P4 for 2-mark questions
            distance_p3_p4 = geodesic_results['distance_p3_p4']
            question_text = question_text.replace("is -", f" Given that the distance between {land1.name} and {land2.name} is {distance_p3_p4:.1f} nm, is -")
            
            response_data = {
                'question': question_text,
                'show_map': show_map,
                'details': {
                    'departure': dep.code,
                    'departure_name': dep.name,
                    'arrival': arr.code,
                    'arrival_name': arr.name,
                    'land1': land1.code,
                    'land1_name': land1.name,
                    'land2': land2.code,
                    'land2_name': land2.name,
                    'cruise_level': "FL180",  # Default for 2-mark questions
                    'tas_normal': tas,
                    'tas_single_engine': tas,
                    'wind_normal': {'direction': wind_dir, 'speed': wind_speed},
                    'wind_single_engine': {'direction': wind_dir, 'speed': wind_speed},
                    'shape_type': "ETP",  # Default for 2-mark questions
                    'reference': reference,
                    'geodesic': geodesic_results,
                    'gs': gs,
                    'cs': cs,
                    'time1': time_p3,
                    'time2': time_p4,
                    'time': int(time),
                }
            }
            
            # Add map data only if requested
            if show_map and geodesic_results_1:
                response_data['details']['geodesic_1'] = geodesic_results_1
                response_data['map_data'] = {
                    'chart_reference': reference,
                    'airports': {
                        'departure': {'code': dep1.code, 'name': dep1.name, 'lat': dep1.lat, 'long': dep1.long},
                        'arrival': {'code': arr1.code, 'name': arr1.name, 'lat': arr1.lat, 'long': arr1.long},
                        'land1': {'code': land1_map.code, 'name': land1_map.name, 'lat': land1_map.lat, 'long': land1_map.long},
                        'land2': {'code': land2_map.code, 'name': land2_map.name, 'lat': land2_map.lat, 'long': land2_map.long}
                    }
                }
            
            return jsonify(response_data)
            
        else:  # 3-mark questions - keep existing logic
            # Generate the base question
            question = generator.generate_question_with_reference(reference, num_airports)
            
            # Extract details for geodesic calculation
            dep = question.details.departure
            arr = question.details.arrival
            land1 = question.details.land1
            land2 = question.details.land2
            tas_normal = question.details.tas_single_engine
            wind_speed = question.details.wind_single_engine['speed']
            wind_dir = question.details.wind_single_engine['direction'] % 360
            reference = question.details.reference
            
            dep1 = find_airport_by_name(dep.name, reference, airports)
            arr1 = find_airport_by_name(arr.name, reference, airports)
            land1_map = find_airport_by_name(land1.name, reference, airports)
            land2_map = find_airport_by_name(land2.name, reference, airports)

            P1 = (dep.lat, dep.long)
            P2 = (arr.lat, arr.long)
            P3 = (land1.lat, land1.long)
            P4 = (land2.lat, land2.long)
            P5 = (dep1.lat, dep1.long)
            P6 = (arr1.lat, arr1.long)
            P7 = (land1_map.lat, land1_map.long)
            P8 = (land2_map.lat, land2_map.long)
            reference = question.details.reference
            
            geodesic_results = calculate_geodesic1(P1, P2, P3, P4, tas_normal, wind_speed, wind_dir)
            
            # Only calculate map geodesic if show_map is True
            geodesic_results_1 = None
            if show_map:
                geodesic_results_1 = calculate_geodesic(P5, P6, P7, P8, tas_normal, wind_speed, wind_dir, chart_id=reference)
            
            distance_p3 = geodesic_results['distance_to_P3_nm_1']
            distance_p4 = geodesic_results['distance_to_P4_nm']
            critical_point_data = geodesic_results.get('critical_point')
            
            if isinstance(critical_point_data, (list, tuple)) and len(critical_point_data) == 2:
                critical_point_obj = Point(critical_point_data[0], critical_point_data[1])
            elif hasattr(critical_point_data, 'lat') and hasattr(critical_point_data, 'long'):
                critical_point_obj = critical_point_data
            else:
                logging.error(f"Invalid critical_point type: {type(critical_point_data)}")
                return jsonify({'error': f'Invalid critical_point type: {type(critical_point_data)}'}), 500

            # Calculate track angles 
            nav = Navigation()  
            mid_house = nav.get_midpoint(critical_point_obj, land1)
            mid_land1 = nav.get_midpoint(critical_point_obj, land2) 
            course_from_home = nav.get_track_angle(mid_house, land1)
            course_from_land1 = nav.get_track_angle(mid_land1, land2)
            
            def calculate_ground_speed(true_course, tas, wind_dir, wind_speed):
                """
                Calculate ground speed given true course, true airspeed, wind direction, and wind speed.
                
                Args:
                    true_course (float): Intended flight path in degrees (clockwise from north).
                    tas (float): True airspeed in knots.
                    wind_dir (float): Direction wind is coming from in degrees (clockwise from north).
                    wind_speed (float): Wind speed in knots.
                
                Returns:
                    float: Ground speed in knots.
                """
                tc_rad = math.radians(true_course)
                wd_rad = math.radians(wind_dir)
                wca_rad = math.asin((wind_speed / tas) * math.sin(wd_rad - tc_rad))
                gs = tas * math.cos(wca_rad) - wind_speed * math.cos(wd_rad - tc_rad)
                return gs
            
            gs = calculate_ground_speed(course_from_home, tas_normal, wind_dir, wind_speed)
            cs = calculate_ground_speed(course_from_land1, tas_normal, wind_dir, wind_speed)
            time_p3 = distance_p3/gs
            time_p4 = distance_p4/cs
            time = (time_p3-time_p4)*3600

            # Base question text from the generator
            full_question = question.question  # For 3-mark questions, use as-is
            
            try:
                doc_data = {
                    'question': full_question,
                    'details': {
                        'maganitute': course_from_home,
                        'maganitute1': course_from_land1,
                        'departure': dep.code,
                        'departure_name': dep.name,
                        'arrival': arr.code,
                        'arrival_name': arr.name,
                        'land1': land1.code,
                        'land1_name': land1.name,
                        'land2': land2.code,
                        'land2_name': land2.name,
                        'cruise_level': question.details.cruise_level,
                        'tas_normal': question.details.tas_normal,
                        'tas_single_engine': question.details.tas_single_engine,
                        'wind_normal': question.details.wind_normal,
                        'wind_single_engine': question.details.wind_single_engine,
                        'shape_type': question.details.shape_type,
                        'reference': question.details.reference,
                        'gs': gs,
                        'cs': cs,
                        'time1': time_p3,
                        'time2': time_p4,
                        'time': int(time),
                    }
                }
                
                doc_ref = db.collection("questions").add(doc_data)
                print(f"✅ Success! Document ID: {doc_ref[1].id}")
            except Exception as e:
                print(f"❌ Failed to write to Firestore: {str(e)}")

            # Prepare the response
            response_data = {
                'question': full_question,
                'show_map': show_map,
                'details': {
                    'maganitute': course_from_home,
                    'maganitute_1': course_from_land1,
                    'departure': dep.code,
                    'departure_name': dep.name,
                    'arrival': arr.code,
                    'arrival_name': arr.name,
                    'land1': land1.code,
                    'land1_name': land1.name,
                    'land2': land2.code,
                    'land2_name': land2.name,
                    'cruise_level': question.details.cruise_level,
                    'tas_normal': question.details.tas_normal,
                    'tas_single_engine': question.details.tas_single_engine,
                    'wind_normal': question.details.wind_normal,
                    'wind_single_engine': question.details.wind_single_engine,
                    'shape_type': question.details.shape_type,
                    'reference': question.details.reference,
                    'geodesic': geodesic_results,
                    'gs': gs,
                    'cs': cs,
                    'time1': time_p3,
                    'time2': time_p4,
                    'time': int(time),
                }
            }
            
            # Add map data only if requested
            if show_map and geodesic_results_1:
                response_data['details']['geodesic_1'] = geodesic_results_1
                response_data['map_data'] = {
                    'chart_reference': reference,
                    'airports': {
                        'departure': {'code': dep1.code, 'name': dep1.name, 'lat': dep1.lat, 'long': dep1.long},
                        'arrival': {'code': arr1.code, 'name': arr1.name, 'lat': arr1.lat, 'long': arr1.long},
                        'land1': {'code': land1_map.code, 'name': land1_map.name, 'lat': land1_map.lat, 'long': land1_map.long},
                        'land2': {'code': land2_map.code, 'name': land2_map.name, 'lat': land2_map.lat, 'long': land2_map.long}
                    }
                }
            
            return jsonify(response_data)
            
    except ValueError as ve:
        logging.error(f"ValueError: {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500


# Additional endpoint to get map data for existing questions
@app.route('/get_map_data', methods=['POST'])
def get_map_data_endpoint():
    """
    Endpoint to get map data for an existing question
    Expected JSON payload:
    {
        "question_details": {...}, // The details object from a previous question
        "reference": "L1"  // Chart reference
    }
    """
    try:
        data = request.get_json()
        if not data or 'question_details' not in data or 'reference' not in data:
            return jsonify({'error': 'Missing required parameters: question_details and reference'}), 400
        
        details = data['question_details']
        reference = data['reference']
        
        # Extract airport information
        dep_name = details['departure_name']
        arr_name = details['arrival_name']
        land1_name = details['land1_name']
        land2_name = details['land2_name']
        
        # Find airports on the chart
        dep1 = find_airport_by_name(dep_name, reference, airports)
        arr1 = find_airport_by_name(arr_name, reference, airports)
        land1_map = find_airport_by_name(land1_name, reference, airports)
        land2_map = find_airport_by_name(land2_name, reference, airports)
        
        if not all([dep1, arr1, land1_map, land2_map]):
            return jsonify({'error': 'Could not find all airports on the specified chart'}), 400
        
        # Calculate geodesic for map
        P5 = (dep1.lat, dep1.long)
        P6 = (arr1.lat, arr1.long)
        P7 = (land1_map.lat, land1_map.long)
        P8 = (land2_map.lat, land2_map.long)
        
        tas = details.get('tas_single_engine', details.get('tas_normal', 200))
        wind_speed = details['wind_single_engine']['speed']
        wind_dir = details['wind_single_engine']['direction']
        
        geodesic_results_1 = calculate_geodesic(P5, P6, P7, P8, tas, wind_speed, wind_dir, chart_id=reference)
        
        return jsonify({
            'geodesic_1': geodesic_results_1,
            'map_data': {
                'chart_reference': reference,
                'airports': {
                    'departure': {'code': dep1.code, 'name': dep1.name, 'lat': dep1.lat, 'long': dep1.long},
                    'arrival': {'code': arr1.code, 'name': arr1.name, 'lat': arr1.lat, 'long': arr1.long},
                    'land1': {'code': land1_map.code, 'name': land1_map.name, 'lat': land1_map.lat, 'long': land1_map.long},
                    'land2': {'code': land2_map.code, 'name': land2_map.name, 'lat': land2_map.lat, 'long': land2_map.long}
                }
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Error getting map data: {str(e)}")
        return jsonify({'error': 'Failed to generate map data'}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'online',
        'endpoints': {
            '/generate_question': 'POST - Generate questions for specific reference and num_airports',
            '/question': 'GET - Display question and map interface'
        }
    })

@app.route('/question')
def display_question():
    return render_template('question1.html')

# Add a new endpoint to calculate wind effects and ground speed


# Error handlers
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': str(e.description)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)