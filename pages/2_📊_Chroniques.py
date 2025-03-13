import os
import sys
import logging
import json
import pandas as pd
import streamlit as st

# Set page config FIRST before any other Streamlit commands
st.set_page_config(page_title="Chroniques", page_icon="📊", layout="centered")

from os.path import abspath, dirname
root_dir = dirname(dirname((abspath(__file__))))
sys.path.append(root_dir)

cwd = os.getcwd()
if cwd != root_dir:
    os.chdir(root_dir)

# -----------------------------------------------------
# Modules
# -----------------------------------------------------
import src
import importlib
importlib.reload(src)

from src.config import initialize_sidebar
from src.path import load_paths, get_selected_profile
from src.visualisation.plotly_chroniques import TimeSeriesPlot_Plotly

# -----------------------------------------------------
# Load paths
# -----------------------------------------------------
profile = get_selected_profile()
print(profile)

# -----------------------------------------------------
# Sidebar
# -----------------------------------------------------
initialize_sidebar()

# -----------------------------------------------------
# Page content
# -----------------------------------------------------

chronique_param_json = os.path.join(root_dir, "data", "chronique_param.json")

# ------------------------------------------------------------------
# Functions to load/save your JSON
# ------------------------------------------------------------------

def load_chronique_params(json_path: str) -> dict:
    """
    Load chronique parameters. If it doesn't exist, return a default dict.

    Args:
        json_path (str): The path to the JSON file.

    Returns:
        dict: The loaded parameters or a default empty dictionary.
    """
    if not os.path.exists(json_path):
        # Return an empty dictionary or default values
        return {}
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chronique_params(params: dict, json_path: str):
    """
    Save chronique parameters to the JSON file.

    Args:
        params (dict): The parameters to save.
        json_path (str): The path to the JSON file.
    """
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(params, f, indent=4)

# ------------------------------------------------------------------
# Read "paths.json" and prepare profiles
# ------------------------------------------------------------------
all_paths = load_paths()
profile_dict = all_paths.get("profiles", {})  # dict of { "cheze": {...}, "basti": {...}, ...}
profile_names = list(profile_dict.keys())     # ["cheze", "basti", ...]

# ------------------------------------------------------------------
# Read or initialize chronique parameters
# ------------------------------------------------------------------
default_params = load_chronique_params(chronique_param_json)

# Set (or retrieve) the default values of each parameter
default_profile = default_params.get("selected_profile", profile_names[0] if profile_names else "")
default_freq = default_params.get("freq", "D")
default_log_y = default_params.get("log_y", False)
default_focus_year = default_params.get("focus_year", 2023)
default_rolling_window = default_params.get("rolling_window", 5)

# year_min and year_max will be determined after reading the CSV.
# Only the (year_min, year_max) interval is stored in the JSON.
default_year_min = default_params.get("year_min", 2004)
default_year_max = default_params.get("year_max", 2024)

# ------------------------------------------------------------------
# Streamlit layout
# ------------------------------------------------------------------
st.title("Chroniques")

# Sidebar (Sidebar)
st.sidebar.header("Parameters")

# 1) Profile selection
selected_profile = st.sidebar.selectbox(
    "Choose a profile",
    profile_names,
    index=profile_names.index(default_profile) if default_profile in profile_names else 0
)

# Get the corresponding CSV path
data_lake_path = None
if selected_profile and selected_profile in profile_dict:
    data_lake_path = profile_dict[selected_profile].get("data_lake_path", None)

# If we have a data_lake_path, read the CSV to determine min_year, max_year
if data_lake_path and os.path.exists(data_lake_path):
    try:
        # Read CSV with updated date parsing approach
        df = pd.read_csv(
            data_lake_path,
            sep=";",
            dtype={"time": str}  # Read time column as string first
        )

        # Convert time column to datetime
        df["time"] = pd.to_datetime(df["time"], dayfirst=True, errors="coerce")

        # Extract year and handle potential NaN values
        df["year"] = df["time"].dt.year
        valid_years = df["year"].dropna()

        if not valid_years.empty:
            min_year_csv = int(valid_years.min())
            max_year_csv = int(valid_years.max())
        else:
            st.error("No valid dates found in the time column")
            min_year_csv = default_year_min
            max_year_csv = default_year_max

    except Exception as e:
        st.error(f"Error reading CSV: {str(e)}")
        min_year_csv = default_year_min
        max_year_csv = default_year_max
