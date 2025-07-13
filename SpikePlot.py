# method 5
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
def test_match_spike_runs(df, player_name, inns, run_values=None, bowler_name=None, transparent=False):
    # Filter by match, player, and innings
    local_df = df[
        (df['batsmanName'] == player_name) & (df['inningNumber'] == inns)
    ].copy()

    if bowler_name:
        local_df = local_df[local_df['bowlerName'] == bowler_name]

    balls_faced_df = local_df[
        (local_df['batsmanName'] == player_name) & (local_df['wides'] == 0)
    ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()

    # Handle run_values = None to include all run types
    if run_values is None:
        filtered_df = local_df.copy()
    else:
        filtered_df = local_df[local_df['batsmanRuns'].isin(run_values)]

    # Filter valid shot points
    player_data = filtered_df[
        ~((filtered_df['wagonX'] == 0) & (filtered_df['wagonY'] == 0))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()

    if player_data.empty:
        print(f"No data found for {player_name} in this match and innings {inns} for selected runs {run_values}")
        return

    # === Additional Stats ===
    total_4s = player_data['isFour'].sum()
    total_6s = player_data['isSix'].sum()
    # control_pct = round(player_data['shotControl'].mean() * 100, 2)
    # control_pct = round((player_data['shotControl'] == 0).sum() / balls_faced_df.shape[0] * 100, 2)
    control_pct = round((local_df[(local_df['wides'] == 0) & (local_df['shotControl'] == 0)].shape[0]) / balls_faced_df.shape[0] * 100, 2)
    # valid_balls = df[
    #     (df['batsmanName'] == player_name) &
    #     (df['inningNumber'] == inns) &
    #     (df['wides'] == 0)
    # ]

    # if bowler_name:
    #     valid_balls = valid_balls[valid_balls['bowlerName'] == bowler_name]

    # control_pct = round((valid_balls['shotControl'] == 1).sum() / valid_balls.shape[0] * 100, 2)

    # Most productive shot calculation
    if 'shotType' in player_data.columns and not player_data.empty:
        shot_summary = player_data.groupby('shotType').agg({
            'batsmanRuns': 'sum',
            'isFour': 'sum',
            'isSix': 'sum'
        }).sort_values(by='batsmanRuns', ascending=False)

        if not shot_summary.empty:
            top_shot = shot_summary.iloc[0]
            top_shot_type = shot_summary.index[0]
            most_prod_shot_text = (
                f"{top_shot_type}: {int(top_shot['batsmanRuns'])} runs, "
                f"{int(top_shot['isFour'])}x4s, {int(top_shot['isSix'])}x6s"
            )
        else:
            most_prod_shot_text = "No productive shot data"
    else:
        most_prod_shot_text = "No shot type data"

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
    # fig, ax = plt.subplots(figsize=(7, 7))
    # ax.set_facecolor("white")
    fig, ax = plt.subplots(figsize=(7, 7), facecolor='none' if transparent else 'white')
    ax.set_facecolor('none' if transparent else 'white')
    center_x, center_y = 180, 164

    # Draw lines
    for _, row in player_data.iterrows():
        ax.plot([center_x, row['wagonX']], [center_y, row['wagonY']],
                color=row['color'], linewidth=1.0, alpha=0.8)

    # Boundary
    # boundary = plt.Circle((center_x, center_y), 175, color='black',
    #                       fill=False, linestyle='--', linewidth=1.2)
    # ax.add_artist(boundary)

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
    ax.set_ylim(-20, 410)
    ax.set_xticks([]), ax.set_yticks([])
    ax.set_xticklabels([]), ax.set_yticklabels([])
    ax.set_aspect('equal', adjustable='box')
    ax.set_title(f"{player_name} Spike Graph Wheel Innings: {inns}", fontsize=12)

    ax.text(180, 360, f"Total Runs: {total_score} ({balls_faced_df.shape[0]} balls)",
            fontsize=11, ha='center', fontweight='bold')
    ax.text(180, 375, f"4s: {total_4s} | 6s: {total_6s}",
            fontsize=11, ha='center', color='darkgreen')
    ax.text(180, 390, f"Shot Control: {control_pct}%",
            fontsize=11, ha='center', color='purple')
    ax.text(180, 405, f"Most Productive Shot: {most_prod_shot_text}",
            fontsize=11, ha='center', color='navy')

    ax.invert_yaxis()
    ax.set_axis_off()

    # Legend
    legend_elements = [
        mpatches.Patch(color=color, label=f'{score} run' + ('s' if score != 1 else ''))
        for score, color in score_colors.items() if run_values is None or score in run_values
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    plt.close(fig)
    return fig
    # plt.show()