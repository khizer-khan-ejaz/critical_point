# ==============================================================================
# IMPORTS
# ==============================================================================
from venv import logger # Note: This import might be incorrect. 'venv' doesn't have a standard logger. Using Python's built-in logging instead.
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random
import math
from math import cos, sin, atan2, sqrt, radians, degrees, asin
import datetime
import logging
from typing import Dict, List, NamedTuple
from fuzzywuzzy import fuzz

# ## NEW ##: Import JWT libraries for authentication
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt

from geographiclib.geodesic import Geodesic
import scipy.optimize as optimize
import firebase_admin
from firebase_admin import credentials, firestore

# Your custom modules. Ensure these files are in the same directory.
from cal_func import calculate_geodesic, calculate_geodesic1
from allclass import *
from sample_airport import *

# ==============================================================================
# INITIALIZATION AND CONFIGURATION
# ==============================================================================

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask App and CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:5000","http://127.0.0.1:5501"]}})

# ## NEW ##: Configure JWT and IP Allowlist
# IMPORTANT: In a production environment, use a strong, random string for the secret key
# and load it from an environment variable for security.
app.config["JWT_SECRET_KEY"] = "a-very-strong-and-secret-key-that-you-should-change" 

# This is the list of IP addresses that are allowed to request a token.
# "127.0.0.1" is your local machine (localhost).
# Replace 'YOUR_CLIENT_IP_HERE' with the actual public IP addresses of your clients.
app.config["ALLOWED_IPS"] = ["127.0.0.1", "82.25.126.162","https://pilottrainingaustralia.unibooker.app"] 

# Initialize the JWT manager
jwt = JWTManager(app)

# Firebase Credentials and Initialization
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "airplane-49087",
    "private_key_id": "84e969bd2c76953bb01f12cea7c94c37b338dcc6",
    "private_key": """-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCdsdQ2iNJsEzH6\nzzK7pLYaTn/u1cTla1RUkCda9AOQdA7DPN7Opyht4m40t7RRrJYozj8Ky4HStfv3\n5dOaL4356P0qIqbMjV34RYZtEe5jyHWosXPQNGaV+pBlL+fuSVSeDFEuYeqiAjqK\n4XkVBpkagpoDKRLHIGRNoAnqKY8X7iD2B/lNvEaQo0F9io/f5lvwJuZQAAA5kPK9\nK4+re0wcZGgbkpdCfmGULvMBfE+i+ExjkuIfX9nh0wIjP5zy//dHl+5tDvl0iOew\n5RcXsAzOGR0UwNohF7cNruBAGpW08OpkTkW658NQwS0mxGy5mn3tMz5DiIihl1y0\nNYdOfW//AgMBAAECggEAHTeaAIKoLgL+cyBZn3+ch9I8jNVJllIk/Uf6KrVkRarj\nI1RPWc2JxZY64gSZYbqO1b+k2YysIIy8Qwlvg7VE4mVDJr/l1KdqnjnPdrzoRM+a\n0ScTtKNI0IfsofrWx4UJqwDQN75HmT29eAbfhsBCtLE29Nfy1TcQrns06xBJJV8c\nd6dt2rfvWgXc4tHmPaiAQtL1RXIUx64jTxvY2OlCASxpzqhxJe100eU0DAq5BQpi\nj6FwvO/OsiMfaZMsYYs5Hoh8IhIbnRXdGQnCYMUsGIEl1rLf3G7n01xLfYXlto0Q\nzXZ+H1vEf7pNRRWmXsLvZF65Xj3kJPmYRg7knvZBQQKBgQDQA8Oynh2iLxldogZ2\nr0rciC8RBaV9iSU7T4H0Zf7fZ7YoZEh95TUXeqPB/eSiQrddkLyOuRnJ4SrrCo0E\nm4ZWN58kwAahX1LlGBY5fKNZlzWbG0R4G8v39CwPYfXlFGtna3F5w2FfIQ4HyPQx\nysMBjiaaz/PoZUQ9+5Ed+dDVvwKBgQDCEm5TcCdighYSmulpTdAR3Nj0hC/wcQwN\ngUQyx12PmXxAQzuj50L4Slmt54Z+SssOTNV0H3R8AwWPf0Zoowt6S8LNJJQZZiuJ\n4LxTL03UBAq/FjesFteCtmBWfCQ4nQFd2t2gsn23/cIoNw3V6nCDaseTgMCAgjL7\n+9ydaKR1wQKBgQCTPFbksy5egd/+epUApQrkFjDaZ5i/xrdnx9tAVoGVOB+jb3gw\nRHDT8aa/xSpz/60yuSP+Ed7DGnH6dDlkrYDkvfITXShUSNiv9+CjSCmHXJRA+Yf5\nTBOPqnEVYk1enJl5Vn+3pCfj4c3AjOjr5Y0qKKgCpHcMY8Ft7gbFpPHAmQKBgQCL\nixsfDa6UCzt5xz97w0KQBX9OWdnqhi6Ha2IxLN7eSRtpTa6NjNS/mR5gh/BR0M+u\niZqVs6RbIwUViAuFY272UZFRVjLTDH7T1e8z1PieMQXVHlGLgKUXTLF6niqhNmts\nI9pmGNGCwYigx+0/2iFqrRWxvssr2/Jy80dPO5W9QQKBgHxVkgeNeD8B9GOFH3mA\nMn05bNqKWFiJU2kBp4rTnzUy+0DiT15NL8SEGyHKRno0Mcm6//DdBTJexomccVvt\nYdVz6J3t67GQCD+FnCZSZvubaygog8/PSNdizRQrIHuLX11Urj9q4BeLA6vuYVRy\npY+B7jrN1sp81hvYQRsDKLbm\n-----END PRIVATE KEY-----\n""",
    "client_email": "firebase-adminsdk-fbsvc@airplane-49087.iam.gserviceaccount.com",
    "client_id": "107082013090178902883",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40airplane-49087.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})