else:
    # Default values in case the CSV does not exist
    min_year_csv = default_year_min
    max_year_csv = default_year_max

# 2) Slider for the year range
year_range = st.sidebar.slider(
    "Year range",
    min_year_csv,
    max_year_csv,
    (default_year_min, default_year_max)  # default value, a tuple
)

# 3) Dropdown menu for frequency (D, W, ME)
freq_options = ["D", "W", "ME"]
freq = st.sidebar.selectbox("Frequency", freq_options, index=freq_options.index(default_freq))

# 4) Checkbox for log_y
log_y = st.sidebar.checkbox("Logarithmic scale (log_y)", value=default_log_y)

# 5) Slider for focus_year
focus_year = st.sidebar.slider(
    "Focus year",
    min_value=min_year_csv,
    max_value=max_year_csv,
    value=default_focus_year
)

# 6) Slider for rolling_window
rolling_window = st.sidebar.slider(
    "Rolling window",
    min_value=2,
    max_value=10,
    value=default_rolling_window
)

# 7) Run button
run_button = st.sidebar.button("Run")

# ------------------------------------------------------------------
# When clicking "Run", save the parameters and rerun the page
# ------------------------------------------------------------------
if run_button:
    # Update the parameters dictionary
    new_params = {
        "selected_profile": selected_profile,
        "year_min": year_range[0],
        "year_max": year_range[1],
        "freq": freq,
        "log_y": log_y,
        "focus_year": focus_year,
        "rolling_window": rolling_window
    }
    save_chronique_params(new_params, chronique_param_json)

    # Force rerun of the app to update the charts
    st.rerun()

# ------------------------------------------------------------------
# Display the chart or results
# ------------------------------------------------------------------
# Here, you insert your logic to build the chart, e.g.:
# In the visualization section, add error handling:

st.write(f"Displaying chart for profile: {selected_profile}")
st.write(f"Data lake path: {data_lake_path}")

# Load the DataFrame
if data_lake_path and os.path.exists(data_lake_path):
    df = pd.read_csv(
        data_lake_path,
        sep=";",
        dtype={"time": str}
    )

    # Convert time column to datetime
    df["time"] = pd.to_datetime(df["time"], dayfirst=True, errors="coerce")

    # Extract year and handle potential NaN values
    df["year"] = df["time"].dt.year

    # Filter the DataFrame based on the selected year_min/year_max
    year_min_selected, year_max_selected = year_range
    df_filtered = df[df["year"].between(year_min_selected, year_max_selected)]


# Create the TimeSeriesPlot_Plotly object
if data_lake_path and os.path.exists(data_lake_path):
    df = pd.read_csv(
        data_lake_path,
        sep=";",
        dtype={"time": str}
    )

    # Convert time column to datetime
    df["time"] = pd.to_datetime(df["time"], dayfirst=True, errors="coerce")

    # Extract year and handle potential NaN values
    df["year"] = df["time"].dt.year

    # Filter the DataFrame based on the selected year_min/year_max
    year_min_selected, year_max_selected = year_range
    df_filtered = df[df["year"].between(year_min_selected, year_max_selected)]

