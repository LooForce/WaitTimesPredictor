import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from collect_data import get_last_hour

SEQ_LEN = 12  # 12 samples = 1 hour if data is at 5-min intervals
PRED_STEPS = 4  # Predict next 20 minutes (4 x 5min)

def create_sequences(df, seq_len=SEQ_LEN, pred_steps=PRED_STEPS):
    """
    Create sequences of the previous hour's wait times as features,
    and the next 20 minutes as targets.
    """
    X, y = [], []
    wait_times = df['Wait'].values
    for i in range(len(wait_times) - seq_len - pred_steps + 1):
        X.append(wait_times[i:i+seq_len])
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
    Predict the next 20 minutes (4 x 5min) given the previous hour of wait times.
    last_hour_data: list of [datetime, wait] pairs
    """
    if len(last_hour_data) < seq_len:
        print("Not enough data in the last hour to make a prediction.")
        return []
    # Prepare DataFrame
    df = pd.DataFrame(last_hour_data, columns=['Date', 'Wait'])
    df['Wait'] = df['Wait'].astype(float)
    last_seq = df['Wait'].values[-seq_len:]
    X_input = last_seq.reshape(1, -1)
    last_time = pd.to_datetime(df['Date'].iloc[-1])
    future_times = [last_time + pd.Timedelta(minutes=5*(i+1)) for i in range(pred_steps)]
    preds = model.predict(X_input)[0]
    print("Predicted wait times for the next 20 minutes (5-min intervals):")
    for t, p in zip(future_times, preds):
        print(f"{t}: {p:.1f} min")
    return list(zip(future_times, preds))

if __name__ == "__main__":
    # Load your historic data for training
    df = pd.read_csv("QueueTimesData/spacemountain.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    X, y = create_sequences(df)
    model, mae = train_rf_model(X, y)

    # Use get_last_hour to get the most recent hour of data for prediction
    last_hour_data = get_last_hour(ride_id=284)  # Replace with your ride ID
    predict_from_last_hour(last_hour_data, model)