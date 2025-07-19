import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib.patches import Wedge  # add this at the top if not already
from io import BytesIO

### this is the working code only for testing
def test_match_wagon(
    df, player_name=None, inns=None, test_num=None, bowler_name=None, run_values=None,
    transparent=False, show_title=True, show_summary=True,
    show_fours_sixes=True, show_control=True, show_prod_shot=True,
    runs_count=True, show_bowler=True
):
    local_df = df.copy()

    if player_name:
        local_df = local_df[local_df['batsmanName'] == player_name]

    if test_num is not None:
        local_df = local_df[local_df['TestNum'] == test_num]

    if inns is not None:
        local_df = local_df[local_df['inningNumber'] == inns]

    if bowler_name:
        local_df = local_df[local_df['bowlerName'] == bowler_name]

    if run_values is not None:
        local_df = local_df[local_df['batsmanRuns'].isin(run_values)]

    if local_df.empty:
        print("No data found with the given filters.")
        return

    # Determine team_bat and team_bowl
    team_bats = local_df['team_bat'].mode()[0]
    team_bowl = df[df['team_bat'] != team_bats]['team_bat'].mode()[0]

    # Summary stats
    innings_valid_balls = local_df[local_df['wides'] == 0]
    innings_runs = innings_valid_balls['batsmanRuns'].sum()
    innings_balls = innings_valid_balls.shape[0]
    innings_4s = innings_valid_balls['isFour'].sum()
    innings_6s = innings_valid_balls['isSix'].sum()

    # Data for productive shot and control (unfiltered control data)
    control_df = df.copy()
    if player_name:
        control_df = control_df[control_df['batsmanName'] == player_name]
    if test_num is not None:
        control_df = control_df[control_df['TestNum'] == test_num]
    if inns is not None:
        control_df = control_df[control_df['inningNumber'] == inns]
    control_df = control_df[control_df['wides'] == 0]

    control_pct = 0.0
    if not control_df.empty:
        control_pct = round(
            (control_df[control_df['shotControl'] == 1].shape[0]) / control_df.shape[0] * 100, 2
        )

    all_shots_data = local_df[
        ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()

    most_prod_shot_text = "No shot data"
    if 'shotType' in all_shots_data.columns and not all_shots_data.empty:
        shot_summary = all_shots_data.groupby('shotType').agg({
            'batsmanRuns': 'sum',
            'isFour': 'sum',
            'isSix': 'sum'
        }).sort_values(by='batsmanRuns', ascending=False)

        if not shot_summary.empty:
            top_shot = shot_summary.iloc[0]
            top_shot_type = shot_summary.index[0]
            most_prod_shot_text = (
                f"{top_shot_type}: {int(top_shot['batsmanRuns'])} runs,\n"
                f"4s: {int(top_shot['isFour'])}, 6s: {int(top_shot['isSix'])}"
            )

    player_data = all_shots_data.copy()
    if player_data.empty:
        print("No shot data to plot.")
        return

    score_colors = {
        0: '#A9A9A9',
        1: '#00C853',
        2: '#2979FF',
        3: '#FF9100',
        4: '#D50000',
        6: '#AA00FF'
    }

    player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')

    # Plot
    fig, ax = plt.subplots(figsize=(7, 7), facecolor='none' if transparent else 'white')
    ax.set_facecolor('none' if transparent else 'white')
    center_x, center_y = 180, 164

    # Draw boundary and pitch
    boundary = plt.Circle((center_x, center_y), 180, color='black', fill=False, linewidth=1.2)
    ax.add_artist(boundary)
    batter_dot = plt.Circle((center_x, center_y), radius=3, edgecolor='black', facecolor='green', zorder=2)
    ax.add_artist(batter_dot)

    # Quadrants
    for angle in range(0, 360, 45):
        rad = np.deg2rad(angle)
        x_end = center_x + 180 * np.cos(rad)
        y_end = center_y + 180 * np.sin(rad)
        ax.plot([center_x, x_end], [center_y, y_end], color='black', linewidth=1.3)

    def get_quadrant(x, y):
        angle = np.arctan2(y - center_y, x - center_x)
        return int((np.degrees(angle) + 360) % 360 // 45)

    player_data['quadrant'] = player_data.apply(
        lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
    )

    quadrant_totals = [player_data[player_data['quadrant'] == q]['batsmanRuns'].sum() for q in range(8)]
    total_score = sum(quadrant_totals)
    top_quadrants = sorted(range(8), key=lambda i: quadrant_totals[i], reverse=True)[:2]
    rank_color = {top_quadrants[i]: 1.0 - i * 0.3 for i in range(len(top_quadrants))}
    cmap = cm.get_cmap('Blues')

    for i in range(8):
        theta1 = i * 45
        theta2 = theta1 + 45
        if i in rank_color:
            ax.add_patch(Wedge(center=(center_x, center_y), r=180, theta1=theta1, theta2=theta2,
                               color=cmap(rank_color[i]), alpha=0.3, zorder=0))
        mid_angle = np.deg2rad(theta1 + 22.5)
        label_x = center_x + 100 * np.cos(mid_angle)
        label_y = center_y + 100 * np.sin(mid_angle)
        ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=13,
                color='darkred' if i in top_quadrants else 'red',
                ha='center', va='center')

    ax.set_xlim(-20, 380)
    ax.set_ylim(-50, 420)
    ax.invert_yaxis()
    ax.set_aspect('equal', adjustable='box')
    ax.set_axis_off()

    if show_title:
        title = f"{player_name if player_name else 'All Players'} vs {team_bowl}"
        if test_num:
            title += f" - Test {test_num}"
        if inns:
            title += f", Inns {inns}"
        ax.set_title(title.upper(), fontsize=12, fontweight='bold', fontfamily='Segoe UI')

    if show_summary:
        ax.text(180, -40, f"Total Runs: {innings_runs} ({innings_balls} balls)",
                fontsize=11, ha='center', fontweight='bold', color='darkgreen')
        ax.text(180, -25, f"Total 4s: {innings_4s} | 6s: {innings_6s}",
                fontsize=11, ha='center', color='darkgreen')

    if runs_count:
        ax.text(180, 375, f"{total_score} ({player_data.shape[0]} balls)",
                fontsize=11, ha='center', fontweight='bold')

    if show_fours_sixes:
        ax.text(180, 388, f"4s: {int(player_data['isFour'].sum())} | 6s: {int(player_data['isSix'].sum())}",
                fontsize=11, ha='center', color='darkgreen')

    if show_control:
        ax.text(10, 330, f"Control: {control_pct}%", fontsize=12, ha='center',
                color='purple', fontweight='bold')

    if show_prod_shot:
        ax.text(10, 390, f"Productive Shot:\n{most_prod_shot_text}", fontsize=11,
                ha='center', color='navy', fontweight='bold')

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    plt.close(fig)
    return fig
    # plt.show()

#### this is the correct and all details previous method needs some changes only

# # def test_match_wagon(df, player_name, inns, bowler_name=None, run_values=None,transparent=False):
# def test_match_wagon(
#     df, player_name=None, inns=None, test_num=None, team_bat=None,
#     bowler_name=None, run_values=None, transparent=False,
#     show_title=True, show_summary=True,
#     show_fours_sixes=True, show_control=True,
#     show_prod_shot=True, runs_count=True, show_bowler=True, show_ground=True
# ):
    
#     # Filter by match, player, and innings
#     # local_df = df[
#     #     (df['batsmanName'] == player_name) &
#     #     (df['inningNumber'] == inns)
#     # ].copy()
#     # local_df = df[
#     #     (df['batsmanName'] == player_name)
#     # ].copy()

#     # local_df = local_df[local_df['TestNum'] == test_num]

#     # local_df = local_df[local_df['inningNumber'] == inns]
#     if player_name is not None:
#         local_df = df[
#             (df['batsmanName'] == player_name)
#         ].copy()
#     else:
#         local_df = df.copy()

#     if test_num is not None:
#         local_df = local_df[local_df['TestNum'] == test_num]

#     if inns is not None:
#         local_df = local_df[local_df['inningNumber'] == inns]
        
#     if team_bat is not None and team_bat != "All":
#         local_df = local_df[local_df['team_bat'] == team_bat]

#     # === Total Innings Summary ===
#     # innings_valid_balls = local_df[local_df['wides'] == 0]
#     # innings_runs = innings_valid_balls['batsmanRuns'].sum()
#     innings_valid_balls = local_df[local_df['wides'] == 0]

#     if player_name is None:
#         innings_runs = innings_valid_balls['teamRuns'].sum()
#     else:
#         innings_runs = innings_valid_balls['batsmanRuns'].sum()

#     innings_balls = innings_valid_balls.shape[0]

#     innings_4s = innings_valid_balls['isFour'].sum()
#     innings_6s = innings_valid_balls['isSix'].sum()
#     # Apply optional bowler filter
#     if bowler_name:
#         local_df = local_df[local_df['bowlerName'] == bowler_name]

#     # Set score = 0 for extras without modifying original df
#     # extras = ['wide', 'bye', 'leg bye']
#     # local_df.loc[local_df['outcome'].str.lower().isin(extras), 'teamRuns'] = 0

#     # playing_team = local_df['team_bat'].iloc[0] if not local_df.empty else "Unknown"
#     # opponent_team = local_df['team_bowl'].iloc[0] if not local_df.empty else "Unknown"

#     if run_values is not None:
#         local_df = local_df[local_df['batsmanRuns'].isin(run_values)]

#     # Filter valid shot points
#     # balls_faced_df = local_df[
#     #     (local_df['batsmanName'] == player_name) & (local_df['wides'] == 0)
#     # ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()
#     # we have to calculate the team_bowl, by seeing the batsman_name and team_bats, the bowling team is the opposite of batting team
#     # team_bats = local_df['team_bat'].unique()[0]
#     # if team_bats == 'IND':
#     #     team_bowl = 'ENG'
#     # elif team_bats == 'ENG':
#     #     team_bowl = 'IND'

#     batting_teams = local_df['team_bat'].dropna().unique()
#     all_teams = pd.concat([local_df['team_bat'], local_df['team_bowl']]).dropna().unique()

#     # Calculate bowling team based on filtered team_bat
#     if len(batting_teams) == 0:
#         team_bowl = "UNKNOWN"
#     else:
#         bowling_teams = [team for team in all_teams if team not in batting_teams]
#         if len(bowling_teams) == 1:
#             team_bowl = bowling_teams[0]
#         elif len(bowling_teams) > 1:
#             team_bowl = "/".join(sorted(set(bowling_teams)))
#         else:
#             team_bowl = "ALL TEAMS"

#     # Full innings (unfiltered) balls for shot control calc
#     # full_balls_df = df[
#     #     (df['batsmanName'] == player_name) &
#     #     (df['inningNumber'] == inns) &
#     #     (df['TestNum'] == test_num) &
#     #     (df['wides'] == 0)
#     # ]
#     if player_name is not None:
#         full_balls_df = df[
#             (df['batsmanName'] == player_name) &
#             (df['inningNumber'] == inns) &
#             (df['TestNum'] == test_num) &
#             (df['wides'] == 0)
#         ]
#     else:
#         full_balls_df = df[
#             (df['inningNumber'] == inns) &
#             (df['TestNum'] == test_num) &
#             (df['wides'] == 0)
#         ]


#     # Full innings valid shot data (unfiltered) for productive shot calc
#     # all_shots_data = df[
#     #     (df['batsmanName'] == player_name) &
#     #     (df['inningNumber'] == inns) &
#     #     (df['TestNum'] == test_num) &
#     #     ~((df['wagonX'] == 0) & (df['wagonY'] == 0))
#     # ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()

#     if player_name is not None:
#         all_shots_data = df[
#             (df['batsmanName'] == player_name) &
#             (df['inningNumber'] == inns) &
#             (df['TestNum'] == test_num) &
#             ~((df['wagonX'] == 0) & (df['wagonY'] == 0))
#         ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()
#     else:
#         all_shots_data = df[
#             (df['inningNumber'] == inns) &
#             (df['TestNum'] == test_num) &
#             ~((df['wagonX'] == 0) & (df['wagonY'] == 0))
#         ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()


#     # This is filtered shot data based on selected run values (for plotting only)
#     balls_faced_df = local_df[
#         (local_df['batsmanName'] == player_name) & (local_df['wides'] == 0)
#     ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()



#     player_data = local_df[
#         ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
#     ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()

#     if player_data.empty:
#         print(f"No data found for {player_name} in this match, and in innings {inns}")
#         return
#     # if player_data.empty:
#     #     player_data_sorted = pd.DataFrame()  # Set to empty for drawing logic below
#     # else:
#     #     player_data_sorted = player_data.sort_values(by='batsmanRuns')
#     #     player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')

#     # Color map
#     score_colors = {
#         0: '#A9A9A9',
#         1: '#00C853',
#         2: '#2979FF',
#         3: '#FF9100',
#         5: '#F3E139',
#         4: '#D50000',
#         6: '#AA00FF'
#     }
#     # player_data['color'] = player_data['score'].map(score_colors).fillna('black')
#     # player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')
#     if not player_data.empty:
#         player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')
#     else:
#         player_data['color'] = pd.Series(dtype='str')

#     # Additional stats
#     total_4s = int(player_data['isFour'].sum())
#     total_6s = int(player_data['isSix'].sum())
#     # control_pct = round((local_df[(local_df['wides'] == 0) & (local_df['shotControl'] == 0)].shape[0]) / balls_faced_df.shape[0] * 100, 2)
#     control_pct = round(
#         (full_balls_df[full_balls_df['shotControl'] == 1].shape[0]) / full_balls_df.shape[0] * 100, 2
#     )

#     # Most productive shot
#     if 'shotType' in all_shots_data.columns and not all_shots_data.empty:
#         shot_summary = all_shots_data.groupby('shotType').agg({
#     # if 'shotType' in player_data.columns and not player_data.empty:
#     #     shot_summary = player_data.groupby('shotType').agg({
#             'batsmanRuns': 'sum',
#             'isFour': 'sum',
#             'isSix': 'sum'
#         }).sort_values(by='batsmanRuns', ascending=False)

#         if not shot_summary.empty:
#             top_shot = shot_summary.iloc[0]
#             top_shot_type = shot_summary.index[0]
#             most_prod_shot_text = (
#                 f"{top_shot_type}: {int(top_shot['batsmanRuns'])} runs,\n"
#                 f"4s: {int(top_shot['isFour'])}, 6s: {int(top_shot['isSix'])}"
#             )
#         else:
#             most_prod_shot_text = "No productive shot data"
#     else:
#         most_prod_shot_text = "No shot type data"

#     # Plot setup
#     # fig, ax = plt.subplots(figsize=(7, 7))
#     # ax.set_facecolor("white")
#     fig, ax = plt.subplots(figsize=(7, 7), facecolor='none' if transparent else 'white')
#     ax.set_facecolor('none' if transparent else 'white')
#     center_x, center_y = 180, 164

#     # Boundary
#     boundary = plt.Circle((center_x, center_y), 180, color='black',
#                           fill=False, linestyle='-', linewidth=1.2)
#     ax.add_artist(boundary)

#     # Pitch
#     # pitch_length = 20.12
#     # pitch_width = 3
#     # pitch = plt.Rectangle((center_x - pitch_width / 2, center_y),
#     #                       pitch_width, pitch_length,
#     #                       edgecolor='black', facecolor='none', linewidth=1.5)
#     # ax.add_artist(pitch)
#     batter_dot = plt.Circle((center_x, center_y), radius=3, edgecolor='black', facecolor='green', linewidth=1, zorder=2)
#     ax.add_artist(batter_dot)

#     # Quadrants
#     for angle in range(0, 360, 45):
#         rad = np.deg2rad(angle)
#         x_end = center_x + 180 * np.cos(rad)
#         y_end = center_y + 180 * np.sin(rad)
#         ax.plot([center_x, x_end], [center_y, y_end], color='black', linestyle='-', linewidth=1.3)

#     def get_quadrant(x, y):
#         angle = np.arctan2(y - center_y, x - center_x)
#         degree = (np.degrees(angle) + 360) % 360
#         return int(degree // 45)

#     player_data['quadrant'] = player_data.apply(
#         lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
#     )

#     # Quadrant scores
#     quadrant_totals = [0] * 8
#     total_score = 0
#     for q in range(8):
#         q_score = player_data[player_data['quadrant'] == q]['batsmanRuns'].sum()
#         quadrant_totals[q] = q_score
#         total_score += q_score

#     # print("Quadrant Totals:", quadrant_totals)
#     # top_quadrants = sorted(range(8), key=lambda i: quadrant_totals[i], reverse=True)[:2]
#     # print("Top Quadrants:", top_quadrants)  # Debug

#     # Highlight top 2 quadrants using Wedge from matplotlib.patches
#     top_quadrants = sorted(range(8), key=lambda i: quadrant_totals[i], reverse=True)[:2]
#     # rank_color = {top_quadrants[0]: 1.0, top_quadrants[1]: 0.7}
#     rank_color = {top_quadrants[i]: 1.0 - i * 0.3 for i in range(len(top_quadrants))}
#     cmap = cm.get_cmap('Greys')  # or any other you prefer

#     for i in range(8):
#         theta1 = i * 45
#         theta2 = theta1 + 45

#         # if i in top_quadrants:
#         #     wedge = Wedge(center=(center_x, center_y),
#         #                 r=180,
#         #                 theta1=theta1,
#         #                 theta2=theta2,
#         #                 color=cmap(rank_color[i]),
#         #                 # color=cmap(i / 7),
#         #                 alpha=0.3,
#         #                 zorder=0)
#         #     ax.add_patch(wedge)
#         if i in rank_color:
#             wedge = Wedge(center=(center_x, center_y),
#                         r=180,
#                         theta1=theta1,
#                         theta2=theta2,
#                         color=cmap(rank_color[i]),
#                         # color=cmap(i / 7),
#                         alpha=0.3,
#                         zorder=0)
#             ax.add_patch(wedge)

#         # Label coordinates
#         mid_angle = np.deg2rad(theta1 + 22.5)
#         label_x = center_x + 100 * np.cos(mid_angle)
#         label_y = center_y + 100 * np.sin(mid_angle)
#         # label_color = 'darkred' if i in top_quadrants else 'black'
#         ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=13, color='black',
#                 ha='center', va='center')

#     # # Highlight top 2 quadrants
#     # top_quadrants = sorted(range(8), key=lambda i: quadrant_totals[i], reverse=True)[:2]
#     # # colors = 
#     # colors = cm.get_cmap('GnBu', 8)

#     # for i in range(8):
#     #     mid_angle = np.deg2rad(i * 45 + 22.5)
#     #     label_x = center_x + 100 * np.cos(mid_angle)
#     #     label_y = center_y + 100 * np.sin(mid_angle)

#     #     label_color = 'red'
#     #     if i in top_quadrants:
#     #         wedge = plt.Circle((center_x, center_y), 180, color=colors(i / 7), alpha=0.25, zorder=0)
#     #         theta1 = i * 45
#     #         theta2 = theta1 + 45
#     #         # ax.add_patch(plt.Wedge((center_x, center_y), 180, theta1, theta2, color=colors(i / 7), alpha=0.25))
#     #         ax.add_patch(Wedge((center_x, center_y), 180, theta1, theta2, color=colors(i / 7), alpha=0.25))
#     #         label_color = 'darkred'

#     #     ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=13, color=label_color,
#     #             ha='center', va='center')

#     # Layout
#     ax.set_xlim(-20, 380)
#     ax.set_ylim(-50, 420)
#     ax.set_xticks([])
#     ax.set_yticks([])
#     ax.set_xticklabels([])
#     ax.set_yticklabels([])
#     ax.set_aspect('equal', adjustable='box')

#     # ax.set_title(f"{player_name} Wagon Wheel Innings: {inns}", fontsize=12)
#     # if show_title:   
#     #     ax.set_title(f"{player_name} Wagon Wheel Innings: {inns}", fontsize=12)
#     if show_title:
#         ax.set_title(f"{player_name} vs {team_bowl} - Test {test_num}, Inns: {inns}".upper(), fontsize=12, fontweight='bold',fontfamily='Segoe UI')


#     if show_summary:
#         ax.text(180, -40, f"Total Runs: {innings_runs} ({innings_balls} balls)",
#                 fontsize=11, ha='center', fontweight='bold', color='darkgreen')
#         ax.text(180, -25, f"Total 4s: {innings_4s} | 6s: {innings_6s}",
#                 fontsize=11, ha='center', color='darkgreen')
#     # ax.text(180, 360, f"Total Runs: {total_score} ({balls_faced_df.shape[0]} balls)",
#     #         fontsize=11, ha='center', fontweight='bold', color='black')
#     # ax.text(180, 375, f"4s: {total_4s} | 6s: {total_6s} | Shot Control: {control_pct}%",
#     #         fontsize=11, ha='center', color='darkgreen')
#     # ax.text(180, 390, f"Most Productive Shot: {most_prod_shot_text}",
#     #         fontsize=11, ha='center', color='navy')
#     if runs_count:
#         ax.text(180, 375, f"{total_score} ({balls_faced_df.shape[0]} balls)",
#                 fontsize=11, ha='center', fontweight='bold')
#     if show_fours_sixes:  
#         ax.text(180, 388, f"4s: {total_4s} | 6s: {total_6s}",
#                 fontsize=11, ha='center', color='darkgreen')
        
#     if show_bowler:
#         if bowler_name is None:
#             bowler_name = 'All Bowlers'
#         if bowler_name:
#             ax.text(180, 405, f"vs {bowler_name}",
#                     fontsize=11, ha='center', color='blue', fontweight='bold')
#     if show_control:
#         ax.text(10, 330, f"Control: {control_pct}%",
#                 fontsize=12, ha='center', color='purple', fontweight='bold')
        
#     if show_prod_shot:
#         ax.text(10, 390, f"Productive Shot:\n{most_prod_shot_text}",
#                 fontsize=11, ha='center', color='navy',fontweight='bold')

#     ax.invert_yaxis()
#     ax.set_axis_off()

#     # Legend
#     # legend_elements = [
#     #     mpatches.Patch(color=color, label=f'{score} run' + ('s' if score != 1 else ''))
#     #     for score, color in score_colors.items()
#     # ]
#     # ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

#     plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
#     plt.close(fig)
#     return fig
#     # plt.show()
