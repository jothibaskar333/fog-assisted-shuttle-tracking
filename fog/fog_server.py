from flask import Flask, request, jsonify
import math
import time

app = Flask(__name__)

# 1. CAMPUS DATA (Ensure these names exactly match SHUTTLE_ROUTE)
CAMPUS_BLOCKS = {
    "SMV": (12.9692, 79.1559), "MB": (12.9710, 79.1580),
    "TT": (12.9725, 79.1600), "PRP": (12.9740, 79.1620),
    "SJT": (12.9755, 79.1640), "MGB": (12.9730, 79.1660),
    "ALM": (12.9715, 79.1680), "CDMM": (12.9695, 79.1700),
    "GH_A": (12.9675, 79.1685), "BH_A": (12.9660, 79.1660)
}

# The single source of truth for the shuttle path
SHUTTLE_ROUTE = ["SMV", "MB", "TT", "PRP", "SJT", "MGB", "ALM", "CDMM", "GH_A", "BH_A"]

# Initial State
shuttle_state = {
    "SHUTTLE_01": {
        "shuttle_id": "SHUTTLE_01",
        "latitude": CAMPUS_BLOCKS["SMV"][0],
        "longitude": CAMPUS_BLOCKS["SMV"][1],
        "current_block": "SMV",
        "last_update": 0,
    },
    "SHUTTLE_02": {
        "shuttle_id": "SHUTTLE_02",
        "latitude": CAMPUS_BLOCKS["PRP"][0],
        "longitude": CAMPUS_BLOCKS["PRP"][1],
        "current_block": "PRP",
        "last_update": 0,
    },
    "SHUTTLE_03": {
        "shuttle_id": "SHUTTLE_03",
        "latitude": CAMPUS_BLOCKS["ALM"][0],
        "longitude": CAMPUS_BLOCKS["ALM"][1],
        "current_block": "ALM",
        "last_update": 0,
    },
}

# --- HELPER FUNCTIONS ---

def calculate_haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance in meters using Haversine formula."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Timing constants for ETA calculations
TRAVEL_SECONDS_PER_LEG = 21.0
STOP_DWELL_SECONDS = 6.0

def legs_forward(from_block, to_block):
    if from_block not in SHUTTLE_ROUTE or to_block not in SHUTTLE_ROUTE:
        return 0
    n = len(SHUTTLE_ROUTE)
    i = SHUTTLE_ROUTE.index(from_block)
    j = SHUTTLE_ROUTE.index(to_block)
    return (j - i) % n

def eta_seconds_to_stop(sid, destination_block):
    if sid not in shuttle_state:
        return None
    
    state = shuttle_state[sid]
    curr_block = state.get("current_block")
    lat, lon = state.get("latitude"), state.get("longitude")
    
    if curr_block not in SHUTTLE_ROUTE or destination_block not in SHUTTLE_ROUTE:
        return None

    legs = legs_forward(curr_block, destination_block)
    if legs == 0:
        return 0

    # Progress along current leg
    idx = SHUTTLE_ROUTE.index(curr_block)
    next_block = SHUTTLE_ROUTE[(idx + 1) % len(SHUTTLE_ROUTE)]
    
    p1_lat, p1_lon = CAMPUS_BLOCKS[curr_block]
    p2_lat, p2_lon = CAMPUS_BLOCKS[next_block]
    
    seg_len = calculate_haversine(p1_lat, p1_lon, p2_lat, p2_lon)
    dist_to_next = calculate_haversine(lat, lon, p2_lat, p2_lon)
    
    frac_remaining = max(0.0, min(1.0, dist_to_next / seg_len)) if seg_len > 0 else 0
    time_to_next = frac_remaining * TRAVEL_SECONDS_PER_LEG
    
    # Add time for all subsequent legs
    remaining_full_legs = max(0, legs - 1)
    total = time_to_next + (remaining_full_legs * (STOP_DWELL_SECONDS + TRAVEL_SECONDS_PER_LEG))
    
    return int(round(total))

# --- API ROUTES ---

@app.route("/update", methods=["POST"])
def update_location():
    data = request.json
    sid = data.get('shuttle_id')
    lat, lon = data.get("latitude"), data.get("longitude")

    if not sid or lat is None or lon is None:
        return jsonify({"error": "Invalid Data"}), 400

    # Find the nearest block to update the status text
    distances = {name: calculate_haversine(lat, lon, coords[0], coords[1]) 
                 for name, coords in CAMPUS_BLOCKS.items()}
    nearest_block = min(distances, key=distances.get)

    if sid not in shuttle_state:
        shuttle_state[sid] = {"shuttle_id": sid}

    shuttle_state[sid].update({
        "latitude": lat,
        "longitude": lon,
        "current_block": nearest_block,
        "last_update": int(time.time())
    })

    return jsonify({"status": "success"})

@app.route("/status", methods=["GET"])
@app.route("/shuttle_data", methods=["GET"])
def get_status():
    status_data = {}
    for sid, state in shuttle_state.items():
        curr = state["current_block"]
        
        # Calculate next destination in the circular route
        try:
            idx = SHUTTLE_ROUTE.index(curr)
            dest = SHUTTLE_ROUTE[(idx + 1) % len(SHUTTLE_ROUTE)]
        except ValueError:
            dest = "Unknown"

        status_data[sid] = {
            "shuttle_id": sid,
            "current_block": curr,
            "destination": dest,
            "latitude": state.get("latitude"),
            "longitude": state.get("longitude")
        }
    return jsonify(status_data)

@app.route("/shuttle_eta", methods=["GET"])
def get_eta():
    sid = request.args.get('shuttle_id')
    user_stop = request.args.get('destination')
    
    eta = eta_seconds_to_stop(sid, user_stop) if sid and user_stop else None
    
    if eta is None:
        return jsonify({"error": "Invalid shuttle_id or destination"}), 400
    
    return jsonify({
        "shuttle_id": sid, 
        "destination": user_stop, 
        "eta_seconds": eta
    })

if __name__ == "__main__":
    app.run(port=5001, debug=True)