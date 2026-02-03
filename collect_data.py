import os
import requests
import csv
import json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

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

def get_last_hour(ride_id):
    now = datetime.now()
    year = now.year
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"
    url = f"https://queue-times.com/en-US/parks/16/rides/{ride_id}?given_date={year}-{month}-{day}"
    page = requests.get(url)
    doc = BeautifulSoup(page.content, "html.parser")
    try:
        front_index = doc.find_all('script')[7].text.index("2ecc71") + 12
        end_index = doc.find_all('script')[7].text.index("Reported closed") - 14
        script = doc.find_all('script')[7].text.strip()[front_index:end_index]
        data = json.loads(script)  # convert to object

        # Convert to DataFrame for easy filtering
        df = pd.DataFrame(data, columns=['Date', 'Wait'])
        df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%y %H:%M:%S")
        df['Wait'] = df['Wait'].astype(float)

        # Get the latest timestamp in the data
        last_time = df['Date'].max()
        one_hour_ago = last_time - timedelta(hours=1)
        last_hour_df = df[df['Date'] > one_hour_ago].sort_values('Date')

        # Return as a list of [date_str, wait_float]
        result = last_hour_df[['Date', 'Wait']].values.tolist()
        if result == None:
            print(f"Ride ID {ride_id} has no data in the last hour.")
        return result
        
    except (IndexError, ValueError, json.JSONDecodeError) as e:
        print(f"{month}/{day}/{year} not found")
        return []

def get_day(ride_id, year=2026, month=None, day=None):
    url = f"https://queue-times.com/en-US/parks/16/rides/{ride_id}?given_date={year}-{month}-{day}"
    page = requests.get(url)
    doc = BeautifulSoup(page.content, "html.parser")
    print("DOC RECEIVED")
    try:
        front_index = doc.find_all('script')[7].text.index("2ecc71") + 12
        end_index = doc.find_all('script')[7].text.index("Reported closed") - 14
        script = doc.find_all('script')[7].text.strip()[front_index:end_index]
        data = json.loads(script)  # convert to object

        # Convert to DataFrame for easy filtering
        df = pd.DataFrame(data, columns=['Date', 'Wait'])
        df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%y %H:%M:%S")
        df['Wait'] = df['Wait'].astype(float)

        # Sort and return all today's data
        df = df.sort_values('Date')
        result = df[['Date', 'Wait']].values.tolist()

        if not result:
            print(f"Ride ID {ride_id} has no data for {month}/{day}/{year}.")

        return result
        
    except (IndexError, ValueError, json.JSONDecodeError) as e:
        print(f"{month}/{day}/{year} not found")
        return []

if __name__ == "__main__":
    pass