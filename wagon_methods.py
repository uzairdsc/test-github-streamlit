import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
# method 1:
# def test_match_spike(df, player_name, inns):
#     # Filter by match, player, and innings
#     local_df = df[
#         (df['batsmanName'] == player_name) &
#         (df['inningNumber'] == inns)  
#     ].copy()

#     balls_faced_df = local_df[
#         (local_df['batsmanName'] == player_name) &
#         (local_df['wides'] == 0)
#     ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()
#     # Set score = 0 for extras without modifying original df
#     # extras = ['wide', 'bye', 'leg bye']
#     # local_df.loc[local_df['outcome'].str.lower().isin(extras), 'teamRuns'] = 0

#     # playing_team = local_df['team_bat'].iloc[0] if not local_df.empty else "Unknown"
#     # opponent_team = local_df['team_bowl'].iloc[0] if not local_df.empty else "Unknown"
#     # Filter valid shot points
#     player_data = local_df[
#         ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
#     ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

#     if player_data.empty:
#         print(f"No data found for {player_name} in this match,and in innings {inns}")
#         return

#     # Color map
#     score_colors = {
#         0: '#A9A9A9',
#         1: '#00C853',
#         2: '#2979FF',
#         3: '#FF9100',
#         4: '#D50000',
#         6: '#AA00FF'
#     }
#     # player_data['color'] = player_data['score'].map(score_colors).fillna('black')
#     player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')

#     # Plot setup
#     fig, ax = plt.subplots(figsize=(7, 7))
#     ax.set_facecolor("white")
#     center_x, center_y = 180, 164

#     # ax.scatter(player_data['wagonX'], player_data['wagonY'],
#     #            c=player_data['color'], s=40, edgecolor='black', linewidth=0.6)

#     # Draw lines
#     for _, row in player_data.iterrows():
#         ax.plot([center_x, row['wagonX']], [center_y, row['wagonY']],
#                 color=row['color'], linewidth=1.0, alpha=0.8)

#     # Boundary
#     boundary = plt.Circle((center_x, center_y), 180, color='black',
#                           fill=False, linestyle='--', linewidth=1.2)
#     # fill the boundary with a light color
#     # boundary.set_facecolor("#00ADC8")
#     ax.add_artist(boundary)

#     # Pitch
#     pitch_length = 20.12
#     pitch_width = 3
#     pitch = plt.Rectangle((center_x - pitch_width / 2, center_y),
#                           pitch_width, pitch_length,
#                           edgecolor='black', facecolor='none', linewidth=1.5)
#     ax.add_artist(pitch)

#     # Quadrants
#     for angle in range(0, 360, 45):
#         rad = np.deg2rad(angle)
#         x_end = center_x + 180 * np.cos(rad)
#         y_end = center_y + 180 * np.sin(rad)
#         # ax.plot([center_x, x_end], [center_y, y_end], color='black', linestyle='--', linewidth=1.3)

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
#         # q_score = player_data[player_data['quadrant'] == q]['score'].sum()
#         q_score = player_data[player_data['quadrant'] == q]['batsmanRuns'].sum()
#         quadrant_totals[q] = q_score
#         total_score += q_score

#     for i in range(8):
#         mid_angle = np.deg2rad(i * 45 + 22.5)
#         label_x = center_x + 100 * np.cos(mid_angle)
#         label_y = center_y + 100 * np.sin(mid_angle)
#         # ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=11, ha='center', va='center')

#     # Layout
#     ax.set_xlim(-20, 380)
#     ax.set_ylim(-20, 380)
#     ax.set_xticks([])
#     ax.set_yticks([])
#     ax.set_xticklabels([])
#     ax.set_yticklabels([])    
#     ax.set_aspect('equal', adjustable='box')


#     ax.set_title(f"{player_name} Spike Graph Wheel Innings: {inns}", fontsize=12) 
#     #  Add total score annotation to bottom center
#     ax.text(180, 370, f"Total Runs Scored by {player_name}  in Inns: {inns} : {total_score} ({balls_faced_df.shape[0]})",
#         fontsize=12, ha='center', va='center', fontweight='bold', color='black')

#     ax.invert_yaxis()
#     ax.set_axis_off()

