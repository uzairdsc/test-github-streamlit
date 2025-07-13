import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib.patches import Wedge  # add this at the top if not already
from io import BytesIO



def test_match_wagon(df, player_name, inns, bowler_name=None, run_values=None,transparent=False):
    # Filter by match, player, and innings
    local_df = df[
        (df['batsmanName'] == player_name) &
        (df['inningNumber'] == inns)
    ].copy()

    # Apply optional bowler filter
    if bowler_name:
        local_df = local_df[local_df['bowlerName'] == bowler_name]

    # Set score = 0 for extras without modifying original df
    # extras = ['wide', 'bye', 'leg bye']
    # local_df.loc[local_df['outcome'].str.lower().isin(extras), 'teamRuns'] = 0

    # playing_team = local_df['team_bat'].iloc[0] if not local_df.empty else "Unknown"
    # opponent_team = local_df['team_bowl'].iloc[0] if not local_df.empty else "Unknown"

    if run_values is not None:
        local_df = local_df[local_df['batsmanRuns'].isin(run_values)]

    # Filter valid shot points
    balls_faced_df = local_df[
        (local_df['batsmanName'] == player_name) & (local_df['wides'] == 0)
    ][['batsmanName', 'wagonX', 'wagonY', 'teamRuns', 'batsmanRuns']].dropna()


    player_data = local_df[
        ~((local_df['wagonX'] == 0) & (local_df['wagonY'] == 0))
    ][['wagonX', 'wagonY', 'teamRuns', 'batsmanRuns', 'isFour', 'isSix', 'shotControl', 'shotType']].dropna()

    if player_data.empty:
        print(f"No data found for {player_name} in this match, and in innings {inns}")
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
    # player_data['color'] = player_data['score'].map(score_colors).fillna('black')
    player_data['color'] = player_data['batsmanRuns'].map(score_colors).fillna('black')

    # Additional stats
    total_4s = int(player_data['isFour'].sum())
    total_6s = int(player_data['isSix'].sum())
    control_pct = round((local_df[(local_df['wides'] == 0) & (local_df['shotControl'] == 0)].shape[0]) / balls_faced_df.shape[0] * 100, 2)

    # Most productive shot
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

    # Plot setup
    # fig, ax = plt.subplots(figsize=(7, 7))
    # ax.set_facecolor("white")
    fig, ax = plt.subplots(figsize=(7, 7), facecolor='none' if transparent else 'white')
    ax.set_facecolor('none' if transparent else 'white')
    center_x, center_y = 180, 164

    # Boundary
    boundary = plt.Circle((center_x, center_y), 180, color='black',
                          fill=False, linestyle='-', linewidth=1.2)
    ax.add_artist(boundary)

    # Pitch
    pitch_length = 20.12
    pitch_width = 3
    pitch = plt.Rectangle((center_x - pitch_width / 2, center_y),
                          pitch_width, pitch_length,
                          edgecolor='black', facecolor='none', linewidth=1.5)
    ax.add_artist(pitch)

    # Quadrants
    for angle in range(0, 360, 45):
        rad = np.deg2rad(angle)
        x_end = center_x + 180 * np.cos(rad)
        y_end = center_y + 180 * np.sin(rad)
        ax.plot([center_x, x_end], [center_y, y_end], color='black', linestyle='-', linewidth=1.3)

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

    # print("Quadrant Totals:", quadrant_totals)
    # top_quadrants = sorted(range(8), key=lambda i: quadrant_totals[i], reverse=True)[:2]
    # print("Top Quadrants:", top_quadrants)  # Debug

    # Highlight top 2 quadrants using Wedge from matplotlib.patches
    top_quadrants = sorted(range(8), key=lambda i: quadrant_totals[i], reverse=True)[:2]
    # rank_color = {top_quadrants[0]: 1.0, top_quadrants[1]: 0.7}
    rank_color = {top_quadrants[i]: 1.0 - i * 0.3 for i in range(len(top_quadrants))}
    cmap = cm.get_cmap('Blues')  # or any other you prefer

    for i in range(8):
        theta1 = i * 45
        theta2 = theta1 + 45

        # if i in top_quadrants:
        #     wedge = Wedge(center=(center_x, center_y),
        #                 r=180,
        #                 theta1=theta1,
        #                 theta2=theta2,
        #                 color=cmap(rank_color[i]),
        #                 # color=cmap(i / 7),
        #                 alpha=0.3,
        #                 zorder=0)
        #     ax.add_patch(wedge)
        if i in rank_color:
            wedge = Wedge(center=(center_x, center_y),
                        r=180,
                        theta1=theta1,
                        theta2=theta2,
                        color=cmap(rank_color[i]),
                        # color=cmap(i / 7),
                        alpha=0.3,
                        zorder=0)
            ax.add_patch(wedge)

        # Label coordinates
        mid_angle = np.deg2rad(theta1 + 22.5)
        label_x = center_x + 100 * np.cos(mid_angle)
        label_y = center_y + 100 * np.sin(mid_angle)
        label_color = 'darkred' if i in top_quadrants else 'red'
        ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=13, color=label_color,
                ha='center', va='center')

    # # Highlight top 2 quadrants
    # top_quadrants = sorted(range(8), key=lambda i: quadrant_totals[i], reverse=True)[:2]
    # # colors = 
    # colors = cm.get_cmap('GnBu', 8)

    # for i in range(8):
    #     mid_angle = np.deg2rad(i * 45 + 22.5)
    #     label_x = center_x + 100 * np.cos(mid_angle)
    #     label_y = center_y + 100 * np.sin(mid_angle)

    #     label_color = 'red'
    #     if i in top_quadrants:
    #         wedge = plt.Circle((center_x, center_y), 180, color=colors(i / 7), alpha=0.25, zorder=0)
    #         theta1 = i * 45
    #         theta2 = theta1 + 45
    #         # ax.add_patch(plt.Wedge((center_x, center_y), 180, theta1, theta2, color=colors(i / 7), alpha=0.25))
    #         ax.add_patch(Wedge((center_x, center_y), 180, theta1, theta2, color=colors(i / 7), alpha=0.25))
    #         label_color = 'darkred'

    #     ax.text(label_x, label_y, f"{quadrant_totals[i]} runs", fontsize=13, color=label_color,
    #             ha='center', va='center')

    # Layout
    ax.set_xlim(-20, 380)
    ax.set_ylim(-20, 410)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_aspect('equal', adjustable='box')

    ax.set_title(f"{player_name} Wagon Wheel Innings: {inns}", fontsize=12)

    # ax.text(180, 360, f"Total Runs: {total_score} ({balls_faced_df.shape[0]} balls)",
    #         fontsize=11, ha='center', fontweight='bold', color='black')
    # ax.text(180, 375, f"4s: {total_4s} | 6s: {total_6s} | Shot Control: {control_pct}%",
    #         fontsize=11, ha='center', color='darkgreen')
    # ax.text(180, 390, f"Most Productive Shot: {most_prod_shot_text}",
    #         fontsize=11, ha='center', color='navy')
    ax.text(180, 360, f"Total Runs: {total_score} ({balls_faced_df.shape[0]} balls)",
            fontsize=11, ha='center', fontweight='bold')
    ax.text(180, 375, f"4s: {total_4s} | 6s: {total_6s}",
            fontsize=11, ha='center', color='darkgreen')
    ax.text(180, 390, f"Control: {control_pct}%",
            fontsize=11, ha='center', color='purple')
    ax.text(180, 405, f"Most Productive Shot: {most_prod_shot_text}",
            fontsize=11, ha='center', color='navy')

    ax.invert_yaxis()
    ax.set_axis_off()

    # Legend
    # legend_elements = [
    #     mpatches.Patch(color=color, label=f'{score} run' + ('s' if score != 1 else ''))
    #     for score, color in score_colors.items()
    # ]
    # ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
    plt.close(fig)
    return fig
    # plt.show()