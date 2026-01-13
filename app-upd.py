import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO
import boto3
from botocore.exceptions import NoCredentialsError

# # Set your custom password here
# APP_PASSWORD = "cricket2025"
# # APP_PASSWORD = st.secrets["auth"]["password"]

# # Session state for authentication
# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False

# if not st.session_state.authenticated:
#     st.title("🔐 Private App Login")
#     password_input = st.text_input("Enter Access Password:", type="password")

#     if password_input == APP_PASSWORD:
#         st.success("Access granted.")
#         st.session_state.authenticated = True
#         st.rerun()
#     elif password_input:
#         st.error("Invalid password. Try again.")
#     st.stop()

# Import your plotting methods
from SpikeUpd import spike_graph_plot as spike_plot_custom
from WagonUpd import wagon_zone_plot

st.set_page_config(page_title="Cricket Wagon Wheel App", layout="wide")
st.title("🏏 Cricket Shot Analysis Dashboard")


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_from_s3(bucket_name, file_key, aws_access_key, aws_secret_key, region_name='us-east-1'):
    """Load CSV from S3 bucket"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        )
        
        with st.spinner(f"Loading data from S3: {file_key}..."):
            obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            df = pd.read_csv(obj['Body']), low_memory=False
            st.success(f"✅ Loaded {len(df)} rows from S3")
            return df
    except NoCredentialsError:
        st.error("❌ AWS credentials not found. Check your secrets.toml file.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading from S3: {str(e)}")
        return None

# ===== Dataset Selection =====
st.sidebar.header("📂 Select Dataset Source")
data_source = st.sidebar.selectbox(
    "Choose data source:",
    ["Upload Local File", "T20 Data for 2025", "Complete T20-T20I Data"]
)

# Initialize session state for df
if 'df' not in st.session_state:
    st.session_state.df = None

df = st.session_state.df

if data_source == "Upload Local File":
    uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file, low_memory=False)
        st.session_state.df = df
        st.sidebar.success(f"✅ Loaded {len(df):,} rows")

elif data_source == "T20 Data for 2025":
    if "aws" in st.secrets:
        bucket = st.secrets["aws"]["bucket_name"]
        access_key = st.secrets["aws"]["access_key_id"]
        secret_key = st.secrets["aws"]["secret_access_key"]
        region = st.secrets["aws"].get("region_name", "ap-south-1")
        
        s3_file_key = st.sidebar.text_input(
            "Enter S3 file path:",
            value="t20_bbb_2024-25.csv"
        )
        
        if st.sidebar.button("Load from S3", key="load_2025"):
            loaded_df = load_from_s3(bucket, s3_file_key, access_key, secret_key, region)
            if loaded_df is not None:
                st.session_state.df = loaded_df
                df = loaded_df
        
        # Show current loaded data info
        if st.session_state.df is not None:
            st.sidebar.info(f"📊 Current data: {len(st.session_state.df):,} rows")
    else:
        st.sidebar.warning("⚠️ AWS credentials not configured in secrets.toml")

elif data_source == "Complete T20-T20I Data":
    if "aws" in st.secrets:
        bucket = st.secrets["aws"]["bucket_name"]
        access_key = st.secrets["aws"]["access_key_id"]
        secret_key = st.secrets["aws"]["secret_access_key"]
        region = st.secrets["aws"].get("region_name", "ap-south-1")
        
        s3_file_key = st.sidebar.text_input(
            "Enter S3 file path:",
            value="t20_bbb.csv"
        )
        
        if st.sidebar.button("Load from S3", key="load_complete"):
            loaded_df = load_from_s3(bucket, s3_file_key, access_key, secret_key, region)
            if loaded_df is not None:
                st.session_state.df = loaded_df
                df = loaded_df
        
        # Show current loaded data info
        if st.session_state.df is not None:
            st.sidebar.info(f"📊 Current data: {len(st.session_state.df):,} rows")
    else:
        st.sidebar.warning("⚠️ AWS credentials not configured in secrets.toml")

# Add a clear data button
if st.session_state.df is not None:
    if st.sidebar.button("🗑️ Clear Loaded Data"):
        st.session_state.df = None
        st.rerun()
        
# ===== Main App Logic =====
# if df is not None:
#     # Update column names for generalized dataset (Himanish format)
#     # MatNum -> p_match, batsmanName -> bat, inningNumber -> inns, etc.
    
#     # Compute static filters
#     test_nums = sorted(df['p_match'].dropna().unique())
#     test_num_options = ["All"] + [str(num) for num in test_nums]
#     batting_teams = sorted(df['team_bat'].dropna().unique())

#     col1, col2 = st.columns(2)

#     with col1:
#         selected_test_str = st.selectbox("Select Match Number", test_num_options, index=0)
#         selected_test_num = None if selected_test_str == "All" else int(selected_test_str)
        
#         team_bat_options = ["All"] + list(batting_teams)
#         selected_team = st.selectbox("Select Batting Team", team_bat_options, index=0)
#         selected_team = None if selected_team == "All" else selected_team

#     # Compute dependent filters
#     if selected_team:
#         player_list = sorted(df[df['team_bat'] == selected_team]['bat'].dropna().unique())
#     else:
#         player_list = sorted(df['bat'].dropna().unique())
    
#     player_options = ["All"] + list(set(player_list))
    
#     # Innings options
#     if selected_team and selected_test_num:
#         inns = df[(df['team_bat'] == selected_team) & (df['p_match'] == selected_test_num)]['inns']
#     elif selected_team:
#         inns = df[df['team_bat'] == selected_team]['inns']
#     elif selected_test_num:
#         inns = df[df['p_match'] == selected_test_num]['inns']
#     else:
#         inns = df['inns']

#     innings_options = sorted(inns.dropna().unique())
#     innings_display = ["All"] + [str(i) for i in innings_options]

#     # Bowler list
#     if selected_team:
#         bowler_list = sorted(df[df['team_bowl'] != selected_team]['bowl'].dropna().unique())
#     else:
#         bowler_list = sorted(df['bowl'].dropna().unique())

#     with col2:
#         selected_inns_str = st.selectbox("Select Innings", innings_display, index=0)
#         selected_inns = None if selected_inns_str == "All" else int(selected_inns_str)
        
#         selected_player = st.selectbox("Select Player", player_options)
#         selected_player = None if selected_player == "All" else selected_player

#         selected_bowler = st.selectbox("Select Bowler", ['All'] + list(bowler_list), index=0)
#         bowler_name = None if selected_bowler == "All" else selected_bowler

#     # Competition filter (optional)
#     if 'competition' in df.columns:
#         competitions = sorted(df['competition'].dropna().unique())
#         competition_options = ["All"] + list(competitions)
#         selected_competition = st.selectbox("Select Competition", competition_options, index=0)
#         selected_competition = None if selected_competition == "All" else selected_competition
#     else:
#         selected_competition = None
# ===== Main App Logic =====
if df is not None:
    # Compute static filters
    test_nums = sorted(df['p_match'].dropna().unique())
    test_num_options = ["All"] + [str(num) for num in test_nums]

    col1, col2 = st.columns(2)

    with col1:
        # STEP 1: Select Match Number
        selected_test_str = st.selectbox("Select Match Number", test_num_options, index=0)
        selected_test_num = None if selected_test_str == "All" else int(selected_test_str)
        
        # STEP 2: Filter teams based on selected match
        if selected_test_num:
            filtered_by_match = df[df['p_match'] == selected_test_num]
        else:
            filtered_by_match = df
        
        batting_teams = sorted(filtered_by_match['team_bat'].dropna().unique())
        team_bat_options = ["All"] + list(batting_teams)
        selected_team = st.selectbox("Select Batting Team", team_bat_options, index=0)
        selected_team = None if selected_team == "All" else selected_team

    # STEP 3: Filter innings based on match + team
    if selected_team:
        filtered_by_team = filtered_by_match[filtered_by_match['team_bat'] == selected_team]
    else:
        filtered_by_team = filtered_by_match
    
    innings_options = sorted(filtered_by_team['inns'].dropna().unique())
    innings_display = ["All"] + [str(i) for i in innings_options]

    with col2:
        # STEP 4: Select Innings
        selected_inns_str = st.selectbox("Select Innings", innings_display, index=0)
        selected_inns = None if selected_inns_str == "All" else int(selected_inns_str)
        
        # STEP 5: Filter players based on match + team + innings
        if selected_inns:
            filtered_by_innings = filtered_by_team[filtered_by_team['inns'] == selected_inns]
        else:
            filtered_by_innings = filtered_by_team
        
        player_list = sorted(filtered_by_innings['bat'].dropna().unique())
        player_options = ["All"] + list(set(player_list))
        selected_player = st.selectbox("Select Player", player_options)
        selected_player = None if selected_player == "All" else selected_player

        # STEP 6: Filter bowlers based on match + opposing team
        if selected_team:
            bowler_list = sorted(filtered_by_match[filtered_by_match['team_bowl'] != selected_team]['bowl'].dropna().unique())
        else:
            bowler_list = sorted(filtered_by_match['bowl'].dropna().unique())
        
        selected_bowler = st.selectbox("Select Bowler", ['All'] + list(bowler_list), index=0)
        bowler_name = None if selected_bowler == "All" else selected_bowler

    # Competition filter (optional)
    if 'competition' in df.columns:
        competitions = sorted(df['competition'].dropna().unique())
        competition_options = ["All"] + list(competitions)
        selected_competition = st.selectbox("Select Competition", competition_options, index=0)
        selected_competition = None if selected_competition == "All" else selected_competition
    else:
        selected_competition = None

    st.markdown("**Select Plot Types to Display:**")
    plot_types = st.multiselect(
        "Choose plot(s):",
        [
            "Spike Plot with Stats",
            "Wagon Zone Plot with Stats"
        ]
    )

    transparent_bg = st.checkbox("Transparent Background for Plots", value=False)
    fig_spike, fig_wagon = None, None

    if plot_types:
        if "Spike Plot with Stats" in plot_types:
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

            with col3:
                st.markdown("## Run Filter (Spike Plot)")

                if "run_init_spike" not in st.session_state:
                    st.session_state["run_all_spike"] = True
                    for i in range(7):
                        st.session_state[f'run_{i}_spike'] = True
                    st.session_state["run_init_spike"] = True

                def sync_all_to_individual_spike():
                    all_selected = st.session_state["run_all_spike"]
                    for i in range(7):
                        st.session_state[f'run_{i}_spike'] = all_selected

                def sync_individual_to_all_spike():
                    all_selected = all(st.session_state[f'run_{i}_spike'] for i in range(7))
                    st.session_state["run_all_spike"] = all_selected

                st.checkbox("All", key="run_all_spike", on_change=sync_all_to_individual_spike)

                for i in range(7):
                    st.checkbox(str(i), key=f'run_{i}_spike', on_change=sync_individual_to_all_spike)

                individual_selected_spike = [i for i in range(7) if st.session_state.get(f'run_{i}_spike', False)]

                if st.session_state["run_all_spike"]:
                    filtered_runs_spike = None
                elif individual_selected_spike:
                    filtered_runs_spike = individual_selected_spike
                else:
                    filtered_runs_spike = []
                    
            if filtered_runs_spike == []:
                st.warning("Please select at least one run value to display the plot.")
            else:
                fig_spike = spike_plot_custom(
                    df=df,
                    player_name=selected_player,
                    inns=selected_inns,
                    mat_num=selected_test_num,
                    team_bat=selected_team,
                    run_values=filtered_runs_spike,
                    bowler_name=bowler_name,
                    competition=selected_competition,
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
            
            with col1:
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

        if "Wagon Zone Plot with Stats" in plot_types:
            st.markdown("<h2 style='text-align: center;'>📊 Wagon Zone Plot with Stats</h2>", unsafe_allow_html=True)
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

                if "run_init_wagon" not in st.session_state:
                    st.session_state["run_all_wagon"] = True
                    for i in range(7):
                        st.session_state[f'run_{i}_wagon'] = True
                    st.session_state["run_init_wagon"] = True

                def sync_all_to_individual_wagon():
                    all_selected = st.session_state["run_all_wagon"]
                    for i in range(7):
                        st.session_state[f'run_{i}_wagon'] = all_selected

                def sync_individual_to_all_wagon():
                    all_selected = all(st.session_state[f'run_{i}_wagon'] for i in range(7))
                    st.session_state["run_all_wagon"] = all_selected

                st.checkbox("All", key="run_all_wagon", on_change=sync_all_to_individual_wagon)

                for i in range(7):
                    st.checkbox(str(i), key=f'run_{i}_wagon', on_change=sync_individual_to_all_wagon)

                individual_selected_wagon = [i for i in range(7) if st.session_state.get(f'run_{i}_wagon', False)]

                if st.session_state["run_all_wagon"]:
                    filtered_runs_wagon = None
                elif individual_selected_wagon:
                    filtered_runs_wagon = individual_selected_wagon
                else:
                    filtered_runs_wagon = []

            if filtered_runs_wagon == []:
                st.warning("Please select at least one run value to display the plot.")
            else:
                with col2:
                    fig_wagon = wagon_zone_plot(
                        df=df,
                        player_name=selected_player,
                        inns=selected_inns,
                        mat_num=selected_test_num,
                        bowler_name=bowler_name,
                        run_values=filtered_runs_wagon,
                        competition=selected_competition,
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
    st.info("Please select a dataset source to begin.")

