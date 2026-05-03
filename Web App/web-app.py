import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import pymongo
import hashlib
import uuid
import json
import folium
from streamlit_folium import st_folium
import io
import base64
import os
import streamlit as st
from ultralytics import YOLO

#python -m streamlit run app4.py --server.port 8502

# MongoDB Connection
def connect_to_mongodb():
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["railway_defect_detection"]
        return client, db
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        return None, None

# Initialize MongoDB connection
mongo_client, db = connect_to_mongodb()

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'init_db' not in st.session_state:
    st.session_state.init_db = False

# GPS Extraction Functions
def get_gps_data(image_path_or_obj):
    """Extract GPS data from image EXIF"""
    try:
        if isinstance(image_path_or_obj, str):
            image = Image.open(image_path_or_obj)
        else:
            image_path_or_obj.seek(0)
            image = Image.open(image_path_or_obj)
            
        exif_data = image._getexif()
        
        if exif_data is None:
            return None
            
        gps_data = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "GPSInfo":
                for gps_tag in value:
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_data[gps_tag_name] = value[gps_tag]
        
        return gps_data if gps_data else None
    except Exception as e:
        # st.error(f"Error reading GPS data: {str(e)}")
        return None

def convert_to_degrees(value):
    """Convert GPS coordinates to degrees"""
    try:
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)
    except:
        return None

def extract_gps_coordinates(gps_data):
    """Extract latitude and longitude from GPS data"""
    if not gps_data:
        return None, None
    
    try:
        lat = gps_data.get('GPSLatitude')
        lat_ref = gps_data.get('GPSLatitudeRef')
        lon = gps_data.get('GPSLongitude')
        lon_ref = gps_data.get('GPSLongitudeRef')
        
        if lat and lon:
            latitude = convert_to_degrees(lat)
            longitude = convert_to_degrees(lon)
            
            if lat_ref == 'S':
                latitude = -latitude
            if lon_ref == 'W':
                longitude = -longitude
                
            return latitude, longitude
    except Exception as e:
        # st.error(f"Error converting GPS coordinates: {str(e)}")
        pass
        
    return None, None

