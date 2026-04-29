# from flask import Flask, request, jsonify
# import sqlite3
# import folium
# from ultralytics import YOLO
# import cv2
# import numpy as np

# model = YOLO("runs/detect/train10/weights/best_finetuned.pt")


# app = Flask(__name__)

# DB_NAME = "potholes.db"


# # -------------------------
# # Database initialization
# # -------------------------

# def init_db():

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS potholes (

#         id INTEGER PRIMARY KEY AUTOINCREMENT,

#         latitude REAL,
#         longitude REAL,

#         severity TEXT,

#         status TEXT DEFAULT 'ACTIVE',

#         report_count INTEGER DEFAULT 1,

#         repair_votes INTEGER DEFAULT 0,

#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

#         last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
#     """)

#     conn.commit()
#     conn.close()


# init_db()


# @app.route("/")
# def home():

#     return "Smart Pothole Backend Running"


# from datetime import datetime
# from math import radians, cos, sin, sqrt, atan2


# # -------------------------
# # Distance calculation
# # -------------------------

# def distance(lat1, lon1, lat2, lon2):

#     R = 6371000

#     dlat = radians(lat2 - lat1)
#     dlon = radians(lon2 - lon1)

#     a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2

#     c = 2 * atan2(sqrt(a), sqrt(1-a))

#     return R * c


# # -------------------------
# # Report pothole API
# # -------------------------

# @app.route("/report_pothole", methods=["POST"])
# def report_pothole():

#     data = request.json

#     latitude = data["latitude"]
#     longitude = data["longitude"]
#     severity = data["severity"]

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()


#     # Check duplicate pothole within 10 meters
#     cursor.execute("SELECT * FROM potholes WHERE status='ACTIVE'")
#     potholes = cursor.fetchall()


#     for pothole in potholes:

#         existing_lat = pothole[1]
#         existing_lon = pothole[2]

#         if distance(latitude, longitude,
#                     existing_lat, existing_lon) < 10:

#             cursor.execute("""

#                 UPDATE potholes

#                 SET report_count = report_count + 1,
#                     last_seen_at = CURRENT_TIMESTAMP

#                 WHERE id = ?

#             """, (pothole[0],))

#             conn.commit()
#             conn.close()

#             return jsonify({"message": "Duplicate pothole updated"})


#     # Insert new pothole
#     cursor.execute("""

#         INSERT INTO potholes
#         (latitude, longitude, severity)

#         VALUES (?, ?, ?)

#     """, (latitude, longitude, severity))


#     conn.commit()
#     conn.close()

#     return jsonify({"message": "New pothole recorded"})

# @app.route("/active_potholes", methods=["GET"])
# def active_potholes():

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM potholes WHERE status='ACTIVE'")

#     potholes = cursor.fetchall()

#     conn.close()

#     return jsonify(potholes)

# @app.route("/all_potholes", methods=["GET"])
# def all_potholes():

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM potholes")

#     potholes = cursor.fetchall()

#     pothole_list = []

#     for pothole in potholes:

#         pothole_list.append({

#             "id": pothole[0],
#             "latitude": pothole[1],
#             "longitude": pothole[2],
#             "severity": pothole[3],
#             "status": pothole[4],
#             "report_count": pothole[5],
#             "repair_votes": pothole[6],
#             "created_at": pothole[7],
#             "last_seen_at": pothole[8]

#         })

#     conn.close()

#     return jsonify(pothole_list)

# @app.route("/potholes_map")
# def potholes_map():

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM potholes")

#     potholes = cursor.fetchall()

#     conn.close()


#     # Default map center (fallback)
#     center_lat = 8.5241
#     center_lon = 76.9366


#     if potholes:
#         center_lat = potholes[0][1]
#         center_lon = potholes[0][2]


#     pothole_map = folium.Map(
#         location=[center_lat, center_lon],
#         zoom_start=14
#     )


#     for pothole in potholes:

#         lat = pothole[1]
#         lon = pothole[2]
#         severity = pothole[3]
#         status = pothole[4]


#         if severity == "LOW":
#             color = "green"

#         elif severity == "MEDIUM":
#             color = "orange"

#         else:
#             color = "red"


#         folium.Marker(
#             location=[lat, lon],
#             popup=f"Severity: {severity} | Status: {status}",
#             icon=folium.Icon(color=color)
#         ).add_to(pothole_map)

#     return pothole_map._repr_html_()

# @app.route("/nearby_potholes", methods=["GET"])
# def nearby_potholes():

#     latitude = float(request.args.get("lat"))
#     longitude = float(request.args.get("lon"))

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM potholes WHERE status='ACTIVE'")
#     potholes = cursor.fetchall()

#     nearby_list = []

#     for pothole in potholes:

#         pothole_id = pothole[0]
#         pothole_lat = pothole[1]
#         pothole_lon = pothole[2]
#         severity = pothole[3]

#         dist = distance(latitude, longitude,
#                         pothole_lat, pothole_lon)

#         if dist <= 200:

#             nearby_list.append({

#                 "id": pothole_id,
#                 "latitude": pothole_lat,
#                 "longitude": pothole_lon,
#                 "severity": severity,
#                 "distance": round(dist, 2)

#             })

#     conn.close()

#     return jsonify(nearby_list)

# @app.route("/confirm_repair", methods=["POST"])
# def confirm_repair():

#     data = request.json

#     pothole_id = data["id"]

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("""
#         UPDATE potholes
#         SET repair_votes = repair_votes + 1
#         WHERE id = ?
#     """, (pothole_id,))

#     cursor.execute("""
#         SELECT repair_votes
#         FROM potholes
#         WHERE id = ?
#     """, (pothole_id,))

#     votes = cursor.fetchone()[0]

#     # threshold = 3 confirmations
#     if votes >= 3:

#         cursor.execute("""
#             UPDATE potholes
#             SET status = 'FIXED'
#             WHERE id = ?
#         """, (pothole_id,))

#     conn.commit()
#     conn.close()

#     return jsonify({"message": "Repair vote recorded"})

# @app.route("/detect_from_mobile", methods=["POST"])
# def detect_from_mobile():

#     file = request.files["image"]

#     latitude = request.form["latitude"]
#     longitude = request.form["longitude"]

#     image_bytes = file.read()

#     npimg = np.frombuffer(image_bytes, np.uint8)

#     frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#     results = model(frame)

#     boxes = results[0].boxes

#     if len(boxes) > 0:

#         severity = "HIGH"

#         cursor = sqlite3.connect(DB_NAME).cursor()

#         cursor.execute("""
#         INSERT INTO potholes
#         (latitude, longitude, severity)
#         VALUES (?, ?, ?)
#         """, (latitude, longitude, severity))

#     return jsonify({"status": "processed"})

# @app.route("/auto_repair_check", methods=["POST"])
# def auto_repair_check():

#     data = request.json

#     latitude = data["latitude"]
#     longitude = data["longitude"]

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT id, latitude, longitude, repair_votes
#         FROM potholes
#         WHERE status='ACTIVE'
#     """)

#     potholes = cursor.fetchall()

#     updated = []

#     for pothole in potholes:

#         pothole_id = pothole[0]
#         pothole_lat = pothole[1]
#         pothole_lon = pothole[2]
#         votes = pothole[3]

        
#         if distance(latitude, longitude,
#                     pothole_lat, pothole_lon) < 10:

#             votes += 1

#             cursor.execute("""
#                 UPDATE potholes
#                 SET repair_votes = ?
#                 WHERE id = ?
#             """, (votes, pothole_id))

            
#             if votes >= 3:

#                 cursor.execute("""
#                     UPDATE potholes
#                     SET status = 'FIXED'
#                     WHERE id = ?
#                 """, (pothole_id,))

#             updated.append(pothole_id)

#     conn.commit()
#     conn.close()

#     return jsonify({
#         "updated_potholes": updated
#     })


# if __name__ == "__main__":

#     app.run(debug=True)




from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import psycopg2
import os
# import sqlite3
import folium
from ultralytics import YOLO
import cv2
import numpy as np
from math import radians, cos, sin, sqrt, atan2
from datetime import datetime
from typing import List

# Initialize FastAPI and YOLO
app = FastAPI(title="Smart Pothole Detection API")
model = YOLO("backend/best_finetuned.pt")
# DB_NAME = "potholes.db"
DATABASE_URL = os.getenv("DATABASE_URL")
def get_connection():
    return psycopg2.connect(DATABASE_URL)

# Pydantic models for data validation
class PotholeBase(BaseModel):
    latitude: float
    longitude: float
    severity: str

class RepairVote(BaseModel):
    id: int

# -------------------------
# Database initialization
# -------------------------
def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS potholes (

        id SERIAL PRIMARY KEY,

        latitude DOUBLE PRECISION,

        longitude DOUBLE PRECISION,

        severity TEXT,

        status TEXT DEFAULT 'ACTIVE',

        report_count INTEGER DEFAULT 1,

        repair_votes INTEGER DEFAULT 0,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    conn.commit()
    conn.close()
init_db()

# -------------------------
# Helper Functions
# -------------------------
def distance(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# -------------------------
# API Endpoints
# -------------------------

@app.get("/")
async def home():
    return {"message": "Smart Pothole Backend Running"}

@app.post("/report_pothole")
async def report_pothole(data: PotholeBase):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM potholes WHERE status='ACTIVE'")
    potholes = cursor.fetchall()

    for pothole in potholes:
        if distance(data.latitude, data.longitude, pothole[1], pothole[2]) < 10:
            cursor.execute("""
                UPDATE potholes 
                SET report_count = report_count + 1, last_seen_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """, (pothole[0],))
            conn.commit()
            conn.close()
            return {"message": "Duplicate pothole updated"}

    cursor.execute("INSERT INTO potholes (latitude, longitude, severity) VALUES (%s, %s, %s)",
                   (data.latitude, data.longitude, data.severity))
    conn.commit()
    conn.close()
    return {"message": "New pothole recorded"}

@app.get("/all_potholes")
async def all_potholes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM potholes")
    potholes = cursor.fetchall()
    conn.close()
    
    return [{
        "id": p[0], "latitude": p[1], "longitude": p[2], "severity": p[3],
        "status": p[4], "report_count": p[5], "repair_votes": p[6]
    } for p in potholes]

@app.get("/potholes_map", response_class=HTMLResponse)
async def potholes_map():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM potholes")
    potholes = cursor.fetchall()
    conn.close()

    center = [potholes[0][1], potholes[0][2]] if potholes else [8.5241, 76.9366]
    p_map = folium.Map(location=center, zoom_start=14)

    for p in potholes:
        color = "green" if p[3] == "LOW" else "orange" if p[3] == "MEDIUM" else "red"
        folium.Marker([p[1], p[2]], popup=f"Severity: {p[3]}", icon=folium.Icon(color=color)).add_to(p_map)

    return p_map._repr_html_()

@app.post("/detect_from_mobile")
async def detect_from_mobile(latitude: float = Form(...), longitude: float = Form(...), image: UploadFile = File(...)):
    contents = await image.read()
    npimg = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    results = model(frame)
    if len(results[0].boxes) > 0:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO potholes (latitude, longitude, severity) VALUES (%s, %s, %s)",
                       (latitude, longitude, "HIGH"))
        conn.commit()
        conn.close()
        return {"status": "detected", "message": "Pothole recorded"}
    
    return {"status": "none", "message": "No pothole detected"}

# Add this to your FastAPI server.py if missing
@app.get("/nearby_potholes")
async def nearby_potholes(lat: float, lon: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM potholes WHERE status='ACTIVE'")
    potholes = cursor.fetchall()
    conn.close()

    nearby_list = []
    for p in potholes:
        dist = distance(lat, lon, p[1], p[2])
        if dist <= 200: # 200 meters
            nearby_list.append({
                "id": p[0],
                "latitude": p[1],
                "longitude": p[2],
                "severity": p[3],
                "distance": round(dist, 2)
            })
    return nearby_list


@app.post("/auto_repair_check")
async def auto_repair_check(lat: float, lon: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, latitude, longitude, repair_votes FROM potholes WHERE status='ACTIVE'")
    potholes = cursor.fetchall()
    
    updated = []
    for p_id, p_lat, p_lon, votes in potholes:
        if distance(lat, lon, p_lat, p_lon) < 10:
            new_votes = votes + 1
            status = 'FIXED' if new_votes >= 3 else 'ACTIVE'
            cursor.execute("UPDATE potholes SET repair_votes = %s, status = %s WHERE id = %s", (new_votes, status, p_id))
            updated.append(p_id)
            
    conn.commit()
    conn.close()
    return {"updated_ids": updated}

if __name__ == "__main__":
    import uvicorn
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 10000)) 
    uvicorn.run(app, host="0.0.0.0", port=port)
