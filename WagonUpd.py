import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import cm
from matplotlib.patches import Wedge
import pandas as pd

def wagon_zone_plot(
    df, player_name=None, inns=None, mat_num=None, bowler_name=None, team_bat=None, 
    team_bowl=None, run_values=None, competition=None, transparent=False, 
    date_from=None, date_to=None,
    show_title=True, show_summary=True,show_fours_sixes=True, show_control=True, 
    show_prod_shot=True,runs_count=True, show_bowler=True
):
    # ---- Apply Filters for Plotting ----
    local_df = df.copy()


    if player_name:
        local_df = local_df[local_df['bat'] == player_name] # bat
    if mat_num:
        # local_df = local_df[local_df['TestNum'] == mat_num]
        local_df = local_df[local_df['p_match'] == mat_num] # p_match

    if inns:
        local_df = local_df[local_df['inns'] == inns] # inns

    if bowler_name:
        local_df = local_df[local_df['bowl'] == bowler_name] #bowl

    if run_values is not None:
        local_df = local_df[local_df['batruns'].isin(run_values)] #batruns

    if team_bat is not None and team_bat != "All":
        local_df = local_df[local_df['team_bat'] == team_bat]

    if team_bowl is not None and team_bowl != "All":
        local_df = local_df[local_df['team_bowl'] == team_bowl]
    #competition filter
    if competition:
        local_df = local_df[local_df['competition'] == competition]

    # Date range filter
    if date_from is not None:
        local_df = local_df[local_df['date'] >= pd.to_datetime(date_from)]

    if date_to is not None:
        local_df = local_df[local_df['date'] <= pd.to_datetime(date_to)]


    if player_name is None:
        innings_valid_balls = local_df.copy()  # include all for team
        innings_runs = innings_valid_balls['score'].sum() #score
    else:
        innings_valid_balls = local_df[local_df['wide'] == 0]
        innings_runs = innings_valid_balls['batruns'].sum() #batruns

    innings_balls = innings_valid_balls[innings_valid_balls['wide'] == 0].shape[0]  # consistent valid balls

    # --- Core Filtering Logic (Team vs Player Mode) ---
    if player_name is None:
        valid_balls = local_df[local_df['wide'] == 0]
        valid_shots = valid_balls[~((valid_balls['wagonX'] == 0) & (valid_balls['wagonY'] == 0))]

        # ADD THESE TWO LINES:
        valid_shots['isFour'] = (valid_shots['outcome'] == 'four').astype(int)
        valid_shots['isSix'] = (valid_shots['outcome'] == 'six').astype(int)

        total_score = valid_shots['score'].sum() #score
        # total_4s = valid_shots['isFour'].sum()
        # total_6s = valid_shots['isSix'].sum()
        #logic update for generalization
        total_4s = (valid_shots['outcome'] == 'four').sum()
        total_6s = (valid_shots['outcome'] == 'six').sum()

        balls_faced = valid_balls.shape[0]

        # control_pct = round(
        #     (valid_balls[valid_balls['control'] == 1].shape[0]) / balls_faced * 100, 2 
        # )#shotControl to control

        # Control calculation like spike graph
        controlled_balls = valid_balls[valid_balls['control'] == 1]
        control_pct = round(len(controlled_balls) / len(valid_balls) * 100, 2) if len(valid_balls) > 0 else 0.0

        

        shot_summary = valid_shots.groupby('shot').agg({ #shot
            'score': 'sum', #score
            'isFour': 'sum', #we need to check the outcome column as four and six is there as strings
            'isSix': 'sum'
        }).sort_values(by='score', ascending=False) #score
    else:
        valid_balls = local_df[(local_df['wide'] == 0) & (~local_df['control'].isna())]
        valid_shots = local_df[
            ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
        ].dropna(subset=['wagonX', 'wagonY'])

        # ADD THESE TWO LINES:
        valid_shots['isFour'] = (valid_shots['outcome'] == 'four').astype(int)
        valid_shots['isSix'] = (valid_shots['outcome'] == 'six').astype(int)

        total_score = valid_shots['batruns'].sum() #batruns
        # total_4s = valid_shots['isFour'].sum()
        # total_6s = valid_shots['isSix'].sum()
        total_4s = (valid_shots['outcome'] == 'four').sum()
        total_6s = (valid_shots['outcome'] == 'six').sum()
        
        balls_faced = valid_balls.shape[0]

        # control_pct = round(
        #     (valid_balls[valid_balls['control'] == 1].shape[0]) / balls_faced * 100, 2 
        # ) #shotControl to control
        
        #  Control calculation like spike graph
        controlled_balls = valid_balls[valid_balls['control'] == 1]
        control_pct = round(len(controlled_balls) / len(valid_balls) * 100, 2) if len(valid_balls) > 0 else 0.0

        shot_summary = valid_shots.groupby('shot').agg({ #shot
            'batruns': 'sum', #batruns
            'isFour': 'sum',
            'isSix': 'sum'
        }).sort_values(by='batruns', ascending=False) #batruns

    # Most Productive Shot
    if not shot_summary.empty:
        top_shot = shot_summary.iloc[0]
        top_shot_type = shot_summary.index[0]
        runs_col = 'score' if player_name is None else 'batruns' #score or batruns
        most_prod_shot_text = (
            f"{top_shot_type.upper()}: {int(top_shot[runs_col])} runs,\n"
            f"4s: {int(top_shot['isFour'])}, 6s: {int(top_shot['isSix'])}"
        )
    else:
        most_prod_shot_text = "No productive shot data"

    # Prepare data for quadrant plotting
    score_col = 'batruns' if player_name else 'score' #batruns or score
    player_data = valid_shots[['wagonX', 'wagonY', score_col, 'isFour', 'isSix']].copy()

    center_x, center_y = 180, 164
    def get_quadrant(x, y):
        angle = np.arctan2(y - center_y, x - center_x)
        degree = (np.degrees(angle) + 360) % 360
        return int(degree // 45)

    player_data['quadrant'] = player_data.apply(lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1)
    # if not player_data.empty:
    #     player_data['quadrant'] = player_data.apply(lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1)
    # else:
    #     player_data['quadrant'] = pd.Series(dtype='int')
    quadrant_totals = [player_data[player_data['quadrant'] == q][score_col].sum() for q in range(8)]
    total_score = sum(quadrant_totals)

    # Plot
    fig, ax = plt.subplots(figsize=(7, 7), facecolor='none' if transparent else 'white')
    ax.set_facecolor('none' if transparent else 'white')

    # Draw ground and pitch
    boundary = plt.Circle((center_x, center_y), 180, color='#8c8c8c', fill=False, linewidth=1.2)
    batter_dot = plt.Circle((center_x, center_y), radius=3, edgecolor='black', facecolor='green', zorder=2)
    ax.add_artist(boundary)
    ax.add_artist(batter_dot)

    for angle in range(0, 360, 45):
        rad = np.deg2rad(angle)
        x_end = center_x + 180 * np.cos(rad)
        y_end = center_y + 180 * np.sin(rad)
        ax.plot([center_x, x_end], [center_y, y_end], color='#8c8c8c', linewidth=1.3)

    # Highlight Top Zones
    top_quadrants = sorted(range(8), key=lambda i: quadrant_totals[i], reverse=True)[:2]
    rank_color = {top_quadrants[i]: 1.0 - i * 0.3 for i in range(len(top_quadrants))}
    cmap = cm.get_cmap('Blues')

    for i in range(8):
        theta1, theta2 = i * 45, (i + 1) * 45
        if i in rank_color:
            ax.add_patch(Wedge(center=(center_x, center_y), r=180, theta1=theta1, theta2=theta2,
                               color=cmap(rank_color[i]), alpha=0.3, zorder=0))
        mid_angle = np.deg2rad(theta1 + 22.5)
        label_x = center_x + 100 * np.cos(mid_angle)
        label_y = center_y + 100 * np.sin(mid_angle)
        ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=13,
                color='black' if i in top_quadrants else '#000',
                ha='center', va='center',fontweight = 'bold')

    ax.set_xlim(-20, 470)
    ax.set_ylim(-50, 370)
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.set_axis_off()

    # Determine team names
    # if not local_df.empty:
    #     team_bats = local_df['team_bat'].unique() 
    #     if len(team_bats) == 1:
    #         team_bat = team_bats[0]
    #         all_teams = df['team_bat'].unique().tolist() + df['team_bowl'].unique().tolist()
    #         team_bowl = [t for t in set(all_teams) if t != team_bat][0] if team_bat in all_teams else "Opponent"
    #     else:
    #         team_bowl = "All Teams"
    # else:
    #     team_bowl = "All Teams"
    
    # # Determine team names
    # if not local_df.empty:
    #     team_bats = local_df['team_bat'].unique() 
    #     if len(team_bats) == 1:
    #         team_bat = team_bats[0]
    #         # Filter by the same match to get correct opponent
    #         if mat_num is not None:
    #             match_df = df[df['p_match'] == mat_num]
    #         else:
    #             match_df = local_df
            
    #         # Get opponent from the same match
    #         team_bowls_in_match = match_df['team_bowl'].unique()
    #         team_bowl = [t for t in team_bowls_in_match if t != team_bat][0] if len(team_bowls_in_match) > 0 else "Opponents"
    #     else:
    #         team_bowl = "All Teams"
    # else:
    #     team_bowl = "All Teams"

    # if show_title:
    #     ax.set_title(
    #         f"{player_name} vs {team_bowl} | {competition} - Mat '{mat_num}', Inns: '{inns}'".upper(),
    #         fontsize=12, fontweight='bold', fontfamily='DejaVu Sans'
    #     )

    # Metadata for title - DO THIS FIRST
    if mat_num is None: mat_num = "All Matches"
    if inns is None: inns = "All Innings"
    if player_name is None: player_name = "All Players"
    if competition is None: competition = "All Comps"
    
    # Determine team names ONLY if not provided as parameters
    if not local_df.empty:
        # Only detect team_bat if it wasn't provided as a filter
        if team_bat is None or team_bat == "All":
            team_bats = local_df['team_bat'].unique() 
            if len(team_bats) == 1:
                team_bat = team_bats[0]
            else:
                team_bat = "All Teams"
        
        # Only detect team_bowl if it wasn't provided as a filter
        if team_bowl is None or team_bowl == "All":
            if mat_num is not None and mat_num != "All Matches":
                match_df = df[df['p_match'] == mat_num]
            else:
                match_df = local_df
            
            team_bowls_in_match = match_df['team_bowl'].unique()
            opponents = [t for t in team_bowls_in_match if t != team_bat]
            
            if len(opponents) == 1:
                team_bowl = opponents[0]
            elif len(opponents) > 1:
                team_bowl = "All Teams"
            else:
                team_bowl = "Opponents"
    else:
        if team_bat is None: team_bat = "All Teams"
        if team_bowl is None: team_bowl = "All Teams"
    
    if show_title:
        # Determine title display (match spike graph logic)
        if player_name and player_name != "All Players":
            title_name = player_name
            title_opponent = team_bowl
        else:
            # For team view, show batting team from filtered data
            if not local_df.empty:
                batting_teams_display = local_df['team_bat'].unique()
                if len(batting_teams_display) == 1:
                    title_name = batting_teams_display[0]  # Show actual team name
                    title_opponent = team_bowl
                else:
                    title_name = "All Players"
                    title_opponent = team_bowl
            else:
                title_name = "All Players"
                title_opponent = "All Teams"
        
        ax.set_title(
            f"{title_name} vs {title_opponent} | {competition} - Mat '{mat_num}', Inns: '{inns}'".upper(),
            fontsize=12, fontweight='bold', fontfamily='DejaVu Sans'
        )

    # Text Summary
    if show_summary:
        ax.text(220, -40, f"Total Runs: {innings_runs} ({balls_faced} balls)",
                fontsize=11, ha='center', fontweight='bold', color='darkgreen')
        ax.text(220, -25, f"Total 4s: {total_4s} | 6s: {total_6s}",
                fontsize=11, ha='center', color='darkgreen')

    if runs_count:
        ax.text(430, 140, f"{total_score} ({balls_faced} balls)",
                fontsize=11, ha='center', fontweight='bold')

    if show_fours_sixes:
        ax.text(430, 155, f"4s: {int(player_data['isFour'].sum())} | 6s: {int(player_data['isSix'].sum())}",
                fontsize=11, ha='center', color='darkgreen')

    if show_control:
        ax.text(430, 80, f"Control: {control_pct}%", fontsize=12, ha='center',
                color='purple', fontweight='bold')

    if show_prod_shot:
        ax.text(430, 250, f"Productive Shot:\n{most_prod_shot_text}", fontsize=11,
                ha='center', color='navy', fontweight='bold')

    if show_bowler:
        if bowler_name is None:
            bowler_name = 'All Bowlers'
        ax.text(430, 170, f"vs {bowler_name}", fontsize=11, ha='center',
                color='blue', fontweight='bold')

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    plt.close(fig)
    return fig
    # plt.show()
