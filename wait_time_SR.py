import os
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import calendar
from datetime import datetime, timedelta

DATA_FOLDER = "QueueTimesData"

def get_ride_data(csv_file, ride_id, month, day, year=datetime.now().year):
    url = f"https://queue-times.com/en-US/parks/16/rides/{ride_id}?given_date={year}-{month}-{day}"
    page = requests.get(url)
    doc = BeautifulSoup(page.content, "lxml")
    try:
        front_index = doc.find_all('script')[7].text.index("2ecc71") + 12
        end_index = doc.find_all('script')[7].text.index("Reported closed") - 14
        script = doc.find_all('script')[7].text.strip()[front_index:end_index]
        data = json.loads(script)
        df1 = pd.DataFrame(data, columns=['Date', 'Wait'])
        df1['Date'] = pd.to_datetime(df1['Date'], format="%m/%d/%y %H:%M:%S").dt.floor("min")
        df1['Wait'] = df1['Wait'].astype(float).astype(int)

        # Load existing data if it exists
        file_path = os.path.join(DATA_FOLDER, csv_file)
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path)
            existing_df['Date'] = pd.to_datetime(existing_df['Date'], format='%Y-%m-%d %H:%M:%S')
            # Only keep rows that are new
            df1 = df1[df1['Date'] > existing_df['Date'].max()]

        if not df1.empty:
            os.makedirs(DATA_FOLDER, exist_ok=True)
            df1.to_csv(file_path, mode='a', index=False, header=not os.path.exists(file_path))
        print(day, end=" ")
    except (IndexError, ValueError, json.JSONDecodeError) as e:
        print(f"{month}/{day}/{year} not found")

def collect_ride_data(csv_file, ride_id, months, year=datetime.now().year):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    file_path = os.path.join(DATA_FOLDER, csv_file)

    # Check the last date in the CSV to start fetching from the next day
    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)
        df_existing['Date'] = pd.to_datetime(df_existing['Date'], format='%Y-%m-%d %H:%M:%S')
        start_date = df_existing['Date'].max().date() + timedelta(days=1)
    else:
        start_date = datetime(year, int(months[0]), 1).date()
        df = pd.DataFrame(columns=['Date', 'Wait'])
        df.to_csv(file_path, mode='w', index=False, header=True)

    # Loop through months starting from start_date
    for month in months:
        month = int(month)
        days_in_month = calendar.monthrange(year, month)[1]

        for day in range(1, days_in_month + 1):
            current_date = datetime(year, month, day).date()
            if current_date >= start_date:
                get_ride_data(csv_file, ride_id, month, day, year)

def load_ride_data(csv_file):
    df = pd.read_csv(os.path.join(DATA_FOLDER, csv_file))
    df.index = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
    return df

def plot_ride_data(csv_file):
    import matplotlib.pyplot as plt
    df = load_ride_data(csv_file)
    df['Wait'].plot()
    plt.xlabel("Date")
    plt.ylabel("Wait Time (min)")
    plt.title("Ride Wait Times")
    plt.show()


if __name__ == "__main__":
    rides_df = pd.read_csv("rides.csv")
    cur_month = datetime.now().month
    months = [month for month in range(1, cur_month + 1)]

    for _, row in rides_df.iterrows():
        csv_file = f"{row['file_name'] + '.csv'}"
        ride_id = str(row['ride_id'])
        print(f"Collecting data for {row['ride_name']}...")
        collect_ride_data(csv_file, ride_id, months)
        print(f"\nDone with {row['ride_name']}.")

    print("All data collected.")