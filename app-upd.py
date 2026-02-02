import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO
import boto3
from botocore.exceptions import NoCredentialsError
import zipfile

# Set your custom password here
APP_PASSWORD = st.secrets["auth"]["password"]

# Session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Private Cricket App Login")
    password_input = st.text_input("Enter Access Password:", type="password")

    if password_input == APP_PASSWORD:
        st.success("Access granted.")
        st.session_state.authenticated = True
        st.rerun()
    elif password_input:
        st.error("Invalid password. Try again.")
    st.stop()

# Import your plotting methods
from SpikeUpd import spike_graph_plot as spike_plot_custom, spike_graph_plot_descriptive
from WagonUpd import wagon_zone_plot, wagon_zone_plot_descriptive

st.set_page_config(page_title="Cricket Wagon Wheel App" ,page_icon="🏏" ,layout="wide")
st.title("🏏 Cricket Wagon Wheel Analysis Dashboard")


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
            df = pd.read_csv(obj['Body'], low_memory=False)
            st.success(f"Loaded {len(df)} rows from S3")
            return df
    except NoCredentialsError:
        st.error("AWS credentials not found. Check your secrets.toml file.")
        return None
    except Exception as e:
        st.error(f"Error loading from S3: {str(e)}")
        return None
    
# zip files of figures
def create_zip_of_plots(figures_dict):
    """
    Create a ZIP file containing all generated plots
    
    Args:
        figures_dict: Dictionary with format {'filename': figure_object}
    
    Returns:
        BytesIO object containing the ZIP file
    """
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, fig in figures_dict.items():
            if fig is not None:
                # Save figure to a BytesIO buffer
                img_buffer = BytesIO()
                
                # Determine if transparent based on filename
                is_transparent = 'transparent' in filename.lower()
                
                fig.savefig(img_buffer, format='png', transparent=is_transparent, 
                           dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                
                # Add to ZIP
                zip_file.writestr(filename, img_buffer.getvalue())
                img_buffer.close()
    
    zip_buffer.seek(0)
    return zip_buffer

# ===== Dataset Selection =====
st.sidebar.header("📂 Select Dataset Source")
data_source = st.sidebar.selectbox(
    "Choose data source:",
    ["Upload Local File", "Preloaded 2026 T20 Data (S3)" ,"T20 Data for 2025 (S3)", "Complete T20-T20I Data (S3)", "Client Offline Storage - Complete T20 Data", "Client Offline Data - Since 2024", "Client Offline Data - Since 2024 WC"]
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
        st.sidebar.success(f"Loaded {len(df):,} rows")

elif data_source == "T20 Data for 2025 (S3)":
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
            st.sidebar.info(f"Current data: {len(st.session_state.df):,} rows")
    else:
        st.sidebar.warning("⚠️ AWS credentials not configured in secrets.toml")

elif data_source == "Complete T20-T20I Data (S3)":
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
            st.sidebar.info(f"Current data: {len(st.session_state.df):,} rows")
    else:
        st.sidebar.warning("⚠️ AWS credentials not configured in secrets.toml")

elif data_source == "Preloaded 2026 T20 Data (S3)":
    if "aws" in st.secrets:
        bucket = st.secrets["aws"]["bucket_name"]
        access_key = st.secrets["aws"]["access_key_id"]
        secret_key = st.secrets["aws"]["secret_access_key"]
        region = st.secrets["aws"].get("region_name", "ap-south-1")
        
        s3_file_key = st.sidebar.text_input(
            "Enter S3 file path:",
            value="t20_bbb_since_2026.csv"
        )
        
        if st.sidebar.button("Load from S3", key="load_complete"):
            loaded_df = load_from_s3(bucket, s3_file_key, access_key, secret_key, region)
            if loaded_df is not None:
                st.session_state.df = loaded_df
                df = loaded_df
        
        # Show current loaded data info
        if st.session_state.df is not None:
            st.sidebar.info(f"Current data: {len(st.session_state.df):,} rows")
    else:
        st.sidebar.warning("⚠️ AWS credentials not configured in secrets.toml")

elif data_source == "Client Offline Storage - Complete T20 Data":
    local_file_path = st.sidebar.text_input(
        "Enter local file path:",
        value="../data/daily_updated_t20_data/t20_bbb.csv"
    )
    
    if st.sidebar.button("Load from Local Storage", key="load_local_complete"):
        try:
            with st.spinner(f"Loading data from {local_file_path}..."):
                loaded_df = pd.read_csv(local_file_path, low_memory=False)
                st.session_state.df = loaded_df
                df = loaded_df
                st.sidebar.success(f"Loaded {len(loaded_df):,} rows from local storage")
        except FileNotFoundError:
            st.sidebar.error(f"File not found: {local_file_path}")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")
    
    # Show current loaded data info
    if st.session_state.df is not None:
        st.sidebar.info(f"Current data: {len(st.session_state.df):,} rows")

elif data_source == "Client Offline Data - Since 2024":
    local_file_path = st.sidebar.text_input(
        "Enter local file path:",
        value="../data/daily_updated_t20_data/t20_bbb_since_2024.csv"
    )
    
    if st.sidebar.button("Load from Local Storage", key="load_local_complete"):
        try:
            with st.spinner(f"Loading data from {local_file_path}..."):
                loaded_df = pd.read_csv(local_file_path, low_memory=False)
                st.session_state.df = loaded_df
                df = loaded_df
                st.sidebar.success(f"Loaded {len(loaded_df):,} rows from local storage")
        except FileNotFoundError:
            st.sidebar.error(f"File not found: {local_file_path}")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")
    
    # Show current loaded data info
    if st.session_state.df is not None:
        st.sidebar.info(f"Current data: {len(st.session_state.df):,} rows")

elif data_source == "Client Offline Data - Since 2024 WC":
    local_file_path = st.sidebar.text_input(
        "Enter local file path:",
        value="../data/daily_updated_t20_data/t20_bbb_since_2024_WC.csv"
    )
    
    if st.sidebar.button("Load from Local Storage", key="load_local_complete"):
        try:
            with st.spinner(f"Loading data from {local_file_path}..."):
                loaded_df = pd.read_csv(local_file_path, low_memory=False)
                st.session_state.df = loaded_df
                df = loaded_df
                st.sidebar.success(f"Loaded {len(loaded_df):,} rows from local storage")
        except FileNotFoundError:
            st.sidebar.error(f"File not found: {local_file_path}")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")
    
    # Show current loaded data info
    if st.session_state.df is not None:
        st.sidebar.info(f"Current data: {len(st.session_state.df):,} rows")


# Add a clear data button
if st.session_state.df is not None:
    if st.sidebar.button("🗑️ Clear Loaded Data"):
        st.session_state.df = None
        st.rerun()
        

# ===== BATCH PLOT GENERATION SECTION =====
if st.session_state.df is not None:
    st.sidebar.markdown("---")
    st.sidebar.header("📋 Batch Plot Generation")
    
    # Squad file upload
    # squad_file = st.sidebar.file_uploader(
    #     "Upload Squad File (Excel/CSV)", 
    #     type=["xlsx", "csv"],
    #     key="squad_upload"
    # )
    squad_file = "data/2026-T20IWC-Squads.xlsx"
    # read the squad file from s3



    if squad_file:
        # Read squad file
        try:
            if squad_file.endswith('.xlsx'):
                squad_df = pd.read_excel(squad_file)
            else:
                squad_df = pd.read_csv(squad_file)
            
            st.sidebar.success(f"Loaded {len(squad_df)} players")
            
            # Get unique teams
            if 'Team' in squad_df.columns:
                teams = sorted(squad_df['Team'].unique())
                selected_squad_team = st.sidebar.selectbox(
                    "Select Team",
                    teams,
                    key="squad_team_select"
                )
                
                # Get PIDs for selected team
                if 'Bt-ID' in squad_df.columns:
                    team_pids = squad_df[squad_df['Team'] == selected_squad_team]['Bt-ID'].astype(str).tolist()
                    st.sidebar.info(f"{len(team_pids)} players in {selected_squad_team}")
                    
                    # Plot type selection
                    batch_plot_types = st.sidebar.multiselect(
                        "Select plots to generate:",
                        ["Spike Graph Plot", "Spike Graph Descriptive", "Wagon Zone Plot", "Wagon Zone Descriptive"],
                        default=["Spike Graph Descriptive", "Wagon Zone Descriptive"],
                        key="batch_plot_select"
                    )
                    
                    # Transparent option
                    batch_transparent = st.sidebar.checkbox(
                        "Generate Transparent Plots", 
                        value=False,
                        key="batch_transparent"
                    )
                    
                    # Apply filters option
                    apply_filters_to_batch = st.sidebar.checkbox(
                        "Apply current filters to batch",
                        value=True,
                        help="Use the same filters (Competition, Date, etc.) for all players",
                        key="batch_apply_filters"
                    )
                    
                    # Generate button
                    if st.sidebar.button("🚀 Generate Batch Plots", type="primary", key="batch_generate_btn"):
                        if batch_plot_types:
                            # Ensure date column is datetime format
                            if 'date' in df.columns and df['date'].dtype == 'object':
                                df['date'] = pd.to_datetime(df['date'])
                            
                            with st.spinner(f"Generating plots for {len(team_pids)} players..."):
                                all_batch_figures = {}
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                error_count = 0
                                success_count = 0
                                
                                for idx, pid in enumerate(team_pids):
                                    # Update progress
                                    progress = (idx + 1) / len(team_pids)
                                    progress_bar.progress(progress)
                                    
                                    # Get player name
                                    player_row = squad_df[squad_df['Bt-ID'] == str(pid)]
                                    if not player_row.empty and 'Player' in squad_df.columns:
                                        player_name = player_row['Player'].iloc[0]
                                    else:
                                        player_name = f"Player_{pid}"
                                    
                                    status_text.text(f"Generating: {player_name} ({idx+1}/{len(team_pids)})")
                                    
                                    # Set filters - get values from session state if apply_filters is checked
                                    if apply_filters_to_batch:
                                        # Get filter values from session state (these are set in main app)
                                        filter_comp = st.session_state.get('filter_competition', 'All')
                                        filter_comp_val = None if filter_comp == "All" else filter_comp
                                        
                                        filter_team_bat = st.session_state.get('filter_team_bat', 'All')
                                        filter_team_bat_val = None if filter_team_bat == "All" else filter_team_bat
                                        
                                        filter_team_bowl = st.session_state.get('filter_team_bowl', 'All')
                                        filter_team_bowl_val = None if filter_team_bowl == "All" else filter_team_bowl
                                        
                                        filter_inns = st.session_state.get('filter_inns', 'All')
                                        filter_inns_val = None if filter_inns == "All" else int(filter_inns)
                                        
                                        filter_match = st.session_state.get('filter_match', 'All')
                                        filter_match_val = None if filter_match == "All" else int(filter_match)
                                        
                                        filter_bowler = st.session_state.get('filter_bowler', 'All')
                                        filter_bowler_val = None if filter_bowler == "All" else filter_bowler
                                        
                                        # Get date range from session state and convert to datetime
                                        date_range_state = st.session_state.get('date_range_filter', None)
                                        if date_range_state and len(date_range_state) == 2:
                                            # Convert date objects to datetime for plotting functions
                                            filter_date_from = pd.to_datetime(date_range_state[0])
                                            filter_date_to = pd.to_datetime(date_range_state[1])
                                        else:
                                            filter_date_from, filter_date_to = None, None
                                        
                                        batch_filters = {
                                            'competition': filter_comp_val,
                                            'date_from': filter_date_from,
                                            'date_to': filter_date_to,
                                            'inns': filter_inns_val,
                                            'mat_num': filter_match_val,
                                            'team_bat': filter_team_bat_val,
                                            'team_bowl': filter_team_bowl_val,
                                            'bowler_name': filter_bowler_val,
                                            'bowler_id': None,
                                            'run_values': None,
                                            'over_values': None,
                                            'phase': None,
                                            'transparent': batch_transparent,
                                            'show_title': True,
                                            'show_summary': True,
                                            'show_legend': True,
                                            'runs_count': True,
                                            'show_fours_sixes': True,
                                            'show_control': True,
                                            'show_prod_shot': True,
                                            'show_bowler': True,
                                            'show_ground': True
                                        }
                                    else:
                                        batch_filters = {
                                            'competition': None,
                                            'date_from': None,
                                            'date_to': None,
                                            'inns': None,
                                            'mat_num': None,
                                            'team_bat': None,
                                            'team_bowl': None,
                                            'bowler_name': None,
                                            'bowler_id': None,
                                            'run_values': None,
                                            'over_values': None,
                                            'phase': None,
                                            'transparent': batch_transparent,
                                            'show_title': True,
                                            'show_summary': True,
                                            'show_legend': True,
                                            'runs_count': True,
                                            'show_fours_sixes': True,
                                            'show_control': True,
                                            'show_prod_shot': True,
                                            'show_bowler': True,
                                            'show_ground': True
                                        }
                                    
                                    # Generate selected plots
                                    try:
                                        if "Spike Graph Plot" in batch_plot_types:
                                            spike_filters = {k: v for k, v in batch_filters.items()}
                                            fig = spike_plot_custom(df=df, pid=pid, player_name=None, **spike_filters)
                                            if fig is not None:
                                                all_batch_figures[f"{player_name}_spike_graph_plot.png"] = fig
                                                success_count += 1
                                        
                                        if "Spike Graph Descriptive" in batch_plot_types:
                                            spike_filters = {k: v for k, v in batch_filters.items()}
                                            fig = spike_graph_plot_descriptive(df=df, pid=pid, player_name=None, **spike_filters)
                                            if fig is not None:
                                                all_batch_figures[f"{player_name}_spike_graph_desc.png"] = fig
                                                success_count += 1
                                        
                                        if "Wagon Zone Plot" in batch_plot_types:
                                            # Wagon plots don't have show_legend or show_ground parameters
                                            wagon_filters = {k: v for k, v in batch_filters.items() if k not in ['show_legend', 'show_ground']}
                                            fig = wagon_zone_plot(df=df, pid=pid, player_name=None, **wagon_filters)
                                            if fig is not None:
                                                all_batch_figures[f"{player_name}_wagon_zone_plot.png"] = fig
                                                success_count += 1
                                        
                                        if "Wagon Zone Descriptive" in batch_plot_types:
                                            # Wagon plots don't have show_legend or show_ground parameters
                                            wagon_filters = {k: v for k, v in batch_filters.items() if k not in ['show_legend', 'show_ground']}
                                            fig = wagon_zone_plot_descriptive(df=df, pid=pid, player_name=None, **wagon_filters)
                                            if fig is not None:
                                                all_batch_figures[f"{player_name}_wagon_zone_desc.png"] = fig
                                                success_count += 1
                                    
                                    except ZeroDivisionError:
                                        error_count += 1
                                        # Player has no data
                                    except Exception as e:
                                        error_count += 1
                                        st.sidebar.warning(f"⚠️ {player_name}: {str(e)[:100]}")
                                
                                progress_bar.empty()
                                status_text.empty()
                                
                                # Create ZIP and download
                                if all_batch_figures:
                                    zip_buffer = create_zip_of_plots(all_batch_figures)
                                    
                                    st.sidebar.success(f"Generated {len(all_batch_figures)} plots!")
                                    if error_count > 0:
                                        st.sidebar.warning(f"⚠️ {error_count} players had no data")
                                    
                                    st.sidebar.download_button(
                                        label=f"📦 Download {selected_squad_team} Batch ZIP",
                                        data=zip_buffer.getvalue(),
                                        file_name=f"{selected_squad_team}_batch_plots.zip",
                                        mime="application/zip",
                                        key="batch_download_btn"
                                    )
                                else:
                                    st.sidebar.error("No plots were generated. Check if PIDs have data.")
                        else:
                            st.sidebar.warning("⚠️ Please select at least one plot type")
                else:
                    st.sidebar.error(" 'Bt-ID' column not found in squad file")
            else:
                st.sidebar.error(" 'Team' column not found in squad file")
        
        except Exception as e:
            st.sidebar.error(f" Error reading squad file: {str(e)}")


# ===== Main App Logic =====
if df is not None:
    # Convert date column to datetime if it exists and isn't already
    if 'date' in df.columns and df['date'].dtype == 'object':
        df['date'] = pd.to_datetime(df['date'])
    
    # ===== CASCADING FILTERS SECTION =====
    st.markdown("---")
    st.subheader("Filter Options")
    
    # Create 4 columns for filters
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    # Initialize working dataframe
    working_df = df.copy()
    
    # ===== COLUMN 1: Date, Competition, Match =====
    with filter_col1:
        
        # Date Range Filter (always shown)
        if 'date' in df.columns:
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if len(date_range) == 2:
                date_from, date_to = date_range
                working_df = working_df[
                    (working_df['date'].dt.date >= date_from) & 
                    (working_df['date'].dt.date <= date_to)
                ]
            else:
                date_from, date_to = None, None
        else:
            date_from, date_to = None, None
        
        # Competition Filter (from working_df)
        competitions = sorted(working_df['competition'].dropna().unique())
        competition_options = ["All"] + list(competitions)
        selected_competition = st.selectbox("Competition", competition_options, index=0)
        
        if selected_competition != "All":
            working_df = working_df[working_df['competition'] == selected_competition]
            selected_competition_value = selected_competition
        else:
            selected_competition_value = None
        
        # Match Number Filter (from working_df)
        mat_nums = sorted(working_df['p_match'].dropna().unique())
        mat_num_options = ["All"] + [str(int(num)) for num in mat_nums]
        selected_mat_str = st.selectbox("Match Number", mat_num_options, index=0)
        
        if selected_mat_str != "All":
            selected_mat_num = int(selected_mat_str)
            working_df = working_df[working_df['p_match'] == selected_mat_num]
        else:
            selected_mat_num = None
    
    # ===== COLUMN 2: Batting Team, Batter, Player ID =====
    with filter_col2:
        
        # Batting Team Filter (from working_df)
        batting_teams = sorted(working_df['team_bat'].dropna().unique())
        team_bat_options = ["All"] + list(batting_teams)
        selected_team = st.selectbox("Batting Team", team_bat_options, index=0)
        
        if selected_team != "All":
            working_df = working_df[working_df['team_bat'] == selected_team]
            selected_team_value = selected_team
        else:
            selected_team_value = None
        
        # Player Filter (from working_df, only from selected batting team)
        player_list = sorted(working_df['bat'].dropna().unique())
        player_options = ["All"] + list(player_list)
        selected_player = st.selectbox("Batter", player_options, index=0)
        
        if selected_player != "All":
            selected_player_value = selected_player
        else:
            selected_player_value = None
        
        # PID Filter (dropdown with unique p_bat values)
        pid_list = sorted(working_df['p_bat'].dropna().unique())
        pid_options = ["All"] + [str(int(p)) for p in pid_list]
        selected_pid_str = st.selectbox("Player ID (PID)", pid_options, index=0)
        
        if selected_pid_str != "All":
            selected_pid = int(selected_pid_str)
        else:
            selected_pid = None
    
    # ===== COLUMN 3: Bowling Team, Bowler, Bowler PID =====
    with filter_col3:
        
        # Bowling Team Filter (from working_df, excluding batting team)
        bowling_teams = sorted(working_df['team_bowl'].dropna().unique())
        # Exclude selected batting team from bowling options
        if selected_team != "All":
            bowling_teams = [t for t in bowling_teams if t != selected_team]
        team_bowl_options = ["All"] + list(bowling_teams)
        selected_team_bowl = st.selectbox("Bowling Team", team_bowl_options, index=0)
        
        if selected_team_bowl != "All":
            working_df = working_df[working_df['team_bowl'] == selected_team_bowl]
            selected_team_bowl_value = selected_team_bowl
        else:
            selected_team_bowl_value = None
        
        # Bowler Filter (from working_df, only from bowling team)
        bowler_list = sorted(working_df['bowl'].dropna().unique())
        bowler_options = ["All"] + list(bowler_list)
        selected_bowler = st.selectbox("Bowler", bowler_options, index=0)
        
        if selected_bowler != "All":
            bowler_name = selected_bowler
        else:
            bowler_name = None
        
        # Bowler PID Filter (dropdown with unique p_bowl values)
        bowl_pid_list = sorted(working_df['p_bowl'].dropna().unique())
        bowl_pid_options = ["All"] + [str(int(p)) for p in bowl_pid_list]
        selected_bowl_pid_str = st.selectbox("Bowler PID", bowl_pid_options, index=0)
        
        if selected_bowl_pid_str != "All":
            bowler_id = int(selected_bowl_pid_str)
        else:
            bowler_id = None
    
    # ===== COLUMN 4: Innings, Overs, Phases =====
    with filter_col4:
        
        # Innings Filter (from working_df)
        innings_options = sorted(working_df['inns'].dropna().unique())
        innings_display = ["All"] + [str(int(i)) for i in innings_options]
        selected_inns_str = st.selectbox("Innings", innings_display, index=0)
        
        if selected_inns_str != "All":
            selected_inns = int(selected_inns_str)
            working_df = working_df[working_df['inns'] == selected_inns]
        else:
            selected_inns = None
        
        # Overs Filter (multiselect)
        if 'over' in working_df.columns:
            over_options = sorted(working_df['over'].dropna().unique())
            selected_overs = st.multiselect(
                "Overs",
                options=[int(o) for o in over_options],
                default=None,
                help="Select specific overs (leave empty for all)"
            )
            over_values = selected_overs if selected_overs else None
        else:
            over_values = None
        
        # Phase Filter (dropdown)
        phase_options = ["All", "Powerplay (1-6)", "Middle (7-15)", "Death (16-20)"]
        selected_phase_str = st.selectbox("Phase", phase_options, index=0)
        
        phase_map = {
            "Powerplay (1-6)": 1,
            "Middle (7-15)": 2,
            "Death (16-20)": 3
        }
        phase = phase_map.get(selected_phase_str, None)
    
    # ===== DATA VALIDATION =====
    st.markdown("---")
    
    # Check if we have data after all filters
    if working_df.empty:
        st.error("⚠️ No data available for the selected filters. Please adjust your filter selections.")
        # st.info("💡 Try selecting 'All' for some filters or choosing different combinations.")
        st.stop()
    else:
        pass
        # st.success(f"Found {len(working_df):,} balls matching your filters")

    st.markdown("**Select Plot Types to Display:**")
    plot_types = st.multiselect(
        "Choose plot(s):",
        [
            "Spike Plot (White Background)",
            "Spike Plot (Transparent Background)",
            "Spike Graph Descriptive",
            "Spike Graph Descriptive (Transparent)",
            "Wagon Zone Plot (White Background)",
            "Wagon Zone Plot (Transparent Background)",
            "Wagon Zone Descriptive",
            "Wagon Zone Descriptive (Transparent)"
        ]
    )

    fig_spike, fig_wagon, fig_spike_trans, fig_wagon_trans, fig_spike_desc, fig_wagon_desc, fig_spike_desc_trans, fig_wagon_desc_trans = None, None, None, None, None, None, None, None

    if plot_types:
        if "Spike Plot (White Background)" in plot_types:
            st.markdown("<h2 style='text-align: center;'>Spike Plot (White Background)</h2>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.markdown("## Customize Plot Info")
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
                    player_name=selected_player_value,
                    pid=selected_pid,
                    inns=selected_inns,
                    mat_num=selected_mat_num,
                    team_bat=selected_team_value,
                    team_bowl=selected_team_bowl_value,
                    run_values=filtered_runs_spike,
                    bowler_name=bowler_name,
                    bowler_id=bowler_id,
                    competition=selected_competition_value,
                    transparent=False,
                    over_values=over_values,
                    phase=phase,
                    date_from=date_from,
                    date_to=date_to,
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
                if fig_spike:
                    buf = BytesIO()
                    fig_spike.savefig(buf, format="png", transparent=False, dpi=300, bbox_inches='tight')
                    buf.seek(0)
                    st.download_button(
                        label="📅 Download Plot as PNG",
                        data=buf.getvalue(),
                        file_name=f"{selected_player}_spikeplot.png",
                        mime="image/png",
                        key="spike_download"
                    )

        if "Spike Plot (Transparent Background)" in plot_types:
            st.markdown("<h2 style='text-align: center;'>Spike Plot (Transparent Background)</h2>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.markdown("## Customize Plot Info")
                show_title_trans = st.checkbox("Show Plot Title", value=True, key="spike_trans_title")
                show_legend_trans = st.checkbox("Show Legend", value=True, key="spike_trans_legend")
                show_summary_trans = st.checkbox("Show Runs Summary", value=True, key="spike_trans_summary")
                runs_count_trans = st.checkbox("Show Runs Count", value=True, key="spike_trans_runs")
                show_fours_sixes_trans = st.checkbox("Show 4s and 6s", value=True, key="spike_trans_fs")
                show_bowler_trans = st.checkbox("Show Bowler", value=True, key="spike_trans_bowler")
                show_control_trans = st.checkbox("Show Control %", value=True, key="spike_trans_control")
                show_prod_shot_trans = st.checkbox("Show Productive Shot", value=True, key="spike_trans_prod")
                show_ground_trans = st.checkbox("Show Ground Image", value=True, key="spike_trans_ground")

            with col3:
                st.markdown("## Run Filter (Spike Plot)")

                if "run_init_spike_trans" not in st.session_state:
                    st.session_state["run_all_spike_trans"] = True
                    for i in range(7):
                        st.session_state[f'run_{i}_spike_trans'] = True
                    st.session_state["run_init_spike_trans"] = True

                def sync_all_to_individual_spike_trans():
                    all_selected = st.session_state["run_all_spike_trans"]
                    for i in range(7):
                        st.session_state[f'run_{i}_spike_trans'] = all_selected

                def sync_individual_to_all_spike_trans():
                    all_selected = all(st.session_state[f'run_{i}_spike_trans'] for i in range(7))
                    st.session_state["run_all_spike_trans"] = all_selected

                st.checkbox("All", key="run_all_spike_trans", on_change=sync_all_to_individual_spike_trans)

                for i in range(7):
                    st.checkbox(str(i), key=f'run_{i}_spike_trans', on_change=sync_individual_to_all_spike_trans)

                individual_selected_spike_trans = [i for i in range(7) if st.session_state.get(f'run_{i}_spike_trans', False)]

                if st.session_state["run_all_spike_trans"]:
                    filtered_runs_spike_trans = None
                elif individual_selected_spike_trans:
                    filtered_runs_spike_trans = individual_selected_spike_trans
                else:
                    filtered_runs_spike_trans = []
                    
            if filtered_runs_spike_trans == []:
                st.warning("Please select at least one run value to display the plot.")
            else:
                fig_spike_trans = spike_plot_custom(
                    df=df,
                    player_name=selected_player_value,
                    pid=selected_pid,
                    inns=selected_inns,
                    mat_num=selected_mat_num,
                    team_bat=selected_team_value,
                    team_bowl=selected_team_bowl_value,
                    run_values=filtered_runs_spike_trans,
                    bowler_name=bowler_name,
                    bowler_id=bowler_id,
                    competition=selected_competition_value,
                    transparent=True,
                    over_values=over_values,
                    phase=phase,
                    date_from=date_from,
                    date_to=date_to,
                    show_title=show_title_trans,
                    show_summary=show_summary_trans,
                    show_legend=show_legend_trans,
                    runs_count=runs_count_trans,
                    show_fours_sixes=show_fours_sixes_trans,
                    show_control=show_control_trans,
                    show_prod_shot=show_prod_shot_trans,
                    show_bowler=show_bowler_trans,
                    show_ground=show_ground_trans
                )
                with col2:
                    st.pyplot(fig_spike_trans)
            
            with col1:
                if fig_spike_trans:
                    buf = BytesIO()
                    fig_spike_trans.savefig(buf, format="png", transparent=True, dpi=300, bbox_inches='tight')
                    buf.seek(0)
                    st.download_button(
                        label="📅 Download Plot as PNG",
                        data=buf.getvalue(),
                        file_name=f"{selected_player}_spike_plot_transparent.png",
                        mime="image/png",
                        key="spike_trans_download"
                    )

        if "Spike Graph Descriptive" in plot_types:
            st.markdown("<h2 style='text-align: center;'>Spike Graph Descriptive</h2>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.markdown("## Customize Plot Info")
                show_title_desc = st.checkbox("Show Plot Title", value=True, key="spike_desc_title")
                show_legend_desc = st.checkbox("Show Legend", value=True, key="spike_desc_legend")
                show_summary_desc = st.checkbox("Show Runs Summary", value=True, key="spike_desc_summary")
                runs_count_desc = st.checkbox("Show Runs Count", value=True, key="spike_desc_runs")
                show_fours_sixes_desc = st.checkbox("Show 4s and 6s", value=True, key="spike_desc_fs")
                show_bowler_desc = st.checkbox("Show Bowler", value=True, key="spike_desc_bowler")
                show_control_desc = st.checkbox("Show Control %", value=True, key="spike_desc_control")
                show_prod_shot_desc = st.checkbox("Show Productive Shot", value=True, key="spike_desc_prod")
                show_ground_desc = st.checkbox("Show Ground Image", value=True, key="spike_desc_ground")

            with col3:
                st.markdown("## Run Filter (Spike Graph)")

                if "run_init_spike_desc" not in st.session_state:
                    st.session_state.run_init_spike_desc = True
                    for i in range(7):
                        st.session_state[f'run_{i}_spike_desc'] = True
                    st.session_state["run_all_spike_desc"] = True

                def sync_all_to_individual_spike_desc():
                    for i in range(7):
                        st.session_state[f'run_{i}_spike_desc'] = st.session_state["run_all_spike_desc"]

                def sync_individual_to_all_spike_desc():
                    if all(st.session_state.get(f'run_{i}_spike_desc', False) for i in range(7)):
                        st.session_state["run_all_spike_desc"] = True

                st.checkbox("All", key="run_all_spike_desc", on_change=sync_all_to_individual_spike_desc)

                for i in range(7):
                    st.checkbox(str(i), key=f'run_{i}_spike_desc', on_change=sync_individual_to_all_spike_desc)

                individual_selected_spike_desc = [i for i in range(7) if st.session_state.get(f'run_{i}_spike_desc', False)]

                if st.session_state["run_all_spike_desc"]:
                    filtered_runs_spike_desc = None
                elif individual_selected_spike_desc:
                    filtered_runs_spike_desc = individual_selected_spike_desc
                else:
                    filtered_runs_spike_desc = []
                    
            if filtered_runs_spike_desc == []:
                st.warning("Please select at least one run value to display the plot.")
            else:
                fig_spike_desc = spike_graph_plot_descriptive(
                    df=df,
                    player_name=selected_player_value,
                    pid=selected_pid,
                    inns=selected_inns,
                    mat_num=selected_mat_num,
                    team_bat=selected_team_value,
                    team_bowl=selected_team_bowl_value,
                    run_values=filtered_runs_spike_desc,
                    bowler_name=bowler_name,
                    bowler_id=bowler_id,
                    competition=selected_competition_value,
                    transparent=False,
                    over_values=over_values,
                    phase=phase,
                    date_from=date_from,
                    date_to=date_to,
                    show_title=show_title_desc,
                    show_summary=show_summary_desc,
                    show_legend=show_legend_desc,
                    runs_count=runs_count_desc,
                    show_fours_sixes=show_fours_sixes_desc,
                    show_control=show_control_desc,
                    show_prod_shot=show_prod_shot_desc,
                    show_bowler=show_bowler_desc,
                    show_ground=show_ground_desc
                )
                with col2:
                    st.pyplot(fig_spike_desc)
            
            with col1:
                if fig_spike_desc:
                    buf = BytesIO()
                    fig_spike_desc.savefig(buf, format="png", transparent=False, dpi=300, bbox_inches='tight')
                    buf.seek(0)
                    st.download_button(
                        label="📅 Download Plot as PNG",
                        data=buf.getvalue(),
                        file_name=f"{selected_player}_spike_graph_descriptive.png",
                        mime="image/png",
                        key="spike_desc_download"
                    )

        if "Spike Graph Descriptive (Transparent)" in plot_types:
            st.markdown("<h2 style='text-align: center;'>Spike Graph Descriptive (Transparent)</h2>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.markdown("## Customize Plot Info")
                show_title_desc_trans = st.checkbox("Show Plot Title", value=True, key="spike_desc_trans_title")
                show_legend_desc_trans = st.checkbox("Show Legend", value=True, key="spike_desc_trans_legend")
                show_summary_desc_trans = st.checkbox("Show Runs Summary", value=True, key="spike_desc_trans_summary")
                runs_count_desc_trans = st.checkbox("Show Runs Count", value=True, key="spike_desc_trans_runs")
                show_fours_sixes_desc_trans = st.checkbox("Show 4s and 6s", value=True, key="spike_desc_trans_fs")
                show_bowler_desc_trans = st.checkbox("Show Bowler", value=True, key="spike_desc_trans_bowler")
                show_control_desc_trans = st.checkbox("Show Control %", value=True, key="spike_desc_trans_control")
                show_prod_shot_desc_trans = st.checkbox("Show Productive Shot", value=True, key="spike_desc_trans_prod")
                show_ground_desc_trans = st.checkbox("Show Ground Image", value=True, key="spike_desc_trans_ground")

            with col3:
                st.markdown("## Run Filter (Spike Graph)")

                if "run_init_spike_desc_trans" not in st.session_state:
                    st.session_state.run_init_spike_desc_trans = True
                    for i in range(7):
                        st.session_state[f'run_{i}_spike_desc_trans'] = True
                    st.session_state["run_all_spike_desc_trans"] = True

                def sync_all_to_individual_spike_desc_trans():
                    for i in range(7):
                        st.session_state[f'run_{i}_spike_desc_trans'] = st.session_state["run_all_spike_desc_trans"]

                def sync_individual_to_all_spike_desc_trans():
                    if all(st.session_state.get(f'run_{i}_spike_desc_trans', False) for i in range(7)):
                        st.session_state["run_all_spike_desc_trans"] = True

                st.checkbox("All", key="run_all_spike_desc_trans", on_change=sync_all_to_individual_spike_desc_trans)

                for i in range(7):
                    st.checkbox(str(i), key=f'run_{i}_spike_desc_trans', on_change=sync_individual_to_all_spike_desc_trans)

                individual_selected_spike_desc_trans = [i for i in range(7) if st.session_state.get(f'run_{i}_spike_desc_trans', False)]

                if st.session_state["run_all_spike_desc_trans"]:
                    filtere


