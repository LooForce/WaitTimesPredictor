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

Train models
------------
Train the random-forest models using `rf_model.py`. This script reads ride CSV data (from `QueueTimesData/` or `wait_times.csv`) and writes model artifacts into `Models/`. The data is taken from QueueTimes.com API and is training data from the year 2025. 

```bash
# run training (may take some time depending on data)
python rf_model.py
```

Run the Streamlit app
---------------------
With the venv activated and dependencies installed:

```bash
streamlit run stream_app.py
```

This opens a browser UI to select rides and dates and view predictions.

Collecting data
---------------
- `collect_data.py` contains functions that fetch ride-specific pages and parse embedded JSON from page scripts. See `get_day` and `get_last_hour`.

Enjoy!
