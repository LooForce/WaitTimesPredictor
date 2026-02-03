import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from collect_data import get_last_hour
import joblib

### This model is trained on previous wait times + time-of-day + day-of-week

SEQ_LEN = 12  # 12 samples = 1 hour if data is at 5-min intervals
PRED_STEPS = 6  # Predict next 20 minutes (4 x 5min)
MODEL_DIR = "Models"

# Ensure the Models folder exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Create sequences for training
def create_sequences(df, seq_len=SEQ_LEN, pred_steps=PRED_STEPS):
    X, y = [], []
    wait_times = df['Wait'].values
    
    hours = df['Date'].dt.hour.values
    minutes = df['Date'].dt.minute.values
    days = df['Date'].dt.dayofweek.values
    
    total_minutes = hours * 60 + minutes
    sin_time = np.sin(2 * np.pi * total_minutes / (24*60))
    cos_time = np.cos(2 * np.pi * total_minutes / (24*60))
    sin_day = np.sin(2 * np.pi * days / 7)
    cos_day = np.cos(2 * np.pi * days / 7)
    
    for i in range(len(wait_times) - seq_len - pred_steps + 1):
        wait_seq = wait_times[i:i+seq_len]
        sin_t = sin_time[i+seq_len-1]
        cos_t = cos_time[i+seq_len-1]
        sin_d = sin_day[i+seq_len-1]
        cos_d = cos_day[i+seq_len-1]
        X.append(np.concatenate([wait_seq, [sin_t, cos_t, sin_d, cos_d]]))
        y.append(wait_times[i+seq_len:i+seq_len+pred_steps])
    return np.array(X), np.array(y)

# Train Random Forest model
def train_rf_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print("MAE (average over all steps):", mae)
    return model, mae

# Predict future wait times
def predict_from_last_hour(last_hour_data, model, seq_len=SEQ_LEN, pred_steps=PRED_STEPS):
    if len(last_hour_data) < seq_len:
        print("Not enough data in the last hour to make a prediction.")
        return []

    df = pd.DataFrame(last_hour_data, columns=['Date', 'Wait'])
    df['Wait'] = df['Wait'].astype(float)
    last_seq = df['Wait'].values[-seq_len:]
    last_time = pd.to_datetime(df['Date'].iloc[-1])
    
    total_minutes = last_time.hour * 60 + last_time.minute
    sin_t = np.sin(2 * np.pi * total_minutes / (24*60))
    cos_t = np.cos(2 * np.pi * total_minutes / (24*60))
    sin_d = np.sin(2 * np.pi * last_time.dayofweek / 7)
    cos_d = np.cos(2 * np.pi * last_time.dayofweek / 7)
    
    X_input = np.concatenate([last_seq, [sin_t, cos_t, sin_d, cos_d]]).reshape(1, -1)
    future_times = [last_time + pd.Timedelta(minutes=5*(i+1)) for i in range(pred_steps)]
    preds = model.predict(X_input)[0]
    
    print("Predicted wait times for the next 20 minutes (5-min intervals):")
    for t, p in zip(future_times, preds):
        print(f"{t}: {p:.1f} min")
    
    return list(zip(future_times, preds))

def get_or_train_model(ride):
    ride_name = ride['ride_name']
    file_name = ride['file_name']
    csv_file = f"QueueTimesData/{file_name}.csv"


    model_path = os.path.join(MODEL_DIR, f"{file_name}.pkl")
    
    if os.path.exists(model_path):
        print(f"Loading model for {ride_name}...")
        model = joblib.load(model_path)
    else:
        print(f"Training new model for {ride_name}...")
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        X, y = create_sequences(df)
        model, mae = train_rf_model(X, y)
        joblib.dump(model, model_path)
        print(f"Model saved to {model_path}")
    
    return model

# ------------------- Main -------------------
if __name__ == "__main__":
    rides_df = pd.read_csv("rides.csv")
    #ride_id = int(input("Enter ride ID for training/prediction: "))
    for ride in rides_df.iterrows():
        model = get_or_train_model(ride[1])
    
    # Make predictions
    #last_hour_data = get_last_hour(ride_id)
    #predict_from_last_hour(last_hour_data, model)