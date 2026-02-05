WaitTimesPredictor
==================

This repository collects theme-park queue times, trains a per-ride model, and exposes a Streamlit app to predict wait times.

Quick overview
- `collect_data.py` — utilities to fetch and parse queue times from queue-times.com
- `rf_model.py` — train Random Forest models per ride and save them under `Models/`
- `stream_app.py` — Streamlit app that loads models and shows predictions
- `wait_times.csv` / `QueueTimesData/` — collected and historical data files

Prerequisites
- Python 3.10+ (3.11/3.12/3.13 should work)

Recommended: use a virtual environment (venv)

Setup (macOS, zsh)
-------------------
From the project root:

```bash
# create a venv named .venv (recommended)
python3 -m venv .venv

# activate it
source .venv/bin/activate

# upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

If you prefer pinned reproducibility, after installing run:

```bash
pip freeze > requirements.txt
```

Add the venv to gitignore if it's not already ignored:

```bash
echo ".venv" >> .gitignore
```

Collect Data
---------------------
Run the line to get the most updated information saved to the csv for better model prediction
```bash
python3 wait_time_SR
```

Train Models
---------------------
```bash
python3 rf_model.py
```

Run the Streamlit app
---------------------
With the venv activated and dependencies installed:

```bash
streamlit run stream_app.py
```

This opens a browser UI to select rides and dates and view predictions.


Enjoy!
