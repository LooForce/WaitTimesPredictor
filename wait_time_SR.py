import os
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

DATA_FOLDER = "QueueTimesData"

def get_ride_data(csv_file, ride_id, month, day):
    url = f"https://queue-times.com/en-US/parks/16/rides/{ride_id}?given_date=2025-{month}-{day}"
    page = requests.get(url)
    doc = BeautifulSoup(page.content, "lxml")
    # scrape the data
    try:
        front_index = doc.find_all('script')[7].text.index("2ecc71") + 12
        end_index = doc.find_all('script')[7].text.index("Reported closed") - 14
        script = doc.find_all('script')[7].text.strip()[front_index:end_index]
        data = json.loads(script)  # convert to object

        df1 = pd.DataFrame(data, columns=['Date', 'Wait'])
        df1['Date'] = pd.to_datetime(df1['Date'], format="%m/%d/%y %H:%M:%S").dt.floor("min")
        df1['Wait'] = df1['Wait'].astype(float)
        df1['Wait'] = df1['Wait'].astype(int)
        # Ensure the data folder exists
        os.makedirs(DATA_FOLDER, exist_ok=True)
        df1.to_csv(os.path.join(DATA_FOLDER, csv_file), mode='a', index=False, header=False)
        print(day, end=" ")
    except (IndexError, ValueError, json.JSONDecodeError) as e:
        print(f"{day} not found")

def collect_ride_data(csv_file, ride_id, months):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    df = pd.DataFrame(columns=['Date', 'Wait'])
    df.to_csv(os.path.join(DATA_FOLDER, csv_file), mode='w', index=False, header=True)
    for month in months:
        for i in range(30):
            get_ride_data(csv_file, ride_id, month, i+1)

def load_ride_data(csv_file):
    df = pd.read_csv(os.path.join(DATA_FOLDER, csv_file))
    df.index = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
    return df

def plot_ride_data(csv_file):
    import matplotlib.pyplot as plt
    df = load_ride_data(csv_file)
    wait = df['Wait']
    wait.plot()
    plt.xlabel("Date")
    plt.ylabel("Wait Time (min)")
    plt.title("Ride Wait Times")
    plt.show()

# Example usage (uncomment to run as a script)
if __name__ == "__main__":
    csv_file = "spacemountain.csv"
    ride_id = "284"  # Replace with actual ride ID
    months = "1"  # Replace with desired months
    collect_ride_data(csv_file, ride_id, months)
    plot_ride_data(csv_file)