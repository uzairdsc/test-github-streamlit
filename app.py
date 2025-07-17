import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO

# Set your custom password here
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

    # 🔧 FIXED: Compute static filters first
    # test_nums = sorted(df['TestNum'].dropna().unique())
    test_nums = sorted(df['TestNum'].dropna().unique())
    test_num_options = ["All"] + [str(num) for num in test_nums]
    batting_teams = sorted(df['team_bat'].dropna().unique())

    col1, col2 = st.columns(2)

    with col1:
        selected_test_str = st.selectbox("Select Test Match Number", test_num_options,index=0)
        selected_test_num = None if selected_test_str == "All" else int(selected_test_str)        
        # selected_team = st.selectbox("Select Batting Team", batting_teams)    
        batting_teams = sorted(df['team_bat'].dropna().unique())
        team_bat_options = ["All"] + batting_teams
        selected_team = st.selectbox("Select Batting Team", team_bat_options, index=0)
        selected_team = None if selected_team == "All" else selected_team

    # 🔧 FIXED: Now compute dependent filters
    # player_list = sorted(df[df['team_bat'] == selected_team]['batsmanName'].dropna().unique())
    if selected_team:
        player_list = sorted(df[df['team_bat'] == selected_team]['batsmanName'].dropna().unique())
    else:
        player_list = sorted(df['batsmanName'].dropna().unique())
    player_list = sorted(set(player_list))
    player_options = ["All"] + player_list
    # innings_options = sorted(
    #     df[(df['team_bat'] == selected_team) & (df['TestNum'] == selected_test_num)]
    #     ['inningNumber'].dropna().unique()
    # )
    if selected_team and selected_test_num:
        inns = df[(df['team_bat'] == selected_team) & (df['TestNum'] == selected_test_num)]['inningNumber']
    elif selected_team:
        inns = df[df['team_bat'] == selected_team]['inningNumber']
    elif selected_test_num:
        inns = df[df['TestNum'] == selected_test_num]['inningNumber']
    else:
        inns = df['inningNumber']

    innings_options = sorted(inns.dropna().unique())
    innings_display = ["All"] + [str(i) for i in innings_options]

    # bowler_list = sorted(df[df['team_bowl'] != selected_team]['bowlerName'].dropna().unique())
    if selected_team:
        bowler_list = sorted(df[df['team_bowl'] != selected_team]['bowlerName'].dropna().unique())
    else:
        bowler_list = sorted(df['bowlerName'].dropna().unique())

    with col2:
        # selected_inns = st.selectbox("Select Innings", ['All'] + innings_options,default='All')
        selected_inns_str = st.selectbox("Select Innings", innings_display, index=0)
        selected_inns = None if selected_inns_str == "All" else int(selected_inns_str)
        # selected_player = st.selectbox("Select Player", ['All'] + player_list, default='All')
        selected_player = st.selectbox("Select Player", player_options)
        selected_player = None if selected_player == "All" else selected_player

        selected_bowler = st.selectbox("Select Bowler", ['All'] + bowler_list,index=0)
        bowler_name = None if selected_bowler == "All" else selected_bowler


    # Dropdown filters
    # player_list = sorted(set(df['batsmanName'].dropna().unique()))
    # selected_player = st.selectbox("Select Player", player_list)

    # select test match
    # test_nums = sorted(df['TestNum'].dropna().unique())
    # selected_test_num = st.selectbox("Select Test Match Number", test_nums)
    # test_nums = sorted(df['TestNum'].dropna().unique())
    # test_num_options = ["All"] + [str(num) for num in test_nums]  # keep all as string

    # selected_test_str = st.selectbox("Select Test Match Number", test_num_options)
    # selected_test_num = None if selected_test_str == "All" else int(selected_test_str)


    # First select Batting Team
    # batting_teams = sorted(df['team_bat'].dropna().unique())
    # selected_team = st.selectbox("Select Batting Team", batting_teams)

    # Now show players based on selected team
    # player_list = sorted(df[df['team_bat'] == selected_team]['batsmanName'].dropna().unique())
    # selected_player = st.selectbox("Select Player", player_list)

    # we will sort the innings when team bat is selected_team
    # innings_options = sorted(df[df['team_bat'] == selected_team]['inningNumber'].dropna().unique())
    # innings_options = sorted(df['inningNumber'].dropna().unique())
    # innings_options = sorted(
    #     df[(df['team_bat'] == selected_team) & (df['TestNum'] == selected_test_num)]
    #     ['inningNumber'].dropna().unique()
    # )
    # if selected_test_num is None:
    #     innings_options = sorted(
    #         df[df['team_bat'] == selected_team]['inningNumber'].dropna().unique()
    #     )
    # else:
    #     innings_options = sorted(
    #         df[(df['team_bat'] == selected_team) & (df['TestNum'] == selected_test_num)]
    #         ['inningNumber'].dropna().unique()
    #     )
    # innings_options = ["All"] + innings_options
    # selected_inns = st.selectbox("Select Innings", innings_options)

    # bowler_list = sorted(df['bowlerName'].dropna().unique())
    # Only include bowlers from the opposition team (not batting team)
    # bowler_list = sorted(
    #     df[df['team_bowl'] != selected_team]['bowlerName'].dropna().unique()
    # )
    # selected_bowler = st.selectbox("Select Bowler", [None] + bowler_list)

    # colum1, colum2= st.columns(2)
    # with colum1:


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


    # selected_runs = []
    # run_options = ['All', 0, 1, 2, 3, 4, 5, 6]
    # default_runs = ['All']  # keeps "All" selected visually

    # # Convert to full list of values if 'All' is selected
    # # filtered_runs = [0, 1, 2, 3, 4, 6] if 'All' in selected_runs else selected_runs
    # if any(p in plot_types for p in ["Spike Plot with Stats", "Wagon Zone Plot with Stats"]):
    #     # selected_runs = st.multiselect("Select Runs", run_options, default=['All'])
    #     selected_runs = st.multiselect("Select Runs", run_options, default=default_runs)

    # filtered_runs = [0, 1, 2, 3, 4, 6] if 'All' in selected_runs else selected_runs

    transparent_bg = st.checkbox("Transparent Background for Plots", value=False)
    fig_spike, fig_wagon = None, None

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
            # make the subheader centered
            st.markdown("<h2 style='text-align: center;'>📊 Spike Plot with Stats</h2>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.markdown("## ⚙️ Customize Plot Info")
                show_title = st.checkbox("Show Plot Title", value=True)
                show_legend = st.checkbox("Show Legend", value=True)
                show_summary = st.checkbox("Show Runs Summary", value=True)
                runs_count = st.checkbox("Show Runs Count", value=True)
                show_fours_sixes = st.checkbox("Show 4s and 6s", value=True)
                show_bowler = st.checkbox("Show Bowler", value=True)
                show_control = st.checkbox("Show Control %", value=True)
                show_prod_shot = st.checkbox("Show Productive Shot", value=True)
                show_ground = st.checkbox("Show Ground Image", value=True)

                # transparent_bg = st.checkbox("Transparent Background for Plots", value=False)
            # with col3:
            #     st.markdown("## 🌟 Filter Runs")
            #     run_all = st.checkbox("All Runs", key="run_all")

            #     run_selections = {}
            #     for i in range(7):
            #         run_selections[i] = st.checkbox(str(i), key=f"run_{i}")

            #     filtered_runs = []
            #     if not run_all:
            #         filtered_runs = [i for i, selected in run_selections.items() if selected]
            #     else:
            #         filtered_runs = None
            with col3:
                st.markdown("## Run Filter (Spike Plot)")

                # Initialize session state (only once)
                if "run_init_spike" not in st.session_state:
                    st.session_state["run_all_spike"] = True
                    for i in range(7):
                        st.session_state[f'run_{i}_spike'] = True
                    st.session_state["run_init_spike"] = True

                # When 'All' checkbox is changed
                def sync_all_to_individual_spike():
                    all_selected = st.session_state["run_all_spike"]
                    for i in range(7):
                        st.session_state[f'run_{i}_spike'] = all_selected

                # When any individual checkbox is changed
                def sync_individual_to_all_spike():
                    all_selected = all(st.session_state[f'run_{i}_spike'] for i in range(7))
                    st.session_state["run_all_spike"] = all_selected

                # All checkbox
                st.checkbox("All", key="run_all_spike", on_change=sync_all_to_individual_spike)

                # Individual run checkboxes
                for i in range(7):
                    st.checkbox(str(i), key=f'run_{i}_spike', on_change=sync_individual_to_all_spike)

                # Determine filtered runs
                individual_selected_spike = [i for i in range(7) if st.session_state.get(f'run_{i}_spike', False)]

                if st.session_state["run_all_spike"]:
                    filtered_runs_spike = None  # Means 'All selected'
                elif individual_selected_spike:
                    filtered_runs_spike = individual_selected_spike
                else:
                    filtered_runs_spike = []  # Empty selection → show warning
                    
            if "Spike Plot with Stats" in plot_types:
                if filtered_runs_spike == []:
                    st.warning("Please select at least one run value to display the plot.")
                else:
                    # fig_spike = spike_plot_custom(
                    #     df, selected_player, selected_inns=selected_inns,
                    #     test_num=selected_test_num,
                    #     run_values=filtered_runs_spike,
                    #     bowler_name=bowler_name,
                    #     transparent=transparent_bg,
                    #     show_title=show_title,
                    #     show_summary=show_summary,
                    #     show_legend=show_legend,
                    #     runs_count=runs_count,
                    #     show_fours_sixes=show_fours_sixes,
                    #     show_control=show_control,
                    #     show_prod_shot=show_prod_shot,
                    #     show_bowler=show_bowler,
                    #     show_ground=show_ground
                    # )
                    fig_spike = spike_plot_custom(
                        df=df,
                        player_name=selected_player,
                        inns=selected_inns,
                        test_num=selected_test_num,
                        team_bat=selected_team,
                        run_values=filtered_runs_spike,
                        bowler_name=None if selected_bowler == "All" else selected_bowler,
                        transparent=transparent_bg,
                        show_title=show_title,
                        show_summary=show_summary,
                        show_legend=show_legend,
                        runs_count=runs_count,
                        show_fours_sixes=show_fours_sixes,
                        show_control=show_control,
                        show_prod_shot=show_prod_shot,
                        show_bowler=show_bowler,
                        show_ground=show_ground
                    )
                    with col2:
                        st.pyplot(fig_spike)
            # fig = spike_plot_custom(df, selected_player, selected_inns, filtered_runs, selected_bowler, transparent=transparent_bg)
            
            with col1:
                # Download button for plot
                buf = BytesIO()
                if fig_spike:
                    fig_spike.savefig(buf, format="png", transparent=transparent_bg)
                    st.download_button(
                        label="📅 Download Plot as PNG",
                        data=buf.getvalue(),
                        file_name=f"{selected_player}_innings{selected_inns}_spike_plot.png",
                        mime="image/png",
                        key="spike_download"
                    )
                else:
                    st.warning("No plot available to download (check your run filters or data).")
        if "Wagon Zone Plot with Stats" in plot_types:
            st.markdown("<h2 style='text-align: center;'>📊 Wagon Zone Plot with Stats</h2>", unsafe_allow_html=True)
            # fig = wagon_zone_plot(df, selected_player, selected_inns, selected_bowler, filtered_runs, transparent=transparent_bg)
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.markdown("## ⚙️ Customize Plot Info")    
                show_title_wagon = st.checkbox("Show Plot Title (Wagon)", value=True, key="wagon_title")
                show_summary_wagon = st.checkbox("Show Runs Summary (Wagon)", value=True, key="wagon_summary")
                runs_count_wagon = st.checkbox("Show Total Runs (Wagon)", value=True, key="wagon_total")
                show_fours_sixes_wagon = st.checkbox("Show 4s and 6s (Wagon)", value=True, key="wagon_fs")
                show_bowler_wagon = st.checkbox("Show Bowler (Wagon)", value=True, key="wagon_bowler")
                show_control_wagon = st.checkbox("Show Control % (Wagon)", value=True, key="wagon_ctrl")
                show_prod_shot_wagon = st.checkbox("Show Productive Shot (Wagon)", value=True, key="wagon_prod")
            with col3:
                st.markdown("## Run Filter (Wagon Plot)")

                # Initialize session state (only once)
                if "run_init_wagon" not in st.session_state:
                    st.session_state["run_all_wagon"] = True
                    for i in range(7):
                        st.session_state[f'run_{i}_wagon'] = True
                    st.session_state["run_init_wagon"] = True

                # When 'All' checkbox is changed
                def sync_all_to_individual_wagon():
                    all_selected = st.session_state["run_all_wagon"]
                    for i in range(7):
                        st.session_state[f'run_{i}_wagon'] = all_selected

                # When any individual checkbox is changed
                def sync_individual_to_all_wagon():
                    all_selected = all(st.session_state[f'run_{i}_wagon'] for i in range(7))
                    st.session_state["run_all_wagon"] = all_selected

                # All checkbox
                st.checkbox("All", key="run_all_wagon", on_change=sync_all_to_individual_wagon)

                # Individual run checkboxes
                for i in range(7):
                    st.checkbox(str(i), key=f'run_{i}_wagon', on_change=sync_individual_to_all_wagon)

                # Determine filtered runs
                individual_selected_wagon = [i for i in range(7) if st.session_state.get(f'run_{i}_wagon', False)]

                if st.session_state["run_all_wagon"]:
                    filtered_runs_wagon = None  # Means 'All selected'
                elif individual_selected_wagon:
                    filtered_runs_wagon = individual_selected_wagon
                else:
                    filtered_runs_wagon = []  # Empty selection → show warning

            if "Wagon Zone Plot with Stats" in plot_types:
                if filtered_runs_wagon == []:
                    st.warning("Please select at least one run value to display the plot.")
                else:
                    with col2:
                        fig_wagon = wagon_zone_plot(
                            df=df,
                            player_name=selected_player,
                            inns=selected_inns,
                            test_num=selected_test_num,
                            bowler_name=None if selected_bowler == "All" else selected_bowler,
                            run_values=filtered_runs_wagon,
                            transparent=transparent_bg,
                            show_title=show_title_wagon,
                            show_summary=show_summary_wagon,
                            runs_count=runs_count_wagon,
                            show_fours_sixes=show_fours_sixes_wagon,
                            show_control=show_control_wagon,
                            show_prod_shot=show_prod_shot_wagon,
                            show_bowler=show_bowler_wagon,
                        )
                        st.pyplot(fig_wagon)
            with col1:
                # Download button for plot
                buf = BytesIO()
                if fig_wagon:
                    fig_wagon.savefig(buf, format="png", transparent=transparent_bg)
                    st.download_button(
                        label="📅 Download Plot as PNG",
                        data=buf.getvalue(),
                        file_name=f"{selected_player}_innings{selected_inns}_wagon_plot.png",
                        mime="image/png",
                        key="wagon_download"
                    )
                else:
                    st.warning("No plot available to download (check your run filters or data).")

else:
    st.info("Please upload a CSV file to begin.")
