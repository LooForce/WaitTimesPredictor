import pandas as pd

def add_time_features(df):
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['hour'] = df['Date'].dt.hour
    df['dayofweek'] = df['Date'].dt.dayofweek
    df['month'] = df['Date'].dt.month
    df['day'] = df['Date'].dt.day
    return df

def add_lag_features(df, lags=[1, 2, 3, 6, 12]):
    # lags are in number of rows (e.g., 5-min intervals)
    for lag in lags:
        df[f'wait_lag_{lag}'] = df['Wait'].shift(lag)
    # Rolling mean for past hour (if 5-min intervals, 12 rows = 1 hour)
    df['wait_roll1h'] = df['Wait'].rolling(window=12).mean()
    return df