import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

import streamlit as st

# 🔐 Set your custom password here
APP_PASSWORD = "cricket2025"

# Session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Private App Login")
    password_input = st.text_input("Enter Access Password:", type="password")

    if password_input == APP_PASSWORD:
        st.success("Access granted.")
        st.session_state.authenticated = True
        st.rerun()
    elif password_input:
        st.error("Invalid password. Try again.")
    st.stop()


# Import your methods here
from wagon_methods import (
    test_match_spike,
    test_match_spike_runs,
    test_match_wagon_colored,
    shot_type_wagon,
    pitch_type_wagon
)

st.set_page_config(page_title="Cricket Wagon Wheel App", layout="wide")
st.title("🏏 Cricket Shot Analysis Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Dropdown filters
    player_list = sorted(set(df['batsmanName'].dropna().unique()))
    selected_player = st.selectbox("Select Player", player_list)

    innings_options = sorted(df['inningNumber'].dropna().unique())
    selected_inns = st.selectbox("Select Innings", innings_options)

    bowler_list = sorted(df['bowlerName'].dropna().unique())
    selected_bowler = st.selectbox("Select Bowler (Optional)", [None] + bowler_list)

    # Plot selection
    st.markdown("**Select Plot Types to Display:**")
    plot_types = st.multiselect(
        "Choose plot(s):",
        [
            "Match Spike (Runs by Color)",
            "Match Spike (Runs Filtered)",
            "Colored Quadrant Wagon",
            "Shot Type Wagon",
            "Pitch Type Wagon"
        ]
    )

    # Show run selection only when "Match Spike (Runs Filtered)" is selected
    selected_runs = []
    run_options = ['All', 0, 1, 2, 3, 4, 6]
    if "Match Spike (Runs Filtered)" in plot_types and "Colored Quadrant Wagon" in plot_types:
        # selected_runs = st.multiselect(
        #     "Select Runs to Include (Filter)", [0, 1, 2, 3, 4, 6], default=[1, 2, 4, 6]
        # )
        selected_runs = st.multiselect("Select Runs", run_options, default=['All'])

    # Handle "All" logic
    if 'All' in selected_runs:
        filtered_runs = [0, 1, 2, 3, 4, 6]
    else:
        filtered_runs = selected_runs


    # Display selected plots
    if plot_types:
        if "Match Spike (Runs by Color)" in plot_types:
            st.subheader("🎯 Match Spike Plot")
            fig = test_match_spike(df, selected_player, selected_inns, selected_bowler)
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.pyplot(fig)

        if "Match Spike (Runs Filtered)" in plot_types and selected_runs:
            st.subheader("🎯 Match Spike Plot (Filtered by Runs)")
            fig = test_match_spike_runs(df, selected_player, selected_inns, filtered_runs,selected_bowler)
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.pyplot(fig)

        if "Colored Quadrant Wagon" in plot_types:
            st.subheader("🎨 Colored Quadrant Wagon")
            fig = test_match_wagon_colored(df, selected_player, selected_inns, selected_bowler, filtered_runs)
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.pyplot(fig)

        if "Shot Type Wagon" in plot_types:
            st.subheader("🏏 Shot Type Wagon")
            fig = shot_type_wagon(df, selected_player, selected_inns, selected_bowler)
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.pyplot(fig)

        if "Pitch Type Wagon" in plot_types:
            st.subheader("📐 Pitch Type Wagon")
            fig = pitch_type_wagon(df, selected_player, selected_inns, selected_bowler)
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.pyplot(fig)
else:
    st.info("Please upload a CSV file to begin.")
