import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import altair as alt

from collect_data import get_day, get_last_hour
from rf_model import predict_from_last_hour


import joblib

# Load rides
rides_df = pd.read_csv("rides.csv")

st.title('Mouse Waiter')

# Ride selection
ride_selection = st.selectbox("Select Ride", rides_df["ride_name"])

# Look up info for the selected ride
ride_info = rides_df[rides_df["ride_name"] == ride_selection].iloc[0]
ride_id = ride_info["ride_id"]
ride_file = ride_info["file_name"]

# Date selection
selected_date = st.date_input("Select Date", value=date.today())

# Get ride wait data
data = get_day(ride_id, selected_date.year, selected_date.month, selected_date.day)
ride_data = pd.DataFrame(data, columns=["datetime", "wait"])
ride_data["datetime"] = pd.to_datetime(ride_data["datetime"], format="%H:%M")

st.subheader(f"Ride: {ride_selection}")
st.write(f"Ride ID: {ride_id}")

# Display chart and predictions
if ride_data.empty:
    st.warning("No data available for the selected date.")
else:
    # Set datetime as index
    ride_data = ride_data.set_index("datetime")
    ride_data = ride_data.rename(columns={"wait": "Wait"})  # Standardize column name

    # Prepare dataframe for plotting
    plot_df = ride_data.copy()

    # If today, get predictions
    if selected_date == date.today():
        last_hour_data = get_last_hour(ride_id)
        if last_hour_data:
            model = joblib.load(f"Models/{ride_file}.pkl")
            preds = predict_from_last_hour(last_hour_data, model)
            pred_df = pd.DataFrame(preds, columns=["datetime", "Predicted"]).set_index("datetime")
            # Combine historic and predicted waits
            plot_df = pd.concat([plot_df, pred_df], axis=1)

    # Convert to long format for Altair
    long_df = plot_df.reset_index().melt(id_vars="datetime", var_name="Type", value_name="Wait Time")

    # Altair chart with different colors
    chart = alt.Chart(long_df).mark_line().encode(
        x="datetime:T",
        y="Wait Time:Q",
        color="Type:N",
        tooltip=["datetime:T", "Type:N", "Wait Time:Q"]
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    