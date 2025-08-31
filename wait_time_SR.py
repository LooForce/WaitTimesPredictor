import os
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

DATA_FOLDER = "QueueTimesData"

def get_ride_data(csv_file, ride_id, month, day, year=2025):
    url = f"https://queue-times.com/en-US/parks/16/rides/{ride_id}?given_date={year}-{month}-{day}"
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
        print(f"{month}/{day}/{year} not found")

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

if __name__ == "__main__":
    rides_df = pd.read_csv("rides.csv")
    months = "1 2 3 4 5 6 7 8".split()  # Replace with desired months

    for _, row in rides_df.iterrows():
        csv_file = f"{row['ride_name']}.csv"
        ride_id = str(row['ride_id'])
        print(f"Collecting data for {row['ride_name']}...")
        collect_ride_data(csv_file, ride_id, months)
        print(f"Done with {row['ride_name']}.")

    print("All data collected.")