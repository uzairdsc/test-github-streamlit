import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO

# 🔐 Set your custom password here
APP_PASSWORD = "cricket2025"
# APP_PASSWORD = st.secrets["auth"]["password"]
# Ensure the password is set in the secrets.toml file

# Session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Private App Login")
    password_input = st.text_input("Enter Access Password:", type="password")

    if password_input == APP_PASSWORD:
        st.success("Access granted.")
        st.session_state.authenticated = True
        st.rerun()
    elif password_input:
        st.error("Invalid password. Try again.")
    st.stop()

# Import your methods here
# from wagon_methods import (
#     # test_match_spike,
#     test_match_spike_runs,
#     test_match_wagon_colored,
#     # shot_type_wagon,
#     # pitch_type_wagon
# )
from SpikePlot import test_match_spike_runs as spike_plot_custom

from WagonZonePlot import test_match_wagon as wagon_zone_plot

st.set_page_config(page_title="Cricket Wagon Wheel App", layout="wide")
st.title("🏏 Cricket Shot Analysis Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Dropdown filters
    # player_list = sorted(set(df['batsmanName'].dropna().unique()))
    # selected_player = st.selectbox("Select Player", player_list)

    # First select Batting Team
    batting_teams = sorted(df['team_bat'].dropna().unique())
    selected_team = st.selectbox("Select Batting Team", batting_teams)

    # Now show players based on selected team
    player_list = sorted(df[df['team_bat'] == selected_team]['batsmanName'].dropna().unique())
    selected_player = st.selectbox("Select Player", player_list)

    # innings_options = sorted(df['inningNumber'].dropna().unique())
    innings_options = sorted(df[df['team_bat'] == selected_team]['inningNumber'].dropna().unique())
    selected_inns = st.selectbox("Select Innings", innings_options)

    bowler_list = sorted(df['bowlerName'].dropna().unique())
    selected_bowler = st.selectbox("Select Bowler", [None] + bowler_list)

    st.markdown("**Select Plot Types to Display:**")
    plot_types = st.multiselect(
        "Choose plot(s):",
        [
            # "Match Spike (Runs Filtered)",
            # "Colored Quadrant Wagon",
            "Spike Plot with Stats",
            "Wagon Zone Plot with Stats"
        ]
    )

    selected_runs = []
    run_options = ['All', 0, 1, 2, 3, 4, 5, 6]
    default_runs = ['All']  # keeps "All" selected visually

    # Convert to full list of values if 'All' is selected
    # filtered_runs = [0, 1, 2, 3, 4, 6] if 'All' in selected_runs else selected_runs
    if any(p in plot_types for p in ["Spike Plot with Stats", "Wagon Zone Plot with Stats"]):
        # selected_runs = st.multiselect("Select Runs", run_options, default=['All'])
        selected_runs = st.multiselect("Select Runs", run_options, default=default_runs)

    filtered_runs = [0, 1, 2, 3, 4, 6] if 'All' in selected_runs else selected_runs

    transparent_bg = st.checkbox("Transparent Background for Plots", value=False)

    if plot_types:
        # if "Match Spike (Runs Filtered)" in plot_types and selected_runs:
        #     st.subheader("🎯 Match Spike Plot (Filtered by Runs)")
        #     fig = test_match_spike_runs(df, selected_player, selected_inns, filtered_runs, selected_bowler)
        #     col1, col2, col3 = st.columns([2, 2, 2])
        #     with col1:
        #         st.pyplot(fig)

        # if "Colored Quadrant Wagon" in plot_types:
        #     st.subheader("🎨 Colored Quadrant Wagon")
        #     fig = test_match_wagon_colored(df, selected_player, selected_inns, selected_bowler, filtered_runs)
        #     with col1:
        #         st.pyplot(fig)

        if "Spike Plot with Stats" in plot_types:
            st.subheader("📊 Spike Plot with Stats")
            col1, col2, col3 = st.columns([2, 2, 2])
            with col2:
                st.markdown("## ⚙️ Customize Plot Info")
                show_title = st.checkbox("Show Plot Title", value=True)
                show_legend = st.checkbox("Show Legend", value=True)
                show_total = st.checkbox("Show Total Runs", value=True)
                show_fours_sixes = st.checkbox("Show 4s and 6s", value=True)
                show_control = st.checkbox("Show Control %", value=True)
                show_prod_shot = st.checkbox("Show Productive Shot", value=True)
            # fig = spike_plot_custom(df, selected_player, selected_inns, filtered_runs, selected_bowler, transparent=transparent_bg)
            fig = spike_plot_custom(
                df, selected_player, selected_inns, filtered_runs, selected_bowler,
                transparent=transparent_bg,
                show_title=show_title,
                show_legend=show_legend,
                show_total=show_total,
                show_fours_sixes=show_fours_sixes,
                show_control=show_control,
                show_prod_shot=show_prod_shot
            )
            with col1:
                st.pyplot(fig)
            
            with col3:
                # Download button for plot
                buf = BytesIO()
                fig.savefig(buf, format="png", transparent=transparent_bg)
                # st.download_button(
                #     label="📅 Download Plot as PNG",
                #     data=buf.getvalue(),
                #     file_name=f"{selected_player}_innings{selected_inns}_spike_plot.png",
                #     mime="image/png"
                # )
                st.download_button(
                label="📅 Download Plot as PNG",
                data=buf.getvalue(),
                file_name=f"{selected_player}_innings{selected_inns}_spike_plot.png",
                mime="image/png",
                key="spike_download"
                )
        if "Wagon Zone Plot with Stats" in plot_types:
            st.subheader("📊 Wagon Zone Plot with Stats")
            fig = wagon_zone_plot(df, selected_player, selected_inns, selected_bowler, filtered_runs, transparent=transparent_bg)
            col1, col2, col3 = st.columns([2, 2, 2])
            with col2:
                st.markdown("## ⚙️ Customize Plot Info")    
                show_title_wagon = st.checkbox("Show Plot Title (Wagon)", value=True, key="wagon_title")
                show_total_wagon = st.checkbox("Show Total Runs (Wagon)", value=True, key="wagon_total")
                show_fours_sixes_wagon = st.checkbox("Show 4s and 6s (Wagon)", value=True, key="wagon_fs")
                show_control_wagon = st.checkbox("Show Control % (Wagon)", value=True, key="wagon_ctrl")
                show_prod_shot_wagon = st.checkbox("Show Productive Shot (Wagon)", value=True, key="wagon_prod")
            with col1:
                with col1:
                    fig = wagon_zone_plot(
                        df, selected_player, selected_inns, selected_bowler, filtered_runs,
                        transparent=transparent_bg,
                        show_title=show_title_wagon,
                        show_total=show_total_wagon,
                        show_fours_sixes=show_fours_sixes_wagon,
                        show_control=show_control_wagon,
                        show_prod_shot=show_prod_shot_wagon
                    )
                    st.pyplot(fig)
                # st.pyplot(fig)
            with col3:
                # Download button for plot
                buf = BytesIO()
                fig.savefig(buf, format="png", transparent=transparent_bg)
                # st.download_button(
                #     label="📅 Download Plot as PNG",
                #     data=buf.getvalue(),
                #     file_name=f"{selected_player}_innings{selected_inns}_spike_plot.png",
                #     mime="image/png"
                # )
                st.download_button(
                label="📅 Download Plot as PNG",
                data=buf.getvalue(),
                file_name=f"{selected_player}_innings{selected_inns}_wagon_plot.png",
                mime="image/png",
                key="wagon_download"
                )

else:
    st.info("Please upload a CSV file to begin.")