#-----------------------------------------------------
# Chronique Vol
#-----------------------------------------------------

    tab1, tab2 = st.tabs(["Standard", "Moyenne glissante"])
    with tab1:
        # Create the TimeSeriesPlot_Plotly object with correct parameters
        plotter = TimeSeriesPlot_Plotly(
            title="Chroniques",
            x_axis_title="Date",
            y_axis_title="Value",
            x_range=(year_min_selected, year_max_selected),
            log_y=log_y,
            mode='chronique'
        )

        # Add the series to the plot
        plotter.add_series(
            df=df_filtered,
            time_col="time",
            var_col="cheze_vol",
            legend_name="Data",
            freq=freq,
            year_min=year_min_selected,
            year_max=year_max_selected,
        )
        
        plotter.add_line(
                orientation='h',
                position=14500000,
                line_dash='dash',
                col='all',
                color='red',
                label='Volume Maximal 14.5Mm3'
                )


        # Create and display the plot
        plotter.fig = plotter.create_figure()
        st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)
    
    with tab2:
        # Create the TimeSeriesPlot_Plotly object with correct parameters
        plotter = TimeSeriesPlot_Plotly(
            title="Chroniques",
            x_axis_title="Date",
            y_axis_title="Value",
            x_range=(year_min_selected, year_max_selected),
            log_y=log_y,
            mode='chronique'
        )

        # Add the series to the plot
        plotter.add_series(
            df=df_filtered,
            time_col="time",
            var_col="cheze_vol",
            legend_name="Data",
            freq=freq,
            year_min=year_min_selected,
            year_max=year_max_selected,
            rolling_window=rolling_window
        )
        
        plotter.add_line(
                orientation='h',
                position=14500000,
                line_dash='dash',
                col='all',
                color='red',
                label='Volume Maximal 14.5Mm3'
                )

        # Create and display the plot
        plotter.fig = plotter.create_figure()
        st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)
#-----------------------------------------------------
# evolution
#-----------------------------------------------------

    tab1, tab2 = st.tabs(["Standard", "Moyenne glissante"])
    with tab1:
        # Create the TimeSeriesPlot_Plotly object with correct parameters
        plotter = TimeSeriesPlot_Plotly(
            title="Chroniques",
            x_axis_title="Date",
            y_axis_title="Value",
            x_range=(year_min_selected, year_max_selected),
            log_y=log_y,
            mode='evolution'
        )

        # Add the series to the plot
        plotter.add_series(
            df=df_filtered,
            time_col="time",
            var_col="cheze_vol",
            legend_name="Data",
            freq=freq,
            year_min=year_min_selected,
            year_max=year_max_selected,
        )
        
        plotter.add_line(
                orientation='h',
                position=14500000,
                line_dash='dash',
                col='all',
                color='red',
                label='Volume Maximal 14.5Mm3'
                )


        # Create and display the plot
        plotter.fig = plotter.create_figure()
        st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)
    
    with tab2:
        # Create the TimeSeriesPlot_Plotly object with correct parameters
        plotter = TimeSeriesPlot_Plotly(
            title="Chroniques",
            x_axis_title="Date",
            y_axis_title="Value",
            x_range=(year_min_selected, year_max_selected),
            log_y=log_y,
            mode='evolution'
        )

        # Add the series to the plot
        plotter.add_series(
            df=df_filtered,
            time_col="time",
            var_col="cheze_vol",
            legend_name="Data",
            freq=freq,
            year_min=year_min_selected,
            year_max=year_max_selected,
            rolling_window=rolling_window
        )
        
        plotter.add_line(
                orientation='h',
                position=14500000,
                line_dash='dash',
                col='all',
                color='red',
                label='Volume Maximal 14.5Mm3'
                )

        # Create and display the plot
        plotter.fig = plotter.create_figure()
        st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)
        
        #-----------------------------------------------------
        # Statistic
        #-----------------------------------------------------

    # Create the TimeSeriesPlot_Plotly object with correct parameters
    plotter = TimeSeriesPlot_Plotly(
        title="Statistique",
        x_axis_title="Date",
        y_axis_title="Value",
        x_range=(year_min_selected, year_max_selected),
        log_y=log_y,
        mode='statistic',
        focus_year=focus_year
    )

    # Add the series to the plot
    plotter.add_series(
        df=df_filtered,
        time_col="time",
        var_col="cheze_vol",
        legend_name="Data",
        freq=freq,
        year_min=year_min_selected,
        year_max=year_max_selected,
    )

    plotter.add_line(
            orientation='h',
            position=14500000,
            line_dash='dash',
            col='all',
            color='red',
            label='Volume Maximal 14.5Mm3'
            )


    # Create and display the plot
    plotter.fig = plotter.create_figure()
    st.plotly_chart(plotter.fig, theme="streamlit", use_container_width=True)

else:
    st.warning("The CSV file does not exist or the path is not configured.")
    