def image_to_base64(image_path_or_obj, max_size=(400, 400)):
    """Convert image to base64 string for embedding in HTML"""
    try:
        if isinstance(image_path_or_obj, str):
            image = Image.open(image_path_or_obj)
        else:
            image_path_or_obj.seek(0)
            image = Image.open(image_path_or_obj)
        
        # Resize image
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=90)
        img_buffer.seek(0)
        
        img_str = base64.b64encode(img_buffer.read()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    
    except Exception as e:
        st.error(f"Error converting image to base64: {str(e)}")
        return None

def create_defect_map(defect_locations):
    """Create a map showing defect locations"""
    if not defect_locations:
        return None
    
    # Calculate center
    center_lat = sum(item['latitude'] for item in defect_locations) / len(defect_locations)
    center_lon = sum(item['longitude'] for item in defect_locations) / len(defect_locations)
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Add different tile layers
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='© Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='© OpenStreetMap contributors, © CARTO',
        name='CartoDB Light',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add markers for defect locations
    for i, item in enumerate(defect_locations):
        # Determine marker color based on defect count
        defect_count = item.get('defects_count', 0)
        if defect_count == 0:
            icon_color = 'green'
            status_emoji = '✅'
        elif defect_count <= 2:
            icon_color = 'orange'
            status_emoji = '⚠️'
        else:
            icon_color = 'red'
            status_emoji = '🚨'
        
        # Create popup with defect information
        popup_html = f"""
        <div style="width: 450px; font-family: Arial, sans-serif;">
            <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); 
                       color: white; padding: 15px; margin: -10px -10px 15px -10px; 
                       border-radius: 8px 8px 0 0; text-align: center;">
                <h3 style="margin: 0; font-size: 18px;">{status_emoji} {item['filename']}</h3>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Railway Track Analysis</p>
            </div>
            
            <div style="text-align: center; margin-bottom: 15px;">
                <img src="{item['image_base64']}" 
                     style="max-width: 420px; max-height: 300px; 
                            border: 3px solid {'#dc3545' if defect_count > 0 else '#28a745'}; 
                            border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            </div>
            
            <div style="background: {'#fff2f2' if defect_count > 0 else '#f0fff4'}; 
                       padding: 15px; border-radius: 8px; 
                       border-left: 5px solid {'#dc3545' if defect_count > 0 else '#28a745'};">
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 5px;">
                        <div style="font-size: 24px; font-weight: bold; color: {'#dc3545' if defect_count > 0 else '#28a745'};">
                            {defect_count}
                        </div>
                        <div style="font-size: 12px; color: #666;">Defects Found</div>
                    </div>
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 5px;">
                        <div style="font-size: 16px; font-weight: bold; color: #2a5298;">
                            {'HIGH' if defect_count > 2 else 'MEDIUM' if defect_count > 0 else 'SAFE'}
                        </div>
                        <div style="font-size: 12px; color: #666;">Risk Level</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 10px;">
                    <strong style="color: #2a5298;">📍 Location:</strong><br>
                    <span style="font-family: monospace; font-size: 12px;">
                        Lat: {item['latitude']:.6f} | Lon: {item['longitude']:.6f}
                    </span>
                </div>
                
                <div style="margin-bottom: 10px;">
                    <strong style="color: #2a5298;">⏰ Processed:</strong><br>
                    <span style="font-size: 12px;">{item.get('timestamp', 'Unknown')}</span>
                </div>
                
                <div>
                    <strong style="color: #2a5298;">🔍 Confidence:</strong><br>
                    <span style="font-size: 12px;">
                        Avg: {item.get('avg_confidence', 0):.1%} | 
                        Max: {item.get('max_confidence', 0):.1%}
                    </span>
                </div>
            </div>
        </div>
        """
        
        folium.Marker(
            location=[item['latitude'], item['longitude']],
            popup=folium.Popup(popup_html, max_width=470),
            tooltip=f"{status_emoji} {item['filename']} | {defect_count} defects | Click for details",
            icon=folium.Icon(
                color=icon_color,
                icon='exclamation-triangle' if defect_count > 0 else 'ok-sign',
                prefix='fa'
            )
        ).add_to(m)
    
    return m

# Initialize database collections if they don't exist
def initialize_database():
    if not st.session_state.init_db and mongo_client is not None:
        # Check if users collection exists and has admin
        users_collection = db["users"]
        if users_collection.count_documents({}) == 0:
            # Create default admin user
            admin_user = {
                "username": "admin",
                "password": hashlib.sha256("admin123".encode()).hexdigest(),
                "is_admin": True,
                "created_at": datetime.now()
            }
            users_collection.insert_one(admin_user)
            st.session_state.init_db = True
            
            # Create indexes
            users_collection.create_index("username", unique=True)
            
            # Create defects collection with indexes
            defects_collection = db["defects"]
            defects_collection.create_index("detection_id")
            defects_collection.create_index("detected_by")
            defects_collection.create_index("detection_date")
            
            st.success("Database initialized with default admin account (username: admin, password: admin123)")
        else:
            st.session_state.init_db = True

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication functions
def login(username, password):
    if mongo_client is None:
        st.error("Cannot connect to database")
        return False
    
    users_collection = db["users"]
    user = users_collection.find_one({
        "username": username,
        "password": hash_password(password)
    })
    
    if user:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.is_admin = user.get("is_admin", False)
        return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_admin = False

def create_user(username, password, is_admin=False):
    if mongo_client is None:
        st.error("Cannot connect to database")
        return False
    
    users_collection = db["users"]
    
    # Check if user already exists
    if users_collection.find_one({"username": username}):
        return False
    
    # Create new user
    new_user = {
        "username": username,
        "password": hash_password(password),
        "is_admin": is_admin,
        "created_at": datetime.now()
    }
    
    users_collection.insert_one(new_user)
    return True

# Set page configuration
st.set_page_config(
    page_title="Railway Track Defect Detection with GPS Mapping",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚂"
)

# Custom CSS for better styling (keeping your original styles plus map enhancements)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-top: 2rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .status-ok {
        color: #10B981;
        font-weight: bold;
    }
    .status-warning {
        color: #F59E0B;
        font-weight: bold;
    }
    .defect-detected {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .no-defect {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .map-container {
        border: 2px solid #dee2e6;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .gps-info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2a5298;
        margin: 0;
    }
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the database
initialize_database()

# Load the model with caching to improve performance
@st.cache_resource
def load_model(model_path):
    """Load YOLO model from given path."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    return YOLO(model_path)

# Try loading with relative path first, fallback to absolute
try:
    model_path = "./yolo11x/best.pt"  # Change if using YOLO11l path
    model = load_model(model_path)
    model_loaded = True
except FileNotFoundError:
    try:
        model_path = r"D:\Rail Paper_Thesis\Models\Latest\railway_defect_detection\weights\best.pt"
        model = load_model(model_path)
        model_loaded = True
    except Exception as e:
        model_loaded = False
        st.error(f"⚠️ Error loading model: {e}")

# Authentication UI
def show_login_ui():
    st.markdown('<div class="main-header">🚂 Railway Track Defect Detection with GPS Mapping</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "About"])
    
    with tab1:
        st.subheader("Login to Access the System")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Login", use_container_width=True):
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        st.markdown("""
        <div class="gps-info-box">
        <h3>🚂 Railway Track Defect Detection with GPS Mapping</h3>
        
        This enhanced application combines AI-powered defect detection with GPS location mapping:
        <br><br>
        <b>✨ New Features:</b><br>
        • 🗺️ Interactive GPS mapping of defect locations<br>
        • 📍 Automatic GPS extraction from images<br>
        • 🎯 Visual risk assessment on map<br>
        • 📊 Location-based analytics<br>
        • 📥 Export GPS data with defect information<br>
        <br>
        <b>Developers:</b><br>
        Moshiur Rahman Sayem - <a href="https://www.facebook.com/moshiurrahmansayembd" target="_blank" style="color: #e8f4f8;">Facebook</a><br>
        Md. Mehedi Hassan - <a href="https://www.facebook.com/md.hassan.mehedi.s____" target="_blank" style="color: #e8f4f8;">Facebook</a><br>            
        <b>Enhanced:</b> January 2025
        </div>
        """, unsafe_allow_html=True)

# User management UI (admin only) - keeping your original function
def show_user_management():
    st.markdown('<div class="admin-section">', unsafe_allow_html=True)
    st.subheader("👤 User Management")
    
    tab1, tab2, tab3 = st.tabs(["Create User", "View Users", "System Stats"])
    
    with tab1:
        st.subheader("Create New User")
        new_username = st.text_input("Username", key="new_username")
        new_password = st.text_input("Password", type="password", key="new_password")
        is_admin = st.checkbox("Admin privileges", key="is_admin")
        
        if st.button("Create User"):
            if new_username and new_password:
                if create_user(new_username, new_password, is_admin):
                    st.success(f"User '{new_username}' created successfully!")
                else:
                    st.error(f"Username '{new_username}' already exists!")
            else:
                st.warning("Please enter both username and password")
    
    with tab2:
        if mongo_client is not None:
            users = list(db["users"].find({}, {"_id": 0, "password": 0}))
            if users:
                users_df = pd.DataFrame(users)
                if "created_at" in users_df.columns:
                    users_df["created_at"] = users_df["created_at"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
                st.dataframe(users_df, use_container_width=True)
            else:
                st.info("No users found")
    
    with tab3:
        if mongo_client is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                user_count = db["users"].count_documents({})
                admin_count = db["users"].count_documents({"is_admin": True})
                
                st.metric("Total Users", user_count)
                st.metric("Admin Users", admin_count)
            
            with col2:
                defect_count = db["defects"].count_documents({})
                latest_detection = db["defects"].find_one(
                    {}, 
                    sort=[("detection_date", pymongo.DESCENDING)]
                )
                
                st.metric("Total Detection Records", defect_count)
                if latest_detection:
                    st.metric(
                        "Latest Detection", 
                        latest_detection.get("detection_date", "Unknown").strftime("%Y-%m-%d %H:%M")
                    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Save detection results to MongoDB (enhanced with GPS data)
def save_detection_to_db(detection_data, detection_id=None):
    if mongo_client is None:
        return None
    
    defects_collection = db["defects"]
    
    if detection_id is None:
        detection_id = str(uuid.uuid4())
    
    detection_record = {
        "detection_id": detection_id,
        "detected_by": st.session_state.username,
        "detection_date": datetime.now(),
        "results": detection_data
    }
    
    defects_collection.insert_one(detection_record)
    return detection_id

# Main application UI (enhanced with GPS mapping)
def show_main_app():
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown(f"""
        <div class="gps-info-box">
        <h3>Welcome, {st.session_state.username}!</h3>
        {"<span class='status-warning'>Admin Mode</span>" if st.session_state.is_admin else ""}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-header">Detection Settings</div>', unsafe_allow_html=True)
        
        # Input methods
        st.subheader("Input Source")
        input_method = st.radio(
            "Select input method:",
            ["Folder with Images", "Upload Images"],
            key="input_method"
        )
        
        # Folder path input
        if input_method == "Folder with Images":
            folder_path = st.text_input("📂 Enter Folder Path:", placeholder="/path/to/images")
        
        # File uploader
        elif input_method == "Upload Images":
            uploaded_files = st.file_uploader(
                "Upload image files", 
                accept_multiple_files=True,
                type=["jpg", "jpeg", "png"]
            )
        
        # Advanced settings
        st.markdown('<div class="sidebar-header">Advanced Settings</div>', unsafe_allow_html=True)
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Minimum confidence score for detection"
        )
        
        # GPS Settings
        st.markdown('<div class="sidebar-header">GPS Settings</div>', unsafe_allow_html=True)
        show_gps_map = st.checkbox("Show GPS Map", value=True, help="Display defect locations on interactive map")
        map_height = st.slider("Map Height", 400, 800, 600, 50)
        
        # User options
        st.markdown('<div class="sidebar-header">User Options</div>', unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    # Main content
    st.markdown('<div class="main-header">🚂 Railway Track Defect Detection with GPS Mapping</div>', unsafe_allow_html=True)
    
    # Show admin panel if user is admin
    if st.session_state.is_admin:
        show_user_management()
    
    # Recent detections
    if mongo_client is not None:
        recent_detections = list(db["defects"].find({}, {"_id": 0, "results": 0}).sort("detection_date", -1).limit(5))
        if recent_detections:
            st.markdown('<div class="sub-header">Recent Detection Sessions</div>', unsafe_allow_html=True)
            recent_df = pd.DataFrame(recent_detections)
            recent_df["detection_date"] = recent_df["detection_date"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
            st.dataframe(recent_df, use_container_width=True, hide_index=True)
    
    # Enhanced Process function with GPS tracking
    def process_images_with_gps(image_list, image_paths=None, is_upload=False):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        start_time = time.time()
        summary_data = []
        all_detections = []
        detection_details = []
        defect_locations = []  # New: store GPS locations with defects
        
        tabs = st.tabs([f"Image {i+1}: {getattr(img, 'name', os.path.basename(img)) if is_upload else os.path.basename(img)}" 
                       for i, img in enumerate(image_list)])
        
        for idx, image_item in enumerate(image_list):
            # Update progress
            progress = (idx + 1) / len(image_list)
            progress_bar.progress(progress)
            status_text.text(f"Processing image {idx + 1} of {len(image_list)}...")
            
            # Load image based on source
            if is_upload:
                image = Image.open(image_item)
                image_name = image_item.name
                # Extract GPS data from uploaded file
                gps_data = get_gps_data(image_item)
            else:
                image_path = os.path.join(image_paths, image_item)
                image = Image.open(image_path)
                image_name = os.path.basename(image_path)
                # Extract GPS data from file path
                gps_data = get_gps_data(image_path)
            
            # Extract GPS coordinates
            latitude, longitude = extract_gps_coordinates(gps_data)
            
            # Convert to OpenCV format for processing
            image_np = np.array(image)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            # Perform inference
            results = model(image_bgr, conf=confidence_threshold)
            
            # Annotate image
            annotated_image = results[0].plot()
            
            # Process detections
            detections = []
            confidences = []
            for detection in results[0].boxes:
                label = int(detection.cls)
                confidence = float(detection.conf)
                bbox = detection.xyxy[0].tolist()
                detections.append({
                    "label": label,
                    "confidence": confidence,
                    "bbox": bbox
                })
                all_detections.append(confidence)
                confidences.append(confidence)
                
            detection_status = "Defects Detected" if detections else "No Defects"
            
            # If GPS data is available, add to defect locations
            if latitude is not None and longitude is not None:
                image_base64 = image_to_base64(image_item if is_upload else image_path)
                defect_locations.append({
                    'filename': image_name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'defects_count': len(detections),
                    'avg_confidence': sum(confidences) / len(confidences) if confidences else 0,
                    'max_confidence': max(confidences) if confidences else 0,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'image_base64': image_base64
                })
            
            # Prepare detection data for MongoDB (enhanced with GPS)
            detection_data = {
                "image_name": image_name,
                "status": detection_status,
                "defects_count": len(detections),
                "gps_data": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "has_gps": latitude is not None and longitude is not None
                },
                "detections": [
                    {
                        "label": d["label"],
                        "confidence": d["confidence"],
                        "bbox": d["bbox"]
                    } for d in detections
                ],
                "processing_time": time.time() - start_time
            }
            detection_details.append(detection_data)
            
            # Add to summary
            summary_data.append({
                "Image Name": image_name,
                "Status": detection_status,
                "Defects Count": len(detections),
                "Avg Confidence": sum([d["confidence"] for d in detections]) / len(detections) if detections else 0,
                "GPS Available": "✅" if latitude is not None else "❌",
                "Latitude": f"{latitude:.6f}" if latitude else "N/A",
                "Longitude": f"{longitude:.6f}" if longitude else "N/A",
                "Processing Time": f"{(time.time() - start_time) / (idx + 1):.2f}s"
            })
            
            # Display in tab
            with tabs[idx]:
                st.markdown(f"#### {image_name}")
                
                # GPS Status
                if latitude is not None and longitude is not None:
                    st.markdown(f'''
                    <div class="gps-info-box">
                        📍 <strong>GPS Location Available</strong><br>
                        Latitude: {latitude:.6f} | Longitude: {longitude:.6f}
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div style="background: #fff3cd; color: #856404; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid #ffc107;">
                        📍 <strong>No GPS Data Available</strong><br>
                        This image doesn't contain GPS coordinates
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Status indicator
                if detection_status == "Defects Detected":
                    st.markdown(f'''
                    <div class="defect-detected">
                        ⚠️ <span class="status-warning">{detection_status}</span> - Found {len(detections)} potential issues
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="no-defect">
                        ✅ <span class="status-ok">{detection_status}</span> - Track appears normal
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Image comparison
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                    st.image(image, caption="Original Image", use_column_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                    st.image(annotated_image, caption="Detected Issues", use_column_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                # Detection details
                if detections:
                    st.markdown('<div class="sub-header">Detection Details</div>', unsafe_allow_html=True)
                    
                    # Create a dataframe for better visualization
                    df_detections = pd.DataFrame([
                        {"Label": d["label"], "Confidence": f"{d['confidence']:.2f}", "Confidence_Value": d["confidence"]} 
                        for d in detections
                    ])
                    
                    # Bar chart visualization
                    if not df_detections.empty:
                        fig = px.bar(
                            df_detections, 
                            x="Label", 
                            y="Confidence_Value", 
                            color="Label",
                            labels={"Confidence_Value": "Confidence Score", "Label": "Defect Type"},
                            title="Defect Detection Confidence Scores",
                            height=300
                        )
                        fig.update_layout(yaxis_range=[0, 1])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed table
                    st.dataframe(
                        df_detections[["Label", "Confidence"]],
                        use_container_width=True,
                        hide_index=True
                    )
        
        # Complete progress
        progress_bar.progress(1.0)
        status_text.text("Processing complete!")
        
        # Save to MongoDB
        detection_id = save_detection_to_db({
            "summary": summary_data,
            "details": detection_details,
            "gps_locations": defect_locations
        })
        
        if detection_id:
            st.success(f"Results saved to database with ID: {detection_id}")
        
        # Update metrics
        total_time = time.time() - start_time
        gps_count = sum(1 for item in summary_data if item["GPS Available"] == "✅")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="stat-number">{len(image_list)}</div>
                <div class="stat-label">📷 Total Images</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            defect_count = sum(1 for item in summary_data if item["Status"] == "Defects Detected")
            st.markdown(f"""
            <div class="metric-container">
                <div class="stat-number">{defect_count}</div>
                <div class="stat-label">🚨 Defects Found</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="stat-number">{gps_count}</div>
                <div class="stat-label">📍 GPS Available</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_conf = f"{sum(all_detections) / len(all_detections) * 100:.1f}%" if all_detections else "0%"
            st.markdown(f"""
            <div class="metric-container">
                <div class="stat-number">{total_time:.1f}s</div>
                <div class="stat-label">⏱️ Total Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        # GPS Map Section
        if show_gps_map and defect_locations:
            st.markdown('<div class="sub-header">🗺️ Defect Location Map</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="gps-info-box">
                <strong>🎯 Interactive Map Features:</strong><br>
                • 🚨 Red markers: High-risk locations (3+ defects)<br>
                • ⚠️ Orange markers: Medium-risk locations (1-2 defects)<br>
                • ✅ Green markers: Safe locations (no defects)<br>
                • Click markers to view detailed defect information and images
            </div>
            """, unsafe_allow_html=True)
            
            defect_map = create_defect_map(defect_locations)
            if defect_map:
                st.markdown('<div class="map-container">', unsafe_allow_html=True)
                st_folium(defect_map, width=None, height=map_height, returned_objects=["last_object_clicked"])
                st.markdown('</div>', unsafe_allow_html=True)
            
            # GPS Statistics
            st.markdown('<div class="sub-header">📊 GPS Coverage Statistics</div>', unsafe_allow_html=True)
            
            if len(defect_locations) > 1:
                # Calculate coverage area
                lats = [loc['latitude'] for loc in defect_locations]
                lons = [loc['longitude'] for loc in defect_locations]
                
                lat_range = max(lats) - min(lats)
                lon_range = max(lons) - min(lons)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="stat-number">{lat_range:.4f}°</div>
                        <div class="stat-label">📐 Latitude Range</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="stat-number">{lon_range:.4f}°</div>
                        <div class="stat-label">📐 Longitude Range</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    center_lat = sum(lats) / len(lats)
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="stat-number">{center_lat:.3f}°</div>
                        <div class="stat-label">🎯 Center Lat</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    center_lon = sum(lons) / len(lons)
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="stat-number">{center_lon:.3f}°</div>
                        <div class="stat-label">🎯 Center Lon</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        elif show_gps_map and not defect_locations:
            st.markdown("""
            <div style="background: #fff3cd; color: #856404; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                📍 <strong>No GPS Data Available</strong><br>
                None of the processed images contain GPS coordinates. To see location mapping, ensure your images have GPS metadata.
            </div>
            """, unsafe_allow_html=True)
        
        # Display Summary Table
        st.markdown('<div class="sub-header">Detection Summary</div>', unsafe_allow_html=True)
        summary_df = pd.DataFrame(summary_data)
        
        # Add styling to the dataframe
        def highlight_defects(row):
            if row["Status"] == "Defects Detected":
                return ['background-color: #FEF2F2'] * len(row)
            return ['background-color: #ECFDF5'] * len(row)
        
        styled_df = summary_df.style.apply(highlight_defects, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # Enhanced Export Section
        st.markdown('<div class="sub-header">📥 Export Data</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV Export
            csv_data = summary_df.to_csv(index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"railway_detection_with_gps_{timestamp}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON Export with GPS data
            export_data = {
                "detection_summary": summary_data,
                "gps_locations": defect_locations,
                "metadata": {
                    "total_images": len(image_list),
                    "total_defects": sum(1 for item in summary_data if item["Status"] == "Defects Detected"),
                    "gps_coverage": f"{gps_count}/{len(image_list)}",
                    "processing_time": f"{total_time:.2f}s",
                    "timestamp": datetime.now().isoformat()
                }
            }
            json_data = json.dumps(export_data, indent=2)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"railway_detection_with_gps_{timestamp}.json",
                mime="application/json"
            )
        
        with col3:
            # GPS-only Export
            if defect_locations:
                gps_df = pd.DataFrame([{
                    'Image': loc['filename'],
                    'Latitude': loc['latitude'],
                    'Longitude': loc['longitude'],
                    'Defects': loc['defects_count'],
                    'Risk_Level': 'HIGH' if loc['defects_count'] > 2 else 'MEDIUM' if loc['defects_count'] > 0 else 'SAFE',
                    'Avg_Confidence': f"{loc['avg_confidence']:.2%}",
                    'Timestamp': loc['timestamp']
                } for loc in defect_locations])
                
                gps_csv = gps_df.to_csv(index=False)
                st.download_button(
                    label="📍 Download GPS Data",
                    data=gps_csv,
                    file_name=f"defect_locations_{timestamp}.csv",
                    mime="text/csv"
                )
            else:
                st.button("📍 No GPS Data", disabled=True)
        
        # Summary visualization if multiple images
        if len(image_list) > 1:
            st.markdown('<div class="sub-header">Analysis Results</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Create a pie chart for defect distribution
                status_count = summary_df["Status"].value_counts().reset_index()
                status_count.columns = ["Status", "Count"]
                
                fig = px.pie(
                    status_count,
                    values="Count",
                    names="Status",
                    title="Defect Detection Results",
                    color="Status",
                    color_discrete_map={
                        "Defects Detected": "#EF4444",
                        "No Defects": "#10B981"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # GPS Coverage Chart
                gps_status = summary_df["GPS Available"].value_counts().reset_index()
                gps_status.columns = ["GPS Status", "Count"]
                
                fig2 = px.pie(
                    gps_status,
                    values="Count",
                    names="GPS Status",
                    title="GPS Data Coverage",
                    color="GPS Status",
                    color_discrete_map={
                        "✅": "#10B981",
                        "❌": "#EF4444"
                    }
                )
                st.plotly_chart(fig2, use_container_width=True)

    # Handle different input methods
    if model_loaded:
        if input_method == "Folder with Images" and folder_path:
            if os.path.isdir(folder_path):
                st.success(f"📁 Found folder: `{folder_path}`")
                image_files = [
                    f for f in os.listdir(folder_path)
                    if f.lower().endswith(("jpg", "jpeg", "png"))
                ]
                
                if image_files:
                    st.info(f"🔍 Found {len(image_files)} image(s)")
                    
                    # Start processing button
                    if st.button("▶️ Start Processing with GPS Mapping", key="start_folder"):
                        process_images_with_gps(image_files, folder_path, is_upload=False)
                else:
                    st.warning("⚠️ No valid images found in the folder.")
            else:
                st.error("🚫 The specified folder does not exist.")
        
        elif input_method == "Upload Images" and uploaded_files:
            st.success(f"📁 {len(uploaded_files)} image(s) uploaded successfully")
            
            # Start processing button
            if st.button("▶️ Start Processing with GPS Mapping", key="start_upload"):
                process_images_with_gps(uploaded_files, is_upload=True)
        
        elif input_method == "Folder with Images":
            st.info("📝 Please enter a folder path to get started.")
        
        elif input_method == "Upload Images":
            st.info("📤 Please upload image files to get started.")
    else:
        st.error("⚠️ Model could not be loaded. Please check if the model file exists at './yolo11x/best.pt'")

# Main application flow
if not st.session_state.logged_in:
    show_login_ui()
else:
    show_main_app()

# Footer
st.markdown("""
<div class="footer">
    Railway Track Defect Detection System with GPS Mapping | Enhanced 2025
</div>
""", unsafe_allow_html=True)