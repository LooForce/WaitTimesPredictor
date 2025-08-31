import pandas as pd

def add_time_features(df):
    df = df.copy()
    df['hour'] = df['Date'].dt.hour
    df['dayofweek'] = df['Date'].dt.dayofweek
    df['month'] = df['Date'].dt.month
    df['day'] = df['Date'].dt.day
    return df