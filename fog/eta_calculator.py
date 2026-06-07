import math

# Use the same coordinates from your fog_server.py
CAMPUS_BLOCKS = {
    "SMV": (12.9692, 79.1559), "MB": (12.9710, 79.1580),
    "TT": (12.9725, 79.1600), "PRP": (12.9740, 79.1620),
    "SJT": (12.9755, 79.1640), "MGB": (12.9730, 79.1660),
    "ALM": (12.9715, 79.1680), "CDMM": (12.9695, 79.1700),
    "GH_A": (12.9675, 79.1685), "BH_A": (12.9660, 79.1660)
}

ROUTE_ORDER = ["SMV", "MB", "TT", "PRP", "SJT", "MGB", "ALM", "CDMM", "GH_A", "BH_A"]

def calculate_haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def calculate_eta(current_lat, current_lon, destination_block):
    if not current_lat or not current_lon or not destination_block:
        return 0
    
    # 1. FIND NEAREST BLOCK
    distances = {name: calculate_haversine(current_lat, current_lon, c[0], c[1]) 
                 for name, c in CAMPUS_BLOCKS.items()}
    current_block = min(distances, key=distances.get)
    dist_to_closest = distances[current_block]

    # 2. ARRIVAL CHECK (15 meters threshold)
    if current_block == destination_block and dist_to_closest < 15:
        return 0

    # 3. SEGMENT LOGIC
    curr_idx = ROUTE_ORDER.index(current_block)
    next_idx = (curr_idx + 1) % len(ROUTE_ORDER)
    next_block = ROUTE_ORDER[next_idx]

    # 4. PATH CALCULATION (Walk the loop)
    total_meters = 0
    temp_idx = next_idx
    count = 0
    
    # Sum all full segments until we reach the destination block
    while ROUTE_ORDER[temp_idx] != destination_block and count < len(ROUTE_ORDER):
        p1 = ROUTE_ORDER[temp_idx]
        p2_idx = (temp_idx + 1) % len(ROUTE_ORDER)
        p2 = ROUTE_ORDER[p2_idx]
        
        total_meters += calculate_haversine(
            CAMPUS_BLOCKS[p1][0], CAMPUS_BLOCKS[p1][1],
            CAMPUS_BLOCKS[p2][0], CAMPUS_BLOCKS[p2][1]
        )
        temp_idx = p2_idx
        count += 1

    # 5. CURRENT LEG PROGRESS
    # Distance from current GPS point to the upcoming block
    dist_to_next = calculate_haversine(current_lat, current_lon, 
                                      CAMPUS_BLOCKS[next_block][0], 
                                      CAMPUS_BLOCKS[next_block][1])
    total_meters += dist_to_next

    # 6. CONVERT TO TIME
    # Speed (meters per second) should be tuned based on simulation settings
    speed_mps = 5.5 
    arrival_seconds = int(total_meters / speed_mps)

    return max(arrival_seconds, 10) # Minimum 10 seconds unless arrived