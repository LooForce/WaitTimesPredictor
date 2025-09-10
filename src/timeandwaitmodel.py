import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from collect_data import get_last_hour
import joblib

###this model is trained on previous wait times + time-of-day + day-of-week


SEQ_LEN = 12  # 12 samples = 1 hour if data is at 5-min intervals
PRED_STEPS = 6  # Predict next 20 minutes (4 x 5min)

def create_sequences(df, seq_len=SEQ_LEN, pred_steps=PRED_STEPS):
    """
    Create sequences of the previous hour's wait times + time-of-day + day-of-week features,
    and the next 20 minutes as targets.
    """
    X, y = [], []
    wait_times = df['Wait'].values
    
    # Extract time info
    hours = df['Date'].dt.hour.values
    minutes = df['Date'].dt.minute.values
    days = df['Date'].dt.dayofweek.values  # Monday=0, Sunday=6
    
    # Cyclical encodings
    total_minutes = hours * 60 + minutes
    sin_time = np.sin(2 * np.pi * total_minutes / (24*60))
    cos_time = np.cos(2 * np.pi * total_minutes / (24*60))
    sin_day = np.sin(2 * np.pi * days / 7)
    cos_day = np.cos(2 * np.pi * days / 7)
    
    for i in range(len(wait_times) - seq_len - pred_steps + 1):
        # sequence of waits
        wait_seq = wait_times[i:i+seq_len]
        
        # time & day encoding at the end of sequence
        sin_t = sin_time[i+seq_len-1]
        cos_t = cos_time[i+seq_len-1]
        sin_d = sin_day[i+seq_len-1]
        cos_d = cos_day[i+seq_len-1]
        
        # features = wait history + time encodings
        X.append(np.concatenate([wait_seq, [sin_t, cos_t, sin_d, cos_d]]))
        y.append(wait_times[i+seq_len:i+seq_len+pred_steps])
        
    return np.array(X), np.array(y)

def train_rf_model(X, y):
    """
    Trains a Random Forest model for multi-output regression.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print("MAE (average over all steps):", mae)
    return model, mae

def predict_from_last_hour(last_hour_data, model, seq_len=SEQ_LEN, pred_steps=PRED_STEPS):
    """
    Predict the next 20 minutes (4 x 5min) given the previous hour of wait times,
    using both time-of-day and day-of-week.
    """
    if len(last_hour_data) < seq_len:
        print("Not enough data in the last hour to make a prediction.")
        return []
    
    df = pd.DataFrame(last_hour_data, columns=['Date', 'Wait'])
    df['Wait'] = df['Wait'].astype(float)
    last_seq = df['Wait'].values[-seq_len:]
    last_time = pd.to_datetime(df['Date'].iloc[-1])
    
    # Cyclical encodings for time and day
    total_minutes = last_time.hour * 60 + last_time.minute
    sin_t = np.sin(2 * np.pi * total_minutes / (24*60))
    cos_t = np.cos(2 * np.pi * total_minutes / (24*60))
    sin_d = np.sin(2 * np.pi * last_time.dayofweek / 7)
    cos_d = np.cos(2 * np.pi * last_time.dayofweek / 7)
    
    # Input = wait sequence + time/day features
    X_input = np.concatenate([last_seq, [sin_t, cos_t, sin_d, cos_d]]).reshape(1, -1)
    
    future_times = [last_time + pd.Timedelta(minutes=5*(i+1)) for i in range(pred_steps)]
    preds = model.predict(X_input)[0]
    
    print("Predicted wait times for the next 20 minutes (5-min intervals):")
    for t, p in zip(future_times, preds):
        print(f"{t}: {p:.1f} min")
    
    return list(zip(future_times, preds))

if __name__ == "__main__":
    # Load your historic data for training
    rides_df = pd.read_csv("rides.csv")

    ride_id = int(input("Enter ride ID for training data: "))
    ride_row = rides_df[rides_df['ride_id'] == ride_id]
    file_name = ride_row['file_name']

    df = pd.read_csv("QueueTimesData/{file_name}.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    X, y = create_sequences(df)
    model, mae = train_rf_model(X, y)
    joblib.dump(model, "rf_waittime_model.pkl")

    # Use get_last_hour to get the most recent hour of data for prediction
    #last_hour_data = get_last_hour(ride_id=284)  # Replace with your ride ID
    #predict_from_last_hour(last_hour_data, model)
    