import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from wait_time_SR import load_ride_data
from feature_engineering import add_time_features

# Load your data
df = load_ride_data("spacemountain.csv")  # Change to your ride's CSV
df = add_time_features(df)

# Features and target
X = df[['hour', 'dayofweek', 'month', 'day']]
y = df['Wait']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))