firebase_admin.initialize_app(cred)
db = firestore.client()
print("✅ Firebase & Firestore initialized successfully!")

# GeoMag Initialization
try:
    from pygeomag import GeoMag
    geo = GeoMag()
    has_pygeomag = True
except ImportError:
    has_pygeomag = False
    logging.warning("pygeomag library not found. Magnetic variation calculations will be disabled.")


# ==============================================================================
# HELPER FUNCTIONS 
# ==============================================================================

# ## NEW ##: Helper function to get the real client IP address
    def get_client_ip():
        """
        Correctly identifies the client's IP address, even behind a reverse proxy.
        """
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip = request.remote_addr
        return ip

# ---- All your existing helper functions and classes remain here ----
class Navigation:
    def get_track_angle(self, dep, arr, magnetic=True, date=None):
        if not (-90 <= dep.lat <= 90 and -180 <= dep.long <= 180 and 
                -90 <= arr.lat <= 90 and -180 <= arr.long <= 180):
            raise ValueError("Invalid latitude or longitude")
        if (dep.lat, dep.long) == (arr.lat, arr.long):
            return 0.0
        lat1, lon1, lat2, lon2 = map(math.radians, [dep.lat, dep.long, arr.lat, arr.long])
        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        true_bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
        if not magnetic:
            return round(true_bearing, 2)
        magnetic_variation = self.get_magnetic_variation(dep.lat, dep.long, date)
        magnetic_bearing = (true_bearing - magnetic_variation + 360) % 360
        return round(magnetic_bearing, 2)

    def get_magnetic_variation(self, lat, lon, date=None):
        if not has_pygeomag:
            logging.warning("GeoMag unavailable. Using fallback magnetic variation (-12.0 for New York).")
            return -12.0
        try:
            date = date or datetime.datetime.utcnow()
            dec_year = self.decimal_year(date)
            result = geo.calculate(glat=lat, glon=lon, alt=0, time=dec_year)
            return float(result.dec)
        except Exception as e:
            logging.error(f"Error calculating magnetic variation: {e}")
            return -12.0

    def decimal_year(self, date):
        year_start = datetime.datetime(date.year, 1, 1)
        year_end = datetime.datetime(date.year + 1, 1, 1)
        return date.year + (date - year_start).total_seconds() / (year_end - year_start).total_seconds()

    def get_midpoint(self, dep, arr):
        lat1, lon1, lat2, lon2 = map(math.radians, [dep.lat, dep.long, arr.lat, arr.long])
        x1, y1, z1 = math.cos(lat1) * math.cos(lon1), math.cos(lat1) * math.sin(lon1), math.sin(lat1)
        x2, y2, z2 = math.cos(lat2) * math.cos(lon2), math.cos(lat2) * math.sin(lon2), math.sin(lat2)
        x, y, z = (x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2
        lon = math.atan2(y, x)
        lat = math.atan2(z, math.sqrt(x * x + y * y))
        return Point(round(math.degrees(lat), 4), round(math.degrees(lon), 4))

    def get_route_magnitude(self, dep, arr, unit='km'):
        R = {'km': 6371.0, 'nm': 3440.1, 'mi': 3958.8}.get(unit, 6371.0)
        lat1, lon1, lat2, lon2 = map(math.radians, [dep.lat, dep.long, arr.lat, arr.long])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        if unit == 'nm':
            distance = distance / 1.852 * 0.539957 # Correct conversion
        elif unit == 'mi':
            distance = distance * 0.621371
        return round(distance, 2)


def haversine_distance(lat1, lon1, lat2, lon2, unit='nm'):
    R_KM = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance_km = c * R_KM
    if unit == 'nm':
        return distance_km / 1.852
    elif unit == 'mi':
        return distance_km * 0.621371
    return distance_km

# Your improved fuzzy matching function
def find_airport_by_name(name, reference, airports):
    if not name or not airports:
        # Using print for direct feedback, but logging is better
        print("Invalid input: name or airports list is empty")
        return None
    name_lower, name_upper = name.lower().strip(), name.upper().strip()
    reference_list = []
    if isinstance(reference, list):
        reference_list = [ref.upper().strip() for ref in reference if isinstance(ref, str) and ref.strip()]
    elif isinstance(reference, str) and reference.strip():
        reference_list = [reference.upper().strip()]
    
    candidates = []
    for airport in airports:
        score = 0
        airport_name_clean = airport.name.lower().strip()
        airport_code_lower = airport.code.lower().strip()
        airport_reference = airport.reference.upper().strip() if airport.reference else ""
        
        if name_lower == airport_name_clean: score += 100
        if name_upper == airport.code: score += 95
        if reference_list and airport_reference in reference_list: score += 90
        if airport_name_clean.startswith(name_lower): score += 85
        fuzzy_score = fuzz.ratio(name_lower, airport_name_clean)
        if fuzzy_score >= 80: score += fuzzy_score * 0.75
        if name_lower in airport_name_clean: score += 65
        
        if score > 0:
            candidates.append({"airport": airport, "score": score})
    
    if candidates:
        return max(candidates, key=lambda x: x["score"])["airport"]
    
    print(f"No match found for '{name}'")
    return None

def find(name, airports):
    name_lower = name.lower()
    for airport in airports:
        if name_lower in airport.name.lower():
            return airport
    return None

PREDEFINED_2_MARK_QUESTIONS = [
    {
        "text_template": "Q1.Refer to ERC {reference}.\n\nYou are planning a flight from {dep_name_text} to {arr_name_text} on {track_name}. TAS is {tas} and W/V {wind_dir_display}M/{wind_speed} kt\n.The question asks for the position of the Critical Point (CP) between {etp_dest1_name_text} and {etp_dest2_name_text} along the {dep_name_text} to {arr_name_text} track ,  as a distance from {dep_name_text}, is closest to -",
        "dep_name_text": "Launceston", "arr_name_text": "East sale", "track_name": "W-218", "etp_dest1_name_text": "East sale", "etp_dest2_name_text": "Latrobe Valley", "reference": "L1",
    },
    {
        "text_template": "Q2.Refer to ERC {reference}.\n\nYou are planning a flight from {dep_name_text} to {arr_name_text} on {track_name}. TAS is {tas} and W/V {wind_dir_display}M/{wind_speed} kt\n.The question asks for the position of the Critical Point (CP) between {etp_dest1_name_text} and {etp_dest2_name_text} along the {dep_name_text} to {arr_name_text} track ,  as a distance from {dep_name_text}, is closest to -",
        "reference": "L2", "dep_name_text": "Griffith", "arr_name_text": "Mildura", "track_name": "W-415", "etp_dest1_name_text": "Mildura", "etp_dest2_name_text": "Swan Hill",
    },
    {
        "text_template": "Q3.Refer to ERC {reference}.\n\nYou are planning a flight from {dep_name_text} to {arr_name_text} on {track_name}. TAS is {tas} and W/V {wind_dir_display}M/{wind_speed} kt\n.The question asks for the position of the Critical Point (CP) between {etp_dest1_name_text} and {etp_dest2_name_text} along the {dep_name_text} to {arr_name_text} track ,  as a distance from {dep_name_text}, is closest to -",
        "dep_name_text": "Grafton", "arr_name_text": "Inverell", "track_name": "W-623", "etp_dest1_name_text": "Inverell", "etp_dest2_name_text": "Armidale", "reference": "L2",
    },
    {
        "text_template": "Q3.Refer to ERC {reference}.\n\nYou are planning a flight from {dep_name_text} to {arr_name_text} on {track_name}. TAS is {tas} and W/V {wind_dir_display}M/{wind_speed} kt\n.The question asks for the position of the Critical Point (CP) between {etp_dest1_name_text} and {etp_dest2_name_text} along the {dep_name_text} to {arr_name_text} track ,  as a distance from {dep_name_text}, is closest to -",
        "dep_name_text": "Inverell", "arr_name_text": "Walgett", "track_name": "W623", "etp_dest1_name_text": "Walgett", "etp_dest2_name_text": "Narrabri", "reference": "L3"
    },
    {
        "text_template": "Q4.Refer to ERC {reference}.\n\nYou are planning a flight from {dep_name_text} to {arr_name_text} on {track_name}.  TAS is {tas} and W/V {wind_dir_display}M/{wind_speed} kt\n.The question asks for the position of the Critical Point (CP) between {etp_dest1_name_text} and {etp_dest2_name_text} along the {dep_name_text} to {arr_name_text} track ,  as a distance from {dep_name_text}, is closest to -",
        "dep_name_text": "Emerald", "arr_name_text": "Charleville", "track_name": "W-806", "etp_dest1_name_text": "Charleville", "etp_dest2_name_text": "Roma", "reference": "L4",
    }
]
generator = AirportQuestionGenerator(sample_airports)


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

# ## MODIFIED ##: Home endpoint with updated info
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'online',
        'message': 'Welcome to the Aviation Question Generator API!',
        'endpoints': {
            '/login': 'POST - Get an access token if your IP is authorized.',
            '/generate_question': 'POST - Generate a question (requires valid JWT).',
            '/get_map_data': 'POST - Get map data for a question (requires valid JWT).',
            '/question': 'GET - A simple frontend to display a question.'
        }
    })

