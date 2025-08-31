import requests
import csv
from datetime import datetime

QUEUE_API = "https://queue-times.com/parks/16/queue_times.json"

def collect():
    response = requests.get(QUEUE_API)
    data = response.json()
    now = datetime.now()
    
    # Open CSV in append mode
    with open("wait_times.csv", "a", newline="") as file:
        writer = csv.writer(file)
        for ride in data['queues']:  # adjust key based on actual API response
            writer.writerow([
                now.strftime("%Y-%m-%d %H:%M:%S"),
                ride['name'],
                ride['waitTime']  # might be ride['wait_time'] depending on API
            ])
            
if __name__ == "__main__":
    collect()