from flask import Flask, render_template, jsonify, request
import requests
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# CHANGE: template_folder points to '1templates' as per your structure
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'))

FOG_STATUS_ENDPOINT = "http://127.0.0.1:5001/status"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shuttle_data")
def shuttle_data():
    try:
        response = requests.get(FOG_STATUS_ENDPOINT)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/shuttle_eta", methods=["GET"])
def shuttle_eta():
    """
    Proxy ETA requests to the fog server.

    The frontend calls `/shuttle_eta?...` on this Flask server (8080),
    but the actual ETA endpoint lives on the fog server (5000).
    """
    shuttle_id = request.args.get("shuttle_id")
    destination = request.args.get("destination")
    try:
        response = requests.get(
            "http://127.0.0.1:5001/shuttle_eta",
            params={"shuttle_id": shuttle_id, "destination": destination},
            timeout=2,
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # CHANGE: Moved to port 8080 to avoid conflict with Fog Server
    app.run(host="0.0.0.0", port=8080, debug=True)