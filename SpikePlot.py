# method 5
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import matplotlib.image as mpimg


# def test_match_spike_runs(df, player_name, inns, run_values=None, bowler_name=None, transparent=False):
def test_match_spike_runs(
    df, player_name,  inns,test_num = None, run_values=None, bowler_name=None, transparent=False,
    show_title=True, show_legend=True, show_summary=True,
    show_fours_sixes=True, show_control=True, show_prod_shot=True, runs_count=True, show_bowler=None
):
    score_colors = {
        # 0:  '#F70000',   
        0:  '#ff4d4d',   
        1:  '#8c8c8c',   
        2:  '#F3E139',   
        3:  '#D16FBC',   
        4:  '#0B9B67',
        5:  '#3964D0',   
        6:  '#7A41D8',   
    }
    # Filter by match, player, and innings
    # local_df = df[
    #     (df['batsmanName'] == player_name) &
    #     (df['TestNum']== test_num) if test_num is not None else True &
    #     (df['inningNumber'] == inns) 
    # ].copy()

    local_df = df[
        (df['batsmanName'] == player_name)
    ].copy()

    local_df = local_df[local_df['TestNum'] == test_num]

    local_df = local_df[local_df['inningNumber'] == inns]

    # === Total Innings Summary ===
    innings_valid_balls = local_df[local_df['wides'] == 0]
    innings_runs = innings_valid_balls['batsmanRuns'].sum()
    innings_balls = innings_valid_balls.shape[0]
    innings_4s = innings_valid_balls['isFour'].sum()
    innings_6s = innings_valid_balls['isSix'].sum()

    if bowler_name:
        local_df = local_df[local_df['bowlerName'] == bowler_name]

    # we have to calculate the team_bowl, by seeing the batsman_name and team_bats, the bowling team is the opposite of batting team
    team_bats = local_df['team_bat'].unique()[0]
    if team_bats == 'IND':
        team_bowl = 'ENG'
    elif team_bats == 'ENG':
        team_bowl = 'IND'
    
    # This keeps a copy of the full innings shot data (unfiltered)
    all_shots_data = local_df[
        ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()

    # Apply run filter
    if run_values is None:
        filtered_df = local_df.copy()
    else:
        filtered_df = local_df[local_df['batsmanRuns'].isin(run_values)]

    # Shots without wides (based on filtered data now)
    balls_faced_df = filtered_df[
        (filtered_df['wides'] == 0)
    ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

    # Handle run_values = None to include all run types

    # Filter valid shot points
    player_data = filtered_df[
        ~((filtered_df['wagonX'] == 0) & (filtered_df['wagonY'] == 0))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()

    # if player_data.empty:
    #     print(f"No data found for {player_name} in this match and innings {inns} for selected runs {run_values}")
    #     return
    if player_data.empty:
        player_data_sorted = pd.DataFrame()  # Set to empty for drawing logic below
    else:
        player_data_sorted = player_data.sort_values(by='batsmanRuns')
        player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')


    # === Additional Stats ===
    total_4s = player_data['isFour'].sum()
    total_6s = player_data['isSix'].sum()
    # control_pct = round(player_data['shotControl'].mean() * 100, 2)
    # control_pct = round((player_data['shotControl'] == 0).sum() / balls_faced_df.shape[0] * 100, 2)
    # control_pct = round((filtered_df[(filtered_df['wides'] == 0) & (filtered_df['shotControl'] == 0)].shape[0]) / balls_faced_df.shape[0] * 100, 2)
    # control_pct = round(player_data['shotControl'].mean() * 100, 2)
    # control_pct = round((player_data['shotControl'] == 0).sum() / balls_faced_df.shape[0] * 100, 2)
    # control_pct = round((filtered_df[(filtered_df['wides'] == 0) & (filtered_df['shotControl'] == 0)].shape[0]) / balls_faced_df.shape[0] * 100, 2)
    valid_balls = local_df[local_df['wides'] == 0]
    # controlled_balls = valid_balls[valid_balls['shotControl'] == 0]
    controlled_balls = valid_balls[valid_balls['shotControl'] ==1]
    control_pct = round(len(controlled_balls) / len(valid_balls) * 100, 2)
    # valid_balls = df[
    #     (df['batsmanName'] == player_name) &
    #     (df['inningNumber'] == inns) &
    #     (df['wides'] == 0)
    # ]

    # if bowler_name:
    #     valid_balls = valid_balls[valid_balls['bowlerName'] == bowler_name]

    # control_pct = round((valid_balls['shotControl'] == 1).sum() / valid_balls.shape[0] * 100, 2)

    total_runs_count = player_data['batsmanRuns'].sum() if runs_count else None
    # Most productive shot calculation
    if 'shotType' in all_shots_data.columns and not all_shots_data.empty:
    # if 'shotType' in player_data.columns and not player_data.empty:
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
        else:
            most_prod_shot_text = "No productive shot data"
    else:
        most_prod_shot_text = "No shot type data"

    # Color map
    # score_colors = {
    #     # 0: '#A9A9A9',
    #     0: '#FFFFFF',   # White (dot balls)
    #     1: '#00C853',
    #     2: '#2979FF',
    #     3: '#FF9100',
    #     5: '#C62828',  # Dark Red
    #     4: '#D50000',
    #     6: '#AA00FF'
    # }

    # player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')
    if not player_data.empty:
        player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')
    else:
        player_data['color'] = pd.Series(dtype='str')

    # Plot setup
    # fig, ax = plt.subplots(figsize=(7, 7))
    # ax.set_facecolor("white")
    fig, ax = plt.subplots(figsize=(7, 7), facecolor='none' if transparent else 'white')
    ax.set_facecolor('none' if transparent else 'white')
    center_x, center_y = 180, 164

     # Add background image
    if not transparent:
        bg_img = mpimg.imread("ground_high_res.png")  # Make sure this path is correct
        ax.imshow(bg_img, extent=[0, 360, 20, 360], aspect='auto', zorder=0)

    # Sort shots so 0s are drawn first, 6s last (so 6s are on top)
    player_data_sorted = player_data.sort_values(by='batsmanRuns')

    # Optional: define different line widths based on run value
    run_widths = {
        0: 1.5,
        1: 2.0,
        2: 2.0,
        3: 2.0,
        4: 3.0,
        5: 2.0,
        6: 3.0
    }

    # Draw the lines in sorted order
    # for _, row in player_data_sorted.iterrows():
    #     lw = run_widths.get(row['batsmanRuns'], 1.0)  # default width = 1.0 if not defined
    #     ax.plot(
    #         [center_x, row['wagonX']], [center_y, row['wagonY']],
    #         color=row['color'], linewidth=lw, alpha=0.8, zorder=1
    #     )
    if not player_data_sorted.empty:
        for _, row in player_data_sorted.iterrows():
            lw = run_widths.get(row['batsmanRuns'], 1.0)
            ax.plot(
                [center_x, row['wagonX']], [center_y, row['wagonY']],
                color=row['color'], linewidth=lw, alpha=0.8, zorder=1
            )
    else:
        ax.text(180, 410, "No shots for selected run(s)", ha='center', fontsize=12, color='red', fontweight='bold')
    # Draw lines
    # for _, row in player_data.iterrows():
    #     ax.plot([center_x, row['wagonX']], [center_y, row['wagonY']],
    #             color=row['color'], linewidth=1.0, alpha=0.8)

    # Boundary
    # boundary = plt.Circle((center_x, center_y), 175, color='black',
    #                       fill=False, linestyle='-', linewidth=1.2)
    # ax.add_artist(boundary)

    # Pitch
    # pitch = plt.Rectangle((center_x - 1.5, center_y), 3, 20.12,
    #                       edgecolor='black', facecolor='none', linewidth=1.5)
    # ax.add_artist(pitch)

    # plot the point (dot) at batter position which is at 180, 164, not rectangle only dot
    #batter position dot
    batter_dot = plt.Circle((center_x, center_y), radius=3, edgecolor='black', facecolor='green', linewidth=1, zorder=2)
    ax.add_artist(batter_dot)
    
    

    # Quadrants
    def get_quadrant(x, y):
        angle = np.arctan2(y - center_y, x - center_x)
        degree = (np.degrees(angle) + 360) % 360
        return int(degree // 45)

    # player_data['quadrant'] = player_data.apply(
    #     lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
    # )
    if not player_data.empty:
        player_data['quadrant'] = player_data.apply(
            lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
        )
    else:
        player_data['quadrant'] = pd.Series(dtype='int')  # Just to prevent downstream errors

    # Quadrant scores
    quadrant_totals = [0] * 8
    total_score = 0
    for q in range(8):
        q_score = player_data[player_data['quadrant'] == q]['batsmanRuns'].sum()
        quadrant_totals[q] = q_score
        total_score += q_score

    # Layout
    # ax.set_xlim(-20, 380)
    # ax.set_ylim(-20, 410)
    # ax.set_xticks([]), ax.set_yticks([])
    # ax.set_xticklabels([]), ax.set_yticklabels([])
    # ax.set_aspect('equal', adjustable='box')
    # ax.set_title(f"{player_name} Spike Graph Wheel Innings: {inns}", fontsize=12)

    # ax.text(180, 360, f"Total Runs: {total_score} ({balls_faced_df.shape[0]} balls)",
    #         fontsize=11, ha='center', fontweight='bold')
    # ax.text(180, 375, f"4s: {total_4s} | 6s: {total_6s}",
    #         fontsize=11, ha='center', color='darkgreen')
    # ax.text(180, 390, f"Control: {control_pct}%",
    #         fontsize=11, ha='center', color='purple')
    # ax.text(180, 405, f"Most Productive Shot: {most_prod_shot_text}",
    #         fontsize=11, ha='center', color='navy')
    ax.set_xlim(-20, 380)
    ax.set_ylim(-30, 420)
    ax.set_xticks([]), ax.set_yticks([])
    ax.set_xticklabels([]), ax.set_yticklabels([])
    ax.set_aspect('equal', adjustable='box')

    # ax.set_title(f"{player_name} Spike Graph Wheel Innings: {inns}", fontsize=12)
    if show_title:
        ax.set_title(f"{player_name} vs {team_bowl} - Test {test_num}, Inns: {inns}".upper(), fontsize=12, fontweight='bold',fontfamily='Segoe UI')

    innings_valid_balls = local_df[local_df['wides'] == 0]
    innings_runs = innings_valid_balls['batsmanRuns'].sum()
    innings_balls = innings_valid_balls.shape[0]
    innings_4s = innings_valid_balls['isFour'].sum()
    innings_6s = innings_valid_balls['isSix'].sum()

    if show_summary:
        ax.text(180, -20, f"Total Runs: {innings_runs} ({innings_balls} balls)",
                fontsize=11, ha='center', fontweight='bold', color='darkgreen')
        ax.text(180, -5, f"Total 4s: {innings_4s} | 6s: {innings_6s}",
                fontsize=11, ha='center', color='darkgreen')
    
    if runs_count:
        ax.text(180, 375, f"{total_score} ({balls_faced_df.shape[0]} balls)",
                fontsize=11, ha='center', fontweight='bold')
    if show_fours_sixes:
        ax.text(180, 388, f"4s: {total_4s} | 6s: {total_6s}",
                fontsize=11, ha='center', color='darkgreen')
    if show_bowler:
        if bowler_name is None:
            bowler_name = 'All'
        if bowler_name:
            ax.text(180, 405, f"vs {bowler_name}",
                    fontsize=11, ha='center', color='blue', fontweight='bold')

    if show_control:
        ax.text(10, 330, f"Control: {control_pct}%",
                fontsize=12, ha='center', color='purple', fontweight='bold')

    if show_prod_shot:
        ax.text(10, 390, f"Productive Shot:\n{most_prod_shot_text}",
                fontsize=11, ha='center', color='navy',fontweight='bold')

    # ax.text(180, 375, f"Total Runs: {total_score} ({balls_faced_df.shape[0]} balls)",
    #         fontsize=11, ha='center', fontweight='bold')
    # ax.text(180, 388, f"4s: {total_4s} | 6s: {total_6s}",
    #         fontsize=11, ha='center', color='darkgreen')
    # ax.text(180, 402, f"Control: {control_pct}%",
    #         fontsize=11, ha='center', color='purple')
    # ax.text(180, 415, f"Most Productive Shot: {most_prod_shot_text}",
    #         fontsize=11, ha='center', color='navy')

    ax.invert_yaxis()
    ax.set_axis_off()

    # Legend
    legend_elements = [
        mpatches.Patch(color=color, label=f'{score} run' + ('s' if score != 1 else ''))
        for score, color in score_colors.items() if run_values is None or score in run_values
    ]

    # ax.legend(handles=legend_elements, loc='upper right', fontsize=8)
    
    if show_legend:
        ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    plt.close(fig)
    return fig
    # plt.show()

# def test_match_spike_runs(df, player_name, inns, run_values=None, bowler_name=None, transparent=False):
#     # Filter by match, player, and innings
#     local_df = df[
#         (df['batsmanName'] == player_name) & (df['inningNumber'] == inns)
#     ].copy()

#     if bowler_name:
#         local_df = local_df[local_df['bowlerName'] == bowler_name]

#     if run_values is None:
#         filtered_df = local_df.copy()
#     else:
#         filtered_df = local_df[local_df['batsmanRuns'].isin(run_values)]

#     balls_faced_df = local_df[
#         (local_df['batsmanName'] == player_name) & (local_df['wides'] == 0)
#     ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()



#     # Handle run_values = None to include all run types

#     # Filter valid shot points
#     player_data = filtered_df[
#         ~((filtered_df['wagonX'] == 0) & (filtered_df['wagonY'] == 0))
#     ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()

#     if player_data.empty:
#         print(f"No data found for {player_name} in this match and innings {inns} for selected runs {run_values}")
#         return

#     # === Additional Stats ===
#     total_4s = player_data['isFour'].sum()
#     total_6s = player_data['isSix'].sum()
#     # control_pct = round(player_data['shotControl'].mean() * 100, 2)
#     # control_pct = round((player_data['shotControl'] == 0).sum() / balls_faced_df.shape[0] * 100, 2)
#     control_pct = round((local_df[(local_df['wides'] == 0) & (local_df['shotControl'] == 0)].shape[0]) / balls_faced_df.shape[0] * 100, 2)
#     # valid_balls = df[
#     #     (df['batsmanName'] == player_name) &
#     #     (df['inningNumber'] == inns) &
#     #     (df['wides'] == 0)
#     # ]

#     # if bowler_name:
#     #     valid_balls = valid_balls[valid_balls['bowlerName'] == bowler_name]

#     # control_pct = round((valid_balls['shotControl'] == 1).sum() / valid_balls.shape[0] * 100, 2)

#     # Most productive shot calculation
#     if 'shotType' in player_data.columns and not player_data.empty:
#         shot_summary = player_data.groupby('shotType').agg({
#             'batsmanRuns': 'sum',
#             'isFour': 'sum',
#             'isSix': 'sum'
#         }).sort_values(by='batsmanRuns', ascending=False)

#         if not shot_summary.empty:
#             top_shot = shot_summary.iloc[0]
#             top_shot_type = shot_summary.index[0]
#             most_prod_shot_text = (
#                 f"{top_shot_type}: {int(top_shot['batsmanRuns'])} runs, "
#                 f"{int(top_shot['isFour'])}x4s, {int(top_shot['isSix'])}x6s"
#             )
#         else:
#             most_prod_shot_text = "No productive shot data"
#     else:
#         most_prod_shot_text = "No shot type data"

#     # Color map
#     score_colors = {
#         0: '#A9A9A9',
#         1: '#00C853',
#         2: '#2979FF',
#         3: '#FF9100',
#         4: '#D50000',
#         6: '#AA00FF'
#     }
#     player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')

#     # Plot setup
#     # fig, ax = plt.subplots(figsize=(7, 7))
#     # ax.set_facecolor("white")
#     fig, ax = plt.subplots(figsize=(7, 7), facecolor='none' if transparent else 'white')
#     ax.set_facecolor('none' if transparent else 'white')
#     center_x, center_y = 180, 164

#     # Draw lines
#     for _, row in player_data.iterrows():
#         ax.plot([center_x, row['wagonX']], [center_y, row['wagonY']],
#                 color=row['color'], linewidth=1.0, alpha=0.8)

#     # Boundary
#     # boundary = plt.Circle((center_x, center_y), 175, color='black',
#     #                       fill=False, linestyle='--', linewidth=1.2)
#     # ax.add_artist(boundary)

#     # Pitch
#     pitch = plt.Rectangle((center_x - 1.5, center_y), 3, 20.12,
#                           edgecolor='black', facecolor='none', linewidth=1.5)
#     ax.add_artist(pitch)

#     # Quadrants
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

#     # Layout
#     ax.set_xlim(-20, 380)
#     ax.set_ylim(-20, 410)
#     ax.set_xticks([]), ax.set_yticks([])
#     ax.set_xticklabels([]), ax.set_yticklabels([])
#     ax.set_aspect('equal', adjustable='box')
#     ax.set_title(f"{player_name} Spike Graph Wheel Innings: {inns}", fontsize=12)

#     ax.text(180, 360, f"Total Runs: {total_score} ({balls_faced_df.shape[0]} balls)",
#             fontsize=11, ha='center', fontweight='bold')
#     ax.text(180, 375, f"4s: {total_4s} | 6s: {total_6s}",
#             fontsize=11, ha='center', color='darkgreen')
#     ax.text(180, 390, f"Shot Control: {control_pct}%",
#             fontsize=11, ha='center', color='purple')
#     ax.text(180, 405, f"Most Productive Shot: {most_prod_shot_text}",
#             fontsize=11, ha='center', color='navy')

#     ax.invert_yaxis()
#     ax.set_axis_off()

#     # Legend
#     legend_elements = [
#         mpatches.Patch(color=color, label=f'{score} run' + ('s' if score != 1 else ''))
#         for score, color in score_colors.items() if run_values is None or score in run_values
#     ]
#     ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

#     plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
#     plt.close(fig)
#     return fig
#     # plt.show()
