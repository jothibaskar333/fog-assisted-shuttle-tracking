import time
import requests
import threading

# The EXACT coordinates of the circle on your map
# Ensure these match the waypoints in your SVG/Map UI
ROUTE_COORDS = [
    (12.9692, 79.1559), (12.9710, 79.1580), (12.9725, 79.1600),
    (12.9740, 79.1620), (12.9755, 79.1640), (12.9730, 79.1660),
    (12.9715, 79.1680), (12.9695, 79.1700), (12.9675, 79.1685),
    (12.9660, 79.1660)
]

# Tuning for smooth "point-to-point" flow
STEPS_PER_SEGMENT = 25  # Smooths the line between points
TIME_STEP = 0.4         # Speed of the update

def run_shuttle(sid, start_idx):
    # Start at the assigned point in the loop
    current_idx = start_idx % len(ROUTE_COORDS)
    
    while True:
        # Get current point and the very next point in the circle
        start_node = ROUTE_COORDS[current_idx]
        next_idx = (current_idx + 1) % len(ROUTE_COORDS)
        end_node = ROUTE_COORDS[next_idx]
        
        # Interpolate between this point and the next to keep the movement fluid
        for s in range(STEPS_PER_SEGMENT):
            frac = s / STEPS_PER_SEGMENT
            lat = start_node[0] + (end_node[0] - start_node[0]) * frac
            lon = start_node[1] + (end_node[1] - start_node[1]) * frac
            
            try:
                # Tell the Fog server exactly where we are on the loop
                requests.post("http://127.0.0.1:5001/update", 
                              json={"shuttle_id": sid, "latitude": lat, "longitude": lon}, 
                              timeout=0.5)
            except:
                pass 
            
            time.sleep(TIME_STEP)

        # Move to the next point in the loop
        current_idx = next_idx

if __name__ == "__main__":
    # Spread shuttles evenly: One at index 0, one at index 3, one at index 6
    shuttles = [("SHUTTLE_01", 0), ("SHUTTLE_02", 3), ("SHUTTLE_03", 6)]
    
    for sid, start in shuttles:
        threading.Thread(target=run_shuttle, args=(sid, start), daemon=True).start()
    
    while True: time.sleep(1)
