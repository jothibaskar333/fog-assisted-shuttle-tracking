import requests
import time

FOG_STATUS_ENDPOINT = "http://127.0.0.1:5001/status"

def fetch_shuttle_status():
    response = requests.get(FOG_STATUS_ENDPOINT)
    return response.json()

if __name__ == "__main__":
    print("Cloud client started...\n")

    while True:
        data = fetch_shuttle_status()  # top-level JSON: {shuttle_id: {...}}

        if data:
            for shuttle_id, info in data.items():
                print(f"Shuttle ID   : {info.get('shuttle_id', 'N/A')}")
                print(f"Current Block: {info.get('current_block', 'N/A')}")
                print(f"Destination  : {info.get('destination', 'N/A')}")
                print(f"Latitude     : {info.get('latitude', 'N/A')}")
                print(f"Longitude    : {info.get('longitude', 'N/A')}")
                print(f"ETA          : {info.get('eta_seconds', 'N/A')} seconds")
                print("-" * 40)
        else:
            print("No shuttle data available yet.")

        time.sleep(3)