#     # Legend
#     legend_elements = [
#         mpatches.Patch(color=color, label=f'{score} run' + ('s' if score != 1 else ''))
#         for score, color in score_colors.items()
#     ]
#     ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

#     plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
#     # plt.show()
#     return fig
def test_match_spike(df, player_name, inns, bowler_name=None):
    # Filter by match, player, innings (and bowler if selected)
    local_df = df[
        (df['batsmanName'] == player_name) &
        (df['inningNumber'] == inns)
    ].copy()

    if bowler_name:
        local_df = local_df[local_df['bowlerName'] == bowler_name]

    balls_faced_df = local_df[
        (local_df['batsmanName'] == player_name) &
        (local_df['wides'] == 0)
    ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

    # Filter valid shot points
    player_data = local_df[
        ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

    if player_data.empty:
        print(f"No data found for {player_name} in this match and innings {inns}")
        return

    # Color map
    score_colors = {
        0: '#A9A9A9',
        1: '#00C853',
        2: '#2979FF',
        3: '#FF9100',
        4: '#D50000',
        6: '#AA00FF'
    }

    player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')

    # Plot setup
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor("white")
    center_x, center_y = 180, 164

    # Draw lines
    for _, row in player_data.iterrows():
        ax.plot([center_x, row['wagonX']], [center_y, row['wagonY']],
                color=row['color'], linewidth=1.0, alpha=0.8)

    # Boundary & pitch
    boundary = plt.Circle((center_x, center_y), 180, color='black',
                          fill=False, linestyle='--', linewidth=1.2)
    ax.add_artist(boundary)

    pitch = plt.Rectangle((center_x - 1.5, center_y), 3, 20.12,
                          edgecolor='black', facecolor='none', linewidth=1.5)
    ax.add_artist(pitch)

    # Quadrants
    def get_quadrant(x, y):
        angle = np.arctan2(y - center_y, x - center_x)
        degree = (np.degrees(angle) + 360) % 360
        return int(degree // 45)

    player_data['quadrant'] = player_data.apply(
        lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
    )

    # Quadrant scores
    quadrant_totals = [0] * 8
    total_score = 0
    for q in range(8):
        q_score = player_data[player_data['quadrant'] == q]['batsmanRuns'].sum()
        quadrant_totals[q] = q_score
        total_score += q_score

    # Plot labels
    for i in range(8):
        mid_angle = np.deg2rad(i * 45 + 22.5)
        label_x = center_x + 100 * np.cos(mid_angle)
        label_y = center_y + 100 * np.sin(mid_angle)

    ax.set_xlim(-20, 380)
    ax.set_ylim(-20, 380)
    ax.set_xticks([]), ax.set_yticks([])
    ax.set_xticklabels([]), ax.set_yticklabels([])
    ax.set_aspect('equal', adjustable='box')

    ax.set_title(f"{player_name} Spike Graph Wheel Innings: {inns}", fontsize=12)
    ax.text(180, 370, f"Total Runs by {player_name} in Inns: {inns} : {total_score} ({balls_faced_df.shape[0]} balls)",
            fontsize=12, ha='center', va='center', fontweight='bold', color='black')

    ax.invert_yaxis()
    ax.set_axis_off()

    # Legend
    legend_elements = [
        mpatches.Patch(color=color, label=f'{score} run' + ('s' if score != 1 else ''))
        for score, color in score_colors.items()
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    plt.close(fig)
    return fig

# method 5
def test_match_spike_runs(df, player_name, inns, run_values, bowler_name=None):
    # Filter by match, player, and innings
    local_df = df[
        (df['batsmanName'] == player_name) &
        (df['inningNumber'] == inns)
    ].copy()

    if bowler_name:
        local_df = local_df[local_df['bowlerName'] == bowler_name]

    balls_faced_df = local_df[
        (local_df['batsmanName'] == player_name) &
        (local_df['wides'] == 0)
    ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

    # Filter valid shot points and run values
    player_data = local_df[
        (~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))) &
        (local_df['batsmanRuns'].isin(run_values))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

    if player_data.empty:
        print(f"No data found for {player_name} in this match and innings {inns} for selected runs {run_values}")
        return

    # Color map
    score_colors = {
        0: '#A9A9A9',
        1: '#00C853',
        2: '#2979FF',
        3: '#FF9100',
        4: '#D50000',
        6: '#AA00FF'
    }
    player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')

    # Plot setup
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor("white")
    center_x, center_y = 180, 164

    # Draw lines
    for _, row in player_data.iterrows():
        ax.plot([center_x, row['wagonX']], [center_y, row['wagonY']],
                color=row['color'], linewidth=1.0, alpha=0.8)

    # Boundary
    boundary = plt.Circle((center_x, center_y), 180, color='black',
                          fill=False, linestyle='--', linewidth=1.2)
    ax.add_artist(boundary)

    # Pitch
    pitch = plt.Rectangle((center_x - 1.5, center_y), 3, 20.12,
                          edgecolor='black', facecolor='none', linewidth=1.5)
    ax.add_artist(pitch)

    # Quadrants
    def get_quadrant(x, y):
        angle = np.arctan2(y - center_y, x - center_x)
        degree = (np.degrees(angle) + 360) % 360
        return int(degree // 45)

    player_data['quadrant'] = player_data.apply(
        lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
    )

    # Quadrant scores
    quadrant_totals = [0] * 8
    total_score = 0
    for q in range(8):
        q_score = player_data[player_data['quadrant'] == q]['batsmanRuns'].sum()
        quadrant_totals[q] = q_score
        total_score += q_score

    # Layout
    ax.set_xlim(-20, 380)
    ax.set_ylim(-20, 380)
    ax.set_xticks([]), ax.set_yticks([])
    ax.set_xticklabels([]), ax.set_yticklabels([])
    ax.set_aspect('equal', adjustable='box')
    ax.set_title(f"{player_name} Spike Graph Wheel Innings: {inns}", fontsize=12)

    ax.text(180, 370, f"Total Runs in Inns: {inns} : {total_score} ({balls_faced_df.shape[0]} balls)",
            fontsize=12, ha='center', va='center', fontweight='bold', color='black')

    ax.invert_yaxis()
    ax.set_axis_off()

    # Legend
    legend_elements = [
        mpatches.Patch(color=color, label=f'{score} run' + ('s' if score != 1 else ''))
        for score, color in score_colors.items() if score in run_values
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    plt.close(fig)
    return fig
    # plt.show()


# method 2:
# def test_match_wagon_colored(df, player_name, inns):
#     # Filter by player and innings
#     local_df = df[
#         (df['batsmanName'] == player_name) &
#         (df['inningNumber'] == inns)
#     ].copy()

#     balls_faced_df = local_df[
#         (local_df['batsmanName'] == player_name) &
#         (local_df['wides'] == 0)
#     ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

#     # Filter valid shot points
#     player_data = local_df[
#         ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
#     ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

#     if player_data.empty:
#         print(f"No data found for {player_name} in this match and innings {inns}")
#         return

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
#     fig, ax = plt.subplots(figsize=(7, 7))
#     ax.set_facecolor("white")
#     center_x, center_y = 180, 164
#     boundary_radius = 180

#     # Define quadrant based on angle
#     def get_quadrant(x, y):
#         angle = np.arctan2(y - center_y, x - center_x)
#         degree = (np.degrees(angle) + 360) % 360
#         return int(degree // 45)

#     player_data['quadrant'] = player_data.apply(
#         lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
#     )

#     # Compute quadrant scores
#     quadrant_totals = [0] * 8
#     total_score = 0
#     for q in range(8):
#         q_score = player_data[player_data['quadrant'] == q]['batsmanRuns'].sum()
#         quadrant_totals[q] = q_score
#         total_score += q_score

#     max_score = max(quadrant_totals) if total_score > 0 else 1

#     # Fill quadrants with gray scale
#     for i in range(8):
#         angle_start = i * 45
#         angle_end = (i + 1) * 45
#         fraction = quadrant_totals[i] / max_score
#         shade = 1 - (fraction * 0.6)  # Darker if higher score
#         wedge = mpatches.Wedge(
#             center=(center_x, center_y),
#             r=boundary_radius,
#             theta1=angle_start,
#             theta2=angle_end,
#             facecolor=(shade, shade, shade),
#             edgecolor='none'
#         )
#         ax.add_patch(wedge)

#     # # Draw shot lines
#     # for _, row in player_data.iterrows():
#     #     ax.plot([center_x, row['wagonX']], [center_y, row['wagonY']],
#     #             color=row['color'], linewidth=1.0, alpha=0.8)

#     # Boundary
#     # ax.add_artist(plt.Circle((center_x, center_y), 180, color='black',
#     #                          fill=False, linestyle='--', linewidth=1.2))

#     # Pitch
#     # pitch = plt.Rectangle((center_x - 1.5, center_y), 3, 20.12,
#     #                       edgecolor='black', facecolor='none', linewidth=1.5)
#     # ax.add_artist(pitch)

#     # Quadrant lines
#     for angle in range(0, 360, 45):
#         rad = np.deg2rad(angle)
#         x_end = center_x + 180 * np.cos(rad)
#         y_end = center_y + 180 * np.sin(rad)
#         ax.plot([center_x, x_end], [center_y, y_end],
#                 color='black', linestyle='--', linewidth=1)

#     # Quadrant score labels
#     for i in range(8):
#         mid_angle = np.deg2rad(i * 45 + 22.5)
#         label_x = center_x + 100 * np.cos(mid_angle)
#         label_y = center_y + 100 * np.sin(mid_angle)
#         ax.text(label_x, label_y, f"{quadrant_totals[i]} runs",
#                 fontsize=13, color='black', ha='center', va='center')

#     # Title and layout
#     ax.set_xlim(-20, 380)
#     ax.set_ylim(-20, 380)
#     ax.set_aspect('equal', adjustable='box')
#     ax.set_title(f"{player_name} Wagon Wheel - Innings {inns}", fontsize=12)
#     ax.text(180, 370, f"Total Runs Scored by {player_name} in Innings {inns}: {total_score} ({balls_faced_df.shape[0]})",
#             fontsize=12, ha='center', va='center', fontweight='bold', color='black')

#     ax.set_xticks([]), ax.set_yticks([])
#     ax.set_xticklabels([]), ax.set_yticklabels([])
#     ax.invert_yaxis()
#     ax.set_axis_off()

#     plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
#     # plt.show()
#     return fig

def test_match_wagon_colored(df, player_name, inns, bowler_name=None, run_values=None):
    # Filter by player and innings
    local_df = df[
        (df['batsmanName'] == player_name) &
        (df['inningNumber'] == inns)
    ].copy()

    if bowler_name:
        local_df = local_df[local_df['bowlerName'] == bowler_name]

    if run_values is not None and len(run_values) > 0:
        local_df = local_df[local_df['batsmanRuns'].isin(run_values)]

    balls_faced_df = local_df[
        (local_df['batsmanName'] == player_name) & (local_df['wides'] == 0)
    ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

    player_data = local_df[
        ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

    if player_data.empty:
        if bowler_name:
            print(f"No data found for {player_name} vs {bowler_name} in innings {inns}")
        else:
            print(f"No data found for {player_name} in innings {inns}")
        return

    # Color map
    score_colors = {
        0: '#A9A9A9',
        1: '#00C853',
        2: '#2979FF',
        3: '#FF9100',
        4: '#D50000',
        6: '#AA00FF'
    }
    player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')

    # Plot setup
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor("white")
    center_x, center_y = 180, 164
    boundary_radius = 180

    def get_quadrant(x, y):
        angle = np.arctan2(y - center_y, x - center_x)
        degree = (np.degrees(angle) + 360) % 360
        return int(degree // 45)

    player_data['quadrant'] = player_data.apply(
        lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
    )

    quadrant_totals = [0] * 8
    total_score = 0
    for q in range(8):
        q_score = player_data[player_data['quadrant'] == q]['batsmanRuns'].sum()
        quadrant_totals[q] = q_score
        total_score += q_score

    max_score = max(quadrant_totals) if total_score > 0 else 1

    for i in range(8):
        angle_start = i * 45
        angle_end = (i + 1) * 45
        fraction = quadrant_totals[i] / max_score
        shade = 1 - (fraction * 0.6)
        wedge = mpatches.Wedge(
            center=(center_x, center_y),
            r=boundary_radius,
            theta1=angle_start,
            theta2=angle_end,
            facecolor=(shade, shade, shade),
            edgecolor='none'
        )
        ax.add_patch(wedge)

    for angle in range(0, 360, 45):
        rad = np.deg2rad(angle)
        x_end = center_x + 180 * np.cos(rad)
        y_end = center_y + 180 * np.sin(rad)
        ax.plot([center_x, x_end], [center_y, y_end], color='black', linestyle='--', linewidth=1)

    for i in range(8):
        mid_angle = np.deg2rad(i * 45 + 22.5)
        label_x = center_x + 100 * np.cos(mid_angle)
        label_y = center_y + 100 * np.sin(mid_angle)
        ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=13, color='black', ha='center', va='center')

    # Title & annotation
    title_text = f"{player_name} Wagon Wheel - Innings {inns}"
    if bowler_name:
        title_text += f" vs {bowler_name}"
    ax.set_title(title_text, fontsize=12)

    bottom_text = f"Total Runs Scored by {player_name} in Innings {inns}"
    if bowler_name:
        bottom_text += f" vs {bowler_name}"
    bottom_text += f": {total_score} ({balls_faced_df.shape[0]})"

    ax.text(180, 370, bottom_text, fontsize=12, ha='center', va='center', fontweight='bold', color='black')

    ax.set_xlim(-20, 380)
    ax.set_ylim(-20, 380)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xticks([]), ax.set_yticks([])
    ax.set_xticklabels([]), ax.set_yticklabels([])
    ax.invert_yaxis()
    ax.set_axis_off()

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    plt.close(fig)
    return fig
    # plt.show()



# method 3:
def shot_type_wagon(df, player_name, inns,bowler_name=None):
    # Filter by match, player, and innings
    local_df = df[
        (df['batsmanName'] == player_name) &
        (df['inningNumber'] == inns)  
    ].copy()

    # Apply bowler filter if provided
    if bowler_name:
        local_df = local_df[local_df['bowlerName'] == bowler_name]

    balls_faced_df = local_df[
        (local_df['batsmanName'] == player_name) &
        (local_df['wides'] == 0)
    ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()
    # Set score = 0 for extras without modifying original df
    # extras = ['wide', 'bye', 'leg bye']
    # local_df.loc[local_df['outcome'].str.lower().isin(extras), 'teamRuns'] = 0

    # playing_team = local_df['team_bat'].iloc[0] if not local_df.empty else "Unknown"
    # opponent_team = local_df['team_bowl'].iloc[0] if not local_df.empty else "Unknown"
    # Filter valid shot points
    player_data = local_df[
        ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'shotType']].dropna()

    # if player_data.empty:
    #     print(f"No data found for {player_name} in this match,and in innings {inns}")
    #     return
    
    if player_data.empty:
        if bowler_name:
            print(f"No data found for {player_name} vs {bowler_name} in innings {inns}")
        else:
            print(f"No data found for {player_name} in innings {inns}")
        return

    # Color map (shotType)
    unique_shots = player_data['shotType'].unique()
    color_palette = plt.cm.get_cmap('tab20', len(unique_shots))  # up to 20 distinct colors
    shot_colors = {shot: color_palette(i) for i, shot in enumerate(unique_shots)}

    # player_data['color'] = player_data['score'].map(score_colors).fillna('black')
    player_data['color'] = player_data['shotType'].map(shot_colors).fillna('black')

    # Plot setup
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor("white")
    center_x, center_y = 180, 164

    # ax.scatter(player_data['wagonX'], player_data['wagonY'],
    #            c=player_data['color'], s=40, edgecolor='black', linewidth=0.6)

    # Draw lines
    for _, row in player_data.iterrows():
        ax.plot([center_x, row['wagonX']], [center_y, row['wagonY']],
                color=row['color'], linewidth=1.0, alpha=0.8)

    # Boundary
    boundary = plt.Circle((center_x, center_y), 180, color='black',
                          fill=False, linestyle='--', linewidth=1.2)
    # fill the boundary with a light color
    # boundary.set_facecolor("#00ADC8")
    ax.add_artist(boundary)

    # Pitch
    # pitch_length = 20.12
    # pitch_width = 3
    # pitch = plt.Rectangle((center_x - pitch_width / 2, center_y),
    #                       pitch_width, pitch_length,
    #                       edgecolor='black', facecolor='none', linewidth=1.5)
    # ax.add_artist(pitch)

    # Quadrants
    for angle in range(0, 360, 45):
        rad = np.deg2rad(angle)
        x_end = center_x + 180 * np.cos(rad)
        y_end = center_y + 180 * np.sin(rad)
        ax.plot([center_x, x_end], [center_y, y_end], color='black', linestyle='--', linewidth=1)

    def get_quadrant(x, y):
        angle = np.arctan2(y - center_y, x - center_x)
        degree = (np.degrees(angle) + 360) % 360
        return int(degree // 45)

    player_data['quadrant'] = player_data.apply(
        lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
    )

    # Quadrant scores
    quadrant_totals = [0] * 8
    total_score = 0
    for q in range(8):
        q_score = player_data[player_data['quadrant'] == q]['teamRuns'].sum()
        q_score = player_data[player_data['quadrant'] == q]['batsmanRuns'].sum()
        quadrant_totals[q] = q_score
        total_score += q_score

    for i in range(8):
        mid_angle = np.deg2rad(i * 45 + 22.5)
        label_x = center_x + 100 * np.cos(mid_angle)
        label_y = center_y + 100 * np.sin(mid_angle)
        # ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=11, ha='center', va='center')

    # Layout
    ax.set_xlim(-20, 380)
    ax.set_ylim(-20, 390)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_aspect('equal', adjustable='box')

    bowler_text = f" vs {bowler_name}" if bowler_name else ""
    ax.set_title(f"{player_name} Spike Graph Wheel Innings: {inns} - Shot Type", fontsize=12) 

    #  Add total score annotation to bottom center
    
        # ---- Shot type stats: Balls Faced and Runs ----
    # Only legal balls (no wides) for balls faced
    shot_stats_df = local_df[local_df['wides'] == 0].groupby('shotType').agg(
        BF=('shotType', 'count'),
        Runs=('batsmanRuns', 'sum')
    ).reset_index()

    # Format string like "FLICK (12, 9)" and join with |
    shot_stats_text = " | ".join([
        f"{row['shotType']} ( {row['Runs']},{row['BF']})"
        for _, row in shot_stats_df.iterrows()
    ])

    # Display just above the bottom text
    ax.text(180, 360, shot_stats_text,
            fontsize=9, ha='center', va='center', color='black', wrap=True)


    ax.text(180, 380, f"Total Runs Scored by {player_name}  in Inns: {inns} vs {bowler_name}: {total_score} ({balls_faced_df.shape[0]})",
        fontsize=12, ha='center', va='center', fontweight='bold', color='black')

    ax.invert_yaxis()
    ax.set_axis_off()

    # Legend for shot types
    legend_elements = [
        mpatches.Patch(color=shot_colors[shot], label=shot) for shot in shot_colors
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    # plt.show()
    return fig

# method 4:
def pitch_type_wagon(df, player_name, inns,bowler_name=None):
    # Filter by match, player, and innings
    local_df = df[
        (df['batsmanName'] == player_name) &
        (df['inningNumber'] == inns)  
    ].copy()

    # Apply bowler filter if provided
    if bowler_name:
        local_df = local_df[local_df['bowlerName'] == bowler_name]

    balls_faced_df = local_df[
        (local_df['batsmanName'] == player_name) &
        (local_df['wides'] == 0)
    ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()
    # Set score = 0 for extras without modifying original df
    # extras = ['wide', 'bye', 'leg bye']
    # local_df.loc[local_df['outcome'].str.lower().isin(extras), 'teamRuns'] = 0

    # playing_team = local_df['team_bat'].iloc[0] if not local_df.empty else "Unknown"
    # opponent_team = local_df['team_bowl'].iloc[0] if not local_df.empty else "Unknown"
    # Filter valid shot points
    player_data = local_df[
        ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'pitchLength']].dropna()

    # if player_data.empty:
    #     print(f"No data found for {player_name} in this match,and in innings {inns}")
    #     return
    
    if player_data.empty:
        if bowler_name:
            print(f"No data found for {player_name} vs {bowler_name} in innings {inns}")
        else:
            print(f"No data found for {player_name} in innings {inns}")
        return

    # Color map (shotType)
    pitch_length = player_data['pitchLength'].unique()
    color_palette = plt.cm.get_cmap('tab20', len(pitch_length))  # up to 20 distinct colors
    shot_colors = {shot: color_palette(i) for i, shot in enumerate(pitch_length)}

    # player_data['color'] = player_data['score'].map(score_colors).fillna('black')
    player_data['color'] = player_data['pitchLength'].map(shot_colors).fillna('black')

    # Plot setup
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor("white")
    center_x, center_y = 180, 164

    # ax.scatter(player_data['wagonX'], player_data['wagonY'],
    #            c=player_data['color'], s=40, edgecolor='black', linewidth=0.6)

    # Draw lines
    for _, row in player_data.iterrows():
        ax.plot([center_x, row['wagonX']], [center_y, row['wagonY']],
                color=row['color'], linewidth=1.0, alpha=0.8)

    # Boundary
    boundary = plt.Circle((center_x, center_y), 180, color='black',
                          fill=False, linestyle='--', linewidth=1.2)
    # fill the boundary with a light color
    # boundary.set_facecolor("#00ADC8")
    ax.add_artist(boundary)

    # Pitch
    # pitch_length = 20.12
    # pitch_width = 3
    # pitch = plt.Rectangle((center_x - pitch_width / 2, center_y),
    #                       pitch_width, pitch_length,
    #                       edgecolor='black', facecolor='none', linewidth=1.5)
    # ax.add_artist(pitch)

    # Quadrants
    for angle in range(0, 360, 45):
        rad = np.deg2rad(angle)
        x_end = center_x + 180 * np.cos(rad)
        y_end = center_y + 180 * np.sin(rad)
        ax.plot([center_x, x_end], [center_y, y_end], color='black', linestyle='--', linewidth=1)

    def get_quadrant(x, y):
        angle = np.arctan2(y - center_y, x - center_x)
        degree = (np.degrees(angle) + 360) % 360
        return int(degree // 45)

    player_data['quadrant'] = player_data.apply(
        lambda row: get_quadrant(row['wagonX'], row['wagonY']), axis=1
    )

    # Quadrant scores
    quadrant_totals = [0] * 8
    total_score = 0
    for q in range(8):
        q_score = player_data[player_data['quadrant'] == q]['teamRuns'].sum()
        q_score = player_data[player_data['quadrant'] == q]['batsmanRuns'].sum()
        quadrant_totals[q] = q_score
        total_score += q_score

    for i in range(8):
        mid_angle = np.deg2rad(i * 45 + 22.5)
        label_x = center_x + 100 * np.cos(mid_angle)
        label_y = center_y + 100 * np.sin(mid_angle)
        # ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=11, ha='center', va='center')

    # Layout
    ax.set_xlim(-20, 380)
    ax.set_ylim(-20, 390)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_aspect('equal', adjustable='box')

    bowler_text = f" vs {bowler_name}" if bowler_name else ""
    ax.set_title(f"{player_name} Spike Graph Wheel Innings: {inns} - Pitch Length", fontsize=12) 

    #  Add total score annotation to bottom center

        # ---- Pitch Length stats: Balls Faced and Runs ----
    pitch_stats_df = local_df[local_df['wides'] == 0].groupby('pitchLength').agg(
        BF=('pitchLength', 'count'),
        Runs=('batsmanRuns', 'sum')
    ).reset_index()

    # Format like "SHORT (12, 14) | FULL (9, 22)"
    pitch_stats_text = " | ".join([
        f"{row['pitchLength']} ({row['Runs']},{row['BF']})"
        for _, row in pitch_stats_df.iterrows()
    ])

    # Display just above the bottom score text
    ax.text(180, 360, pitch_stats_text,
            fontsize=9, ha='center', va='center', color='black', wrap=True)


    ax.text(180, 380, f"Total Runs Scored by {player_name}  in Inns: {inns} vs {bowler_name}: {total_score} ({balls_faced_df.shape[0]})",
        fontsize=12, ha='center', va='center', fontweight='bold', color='black')

    ax.invert_yaxis()
    ax.set_axis_off()

    # Legend for shot types
    legend_elements = [
        mpatches.Patch(color=shot_colors[shot], label=shot) for shot in shot_colors
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    # plt.show()
    return fig