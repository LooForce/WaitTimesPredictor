from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

QUEUE_API = "https://queue-times.com/parks/16/queue_times.json"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/wait-times")
def wait_times():
    # Fetch Disneyland wait times
    queue_response = requests.get(QUEUE_API)
    queue_data = queue_response.json()
    
    # Add time data
    now = datetime.now()
    time_data = {
        "hour": now.hour,
        "weekday": now.weekday(),
        "month": now.month,
        "day": now.day
    }
    
    # Combine everything
    data = {
        "queue_times": queue_data,
        "time": time_data
    }
    
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