# ## NEW ##: Login endpoint to issue tokens to authorized IPs
@app.route('/login', methods=['POST'])
def login():
    client_ip = get_client_ip()
    logging.info(f"Login attempt from IP: {client_ip}")

    if client_ip not in app.config["ALLOWED_IPS"]:
        logging.warning(f"Access denied for IP: {client_ip}. Not in allowlist.")
        return jsonify({"msg": "Access denied: Your IP address is not authorized."}), 403

    # IP is allowed. Create a token and bind it to the IP for extra security.
    additional_claims = {"ip": client_ip}
    access_token = create_access_token(identity=client_ip, additional_claims=additional_claims)
    
    logging.info(f"Token successfully issued for IP: {client_ip}")
    return jsonify(access_token=access_token)


# ## MODIFIED ##: Protected Question Generation Endpoint
@app.route('/generate_question', methods=['POST'])
@jwt_required() 
def generate_question_endpoint():
 # This decorator protects the endpoint
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

        # For 2-mark questions, use predefined questions with retry logic
        if marks == 2:
            max_question_attempts = 100000 # Number of times to retry the entire question
            for question_attempt in range(max_question_attempts):
                
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
                        base_number = random.randint(10, 35)
                        return base_number * 10

                    def generate_wind_strength():
                        num_multiples = 90 // 5
                        random_index = random.randint(0, num_multiples - 1)
                        return (random_index + 1) * 5
                    
                    def random_multiple_of_5(min_value, max_value):
                        lower_bound = min_value if min_value % 5 == 0 else min_value + (5 - min_value % 5)
                        upper_bound = max_value if max_value % 5 == 0 else max_value - (max_value % 5)
                        num_multiples = (upper_bound - lower_bound) // 5 + 1
                        random_index = random.randint(0, num_multiples - 1)
                        return lower_bound + random_index * 5
                    
                    # Initialize parameters
                    max_attempts = 5
                    attempt = 0
                    time = float('inf')
                    
                    while attempt < max_attempts and abs(time) >= 60:
                        # Generate random wind and TAS values
                        wind_dir = generate_three_digit_multiple_of_10()
                        wind_speed = generate_wind_strength()
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
                        distance_to_P3_nm = geodesic_results['distance_to_P3_nm']
                        distance_p1 = geodesic_results['distance_to_P1_nm']
                        
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
                            tc_rad = math.radians(true_course)
                            wd_rad = math.radians(wind_dir)
                            wca_rad = math.asin((wind_speed / tas) * math.sin(wd_rad - tc_rad))
                            gs = tas * math.cos(wca_rad) - wind_speed * math.cos(wd_rad - tc_rad)
                            return gs
                        
                        gs = calculate_ground_speed(course_from_home, tas, wind_dir, wind_speed)
                        cs = calculate_ground_speed(course_from_land1, tas, wind_dir, wind_speed)
                        time_p3 = distance_p3 / gs
                        time_p4 = distance_p4 / cs
                        time_p3_1 = distance_p3 / gs
                        time_p4_1 = distance_p4 / cs
                        time = (time_p3 - time_p4) * 3600  # In seconds
                        
                        attempt += 1
                    
                    # If time difference is within 60 seconds, proceed with response
                    if abs(time) < 60:
                        distance_to_degree = geodesic_results['distance_to_degree']    
                        
                        # Add distance between P3 and P4 for 2-mark questions
                        distance_p3_p4 = geodesic_results['distance_p3_p4']
                        P3toP4 = haversine_distance(land1.lat, land1.long, land2.lat, land2.long)
                        question_text = question_text.replace("is -", f" Given that the distance between {land1.name} and {land2.name} is {distance_p3_p4:.1f} nm, is -")
                        steps = [
                            {
                                "step_number": 1,
                                "title": "Calculate Critical Point Distance",
                                "description": f"Draw a line from {land1.name} to {land2.name}. Mark the point halfway along the {dep.code}-{arr.code} line. ",
                                "calculation": f"This distance should be {P3toP4}NM and the mid-point should be {P3toP4/2}NM.",
                                "result": " nautical miles"
                            },
                            {
                                "step_number": 2,
                                "title": f"Draw a line at right angles to the {land1.name} - {land2.name} line across the {dep.code}-{arr.code} Track. This point will be the ETP in nil wind",
                            },
                            {
                                "step_number": 3,
                                "title": f"Calculate the wind vector that will affect the nil wind ETP",
                                "description": f'''To do this you will need the aircraft's Single Engine TAS ({tas}KTS) and using the calculated nil  
                                    wind time interval, multiply this by the wind speed to determine the length of  
                                    time the wind affects the flight. 
                                    (note: since the question for asked single engine critical point, we will use single engine TAS)  
                                    In this case, the TAS is {tas} knots and the distance from the nil wind ETP 
                                    to either airport is {distance_to_P3_nm}NM
                                    The nil wind time to either airport is {distance_to_P3_nm/tas} hours (Dist./TAS).  
                                    The wind is {wind_speed} knots (at single engine cruise level), {distance_to_P3_nm/tas}hrs worth is ({distance_to_P3_nm/tas} x {wind_speed} = {distance_to_degree} NM.) 
                                       '''
                            },
                            {
                                "step_number": 4,
                                "title": f"Using a protractor draw a wind vector from the nil wind ETP",
                                "description": f"From the nil wind ETP {distance_to_degree} on wind vector. Now draw a line parallel to the original line that bisects {land1.name} and {land2.name}. Where this line intersects the {dep.code}-{arr.code} track is the actual ETP for continuing to {land1.name} or diverting to {land2.name}. ",
                                "result": f"In this case the actual ETP lies {distance_p1}nm from {dep.name}   "
                            },
                            {
                                "step_number": 5,
                                "title": "Verification: ",
                                "description": f"We can verify if this answer is correct by calculating the time required to fly to either {land1.name} or {land2.name} and comparing. Ideally, the times should be the same (+-1 minute).\n"
                                f"Distance from Critical Point to {land1.name}: {distance_p3}NM "
                                f"Average Track from Critical Point to {land1.name}: {course_from_home}M "
                                f"Groundspeed from Critical Point to {land1.name}: {gs}KTS "
                                f"Time= Distance/Speed. Therefore = {time_p3_1*60:.1f}Mins ",
                            },
                            {
                                "step_number": 6,
                                "title": "Verification: ",
                                "description": f"We can verify if this answer is correct by calculating the time required to fly to either {land1.name} or {land2.name} and comparing. Ideally, the times should be the same (+-1 minute)."
                                f"Distance from Critical Point to {land2.name}: {distance_p4}NM "
                                f"Average Track from Critical Point to {land2.name}: {course_from_land1}M "
                                f"Groundspeed from Critical Point to {land2.name}: {cs}KTS "
                                f"Time= Distance/Speed. Therefore = {time_p4_1*60:.1f}Mins ",
                            }
                        ]
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
                                'steps': steps,
                                'Ans':distance_p1
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
            tas_single = question.details.tas_single_engine
            wind_speed = question.details.wind_single_engine['speed']
            wind_dir = question.details.wind_single_engine['direction'] % 360
            reference = question.details.reference
            reference_point=question.details.rondom_choice
            

            
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
            
            geodesic_results = calculate_geodesic1(P1, P2, P3, P4, tas_single, wind_speed, wind_dir)
            distance_to_P3_nm=geodesic_results['distance_to_P3_nm']
            degreesdistance=geodesic_results['distance_to_degree']           
            # Only calculate map geodesic if show_map is True
            geodesic_results_1 = None
            if show_map:
                geodesic_results_1 = calculate_geodesic(P5, P6, P7, P8, tas_single, wind_speed, wind_dir, chart_id=reference)
            distance_p1=geodesic_results['distance_to_P1_nm']
           
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
                        
            distancefrom2=haversine_distance(critical_point_obj.lat,critical_point_obj.long,arr.lat,arr.long)
            P3toP4=haversine_distance(land1.lat,land1.long,land2.lat,land2.long)
            cp_distance = distance_p1 if reference_point == dep.name else distancefrom2
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
            
            gs = calculate_ground_speed(course_from_home, tas_single, wind_dir, wind_speed)
            cs = calculate_ground_speed(course_from_land1, tas_single, wind_dir, wind_speed)
            time_p3 = distance_p3/gs
            time_p4 = distance_p4/cs
            time = (time_p3-time_p4)*3600
            time_p3_1 = distance_p3/gs*60
            time_p4_1 = distance_p4/cs*60

            # Base question text from the generator
            full_question = question.question  # For 3-mark questions, use as-is
            steps = [
            {
                "step_number": 1,
                "title": "Calculate Critical Point Distance",
                "description": f"Draw a line from {land1.name} to {land2.name}. Mark the point halfway along the {dep.code}-{arr.code} line. ",
                "calculation": f"This distance should be {P3toP4}NM and the mid-point should be {P3toP4/2}NM.",
                "result": " nautical miles"
            },
            {
                "step_number": 2,
                "title": f"Draw a line at right angles to the {land1.name} - {land2.name}  line across the {dep.code}-{arr.code} Track. This point will be the ETP in nil wind",
                
            },
            {
                "step_number": 3,
                "title": f"Calculate the wind vector that will affect the nil wind ETP",
                "description": f'''To do this you will need the aircraft's Single Engine TAS ({tas_single}KTS) and using the calculated nil  

                                    wind time interval, multiply this by the wind speed to determine the length of  

                                    time the wind affects the flight. 

                                    (note: since the question for asked single engine critical point, we will use single engine TAS)  

                                    In this case, the TAS is  knots and the distance from the nil wind ETP 
                                    to either airport is {distance_to_P3_nm}NM
                                    The nil wind time to either airport is {distance_to_P3_nm/tas_single} hours (Dist./TAS).  

                                    The wind is {wind_speed} knots (at single engine cruse level), {distance_to_P3_nm/tas_single}hrs worth is ({distance_to_P3_nm/tas_single} x {wind_speed} = {degreesdistance} NM.) 
                                       '''
            },
            {
                "step_number": 4,
                "title": f"Using a protractor draw a wind vector from the nil wind ETP",
                "description": f"From the nil wind ETP {degreesdistance} on wind vector.Now draw a line  parallel to the original line that bisects {land1.name} and {land2.name} .Where this line  intersects the {dep.code}-{arr.code} track is the actual ETP for continuing to {land1.name}  or  diverting to {land2.name}. ",
                "result": f"In this case the actual ETP lies {distance_p1}nm from {dep.name}, or {distancefrom2}nm from {arr.name}.  "
            },
            {
                "step_number": 5,
                "title": "Verification: ",
                "description": f"We can verify if this answer is correct by calculating the time required to fly to either {land1.name} or {land2.name} and comparing. Ideally, the times should be the same (+-1 minute).\n"
                f"Distance from Critical Point to {land1.name}: {distance_p3}NM "
                f"Average Track from Critical Point to {land1.name}: {course_from_home}M "
                f"Groundspeed from Critical Point to {land1.name}: {gs}KTS "
                f"Time= Distance/Speed. Therefore =  {time_p3_1}Mins ",
                

                
            },
            {
                "step_number": 6,
                "title": f"Verification: ",
                "description": f"We can verify if this answer is correct by calculating the time required to fly to either {land1.name} or {land2.name} and comparing. Ideally, the times should be the same (+-1 minute)."
                f"Distance from Critical Point to {land2.name}: {distance_p4}NM "
                f"Average Track from Critical Point to {land2.name}: {course_from_land1}M "
                f"Groundspeed from Critical Point to {land2.name}: {cs}KTS "
                f"Time= Distance/Speed. Therefore =  {time_p4_1}Mins ",
            }
        ]


        
            
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
                    'Ans':cp_distance,
                    'Ans2':distancefrom2,
                    'gs': gs,
                    'cs': cs,
                    'time1': time_p3,
                    'time2': time_p4,
                    'time': int(time),
                    'steps': steps 
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


# ## MODIFIED ##: Protected Map Data Endpoint
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


# Public endpoint for the frontend template
@app.route('/question')
def display_question():
    return render_template('question1.html')

# ==============================================================================
# ERROR HANDLERS AND MAIN EXECUTION
# ==============================================================================
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': str(e.description)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)