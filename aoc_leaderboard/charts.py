import datetime
from functools import reduce
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pytz
from matplotlib.pyplot import Figure
from pandas import DataFrame

from aoc_leaderboard.leaderboard import Member

# Create a list to store time intervals for x-axis
_TIME_INTERVALS = ["5m", "10m", "30m", "1h", "2h", "4h", "8h", "1d", "2d", "4d"]

# Convert the time intervals to seconds for calculations
_TIME_SECONDS = [
    5 * 60,
    10 * 60,
    30 * 60,
    60 * 60,
    2 * 60 * 60,
    4 * 60 * 60,
    8 * 60 * 60,
    24 * 60 * 60,
    2 * 24 * 60 * 60,
    4 * 24 * 60 * 60,
]


# Convert UNIX timestamp to datetime and adjust for EST timezone
def convert_to_est(unix_timestamp):
    utc_time = datetime.datetime.utcfromtimestamp(unix_timestamp)
    est = pytz.timezone("US/Eastern")
    return utc_time.replace(tzinfo=pytz.utc).astimezone(est)


# Calculate the midnight timestamp (in EST) for a given day's timestamp
def get_midnight_est(day_timestamp):
    est_time = convert_to_est(day_timestamp)
    return datetime.datetime(
        est_time.year, est_time.month, est_time.day, tzinfo=est_time.tzinfo
    )


def get_days_range(data: List[Member]):
    curr_day = reduce(lambda x, y: max(x, len(y.completion_day_level)), data, 0)
    return range(1, curr_day + 1)


def get_local_score(df: DataFrame) -> Figure:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df["name"], df["stars"], color="yellow")
    ax.set_xlabel("Number of stars won", color="white")
    ax.set_ylabel("Name", color="white")
    ax.set_title("Number of stars won per member", color="white")
    ax.grid(axis="x", color="gray")
    ax.tick_params(axis="both", colors="white")
    return fig


def num_stars_won(df: DataFrame, dr: range) -> Figure:
    # Columns related to star 1 and star 2 timestamps for each day
    star_1_columns = [f"day_{i}_1_ts" for i in dr]
    star_2_columns = [f"day_{i}_2_ts" for i in dr]

    # Calculate the counts for star 1 and star 2 for each day
    star_1_counts = [df[col].notna().sum() for col in star_1_columns]
    star_2_counts = [df[col].notna().sum() for col in star_2_columns]

    # Plotting the stacked bar chart
    days = list(dr)
    print(days)
    fig, ax = plt.subplots(figsize=(10, 4))
    bars1 = ax.bar(days, star_1_counts, label="Star 1", color="green")
    bars2 = ax.bar(
        days, star_2_counts, bottom=star_1_counts, label="Star 2", color="teal"
    )

    # Annotating each bar with the respective count
    for bar in bars1:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yval - 5,
            str(int(yval)),
            ha="center",
            va="bottom",
            color="white",
        )

    for bar in bars2:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yval + bar.get_y() - 5,
            str(int(yval)),
            ha="center",
            va="bottom",
            color="white",
        )

    ax.set_xlabel("Day")
    ax.set_ylabel("Total stars won")
    ax.set_title("Number of stars won per day")
    ax.set_xticks(days)
    ax.set_xticklabels(days)  # Ensure x-axis labels are always displayed
    ax.tick_params(axis="both", colors="white")
    ax.legend(loc="upper left")

    return fig


def daily_stars_progression(df: DataFrame, dr: range) -> Figure:
    # Create a dictionary to store cumulative counts for each day over the time intervals
    cumulative_counts = {f"Day {i}": [] for i in dr}

    # Calculate the cumulative counts for each day
    for i in dr:
        for t in _TIME_SECONDS:
            count_star1 = (
                df[f"day_{i}_1_ts"].notnull()
                & (df[f"day_{i}_1_ts"] - df[f"day_{i}_1_ts"].min() <= t)
            ).sum()
            count_star2 = (
                df[f"day_{i}_2_ts"].notnull()
                & (df[f"day_{i}_2_ts"] - df[f"day_{i}_2_ts"].min() <= t)
            ).sum()
            cumulative_counts[f"Day {i}"].append(count_star1 + count_star2)

    # Calculate the average progression
    average_progression = [
        np.mean([cumulative_counts[f"Day {i}"][j] for i in dr])
        for j in range(len(_TIME_SECONDS))
    ]

    # Plotting the progression of stars per day with the legend on the right side of the graph
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plotting the lines for each day
    for day, counts in cumulative_counts.items():
        ax.plot(_TIME_INTERVALS, counts, label=day)

    # Plotting the average progression
    ax.plot(
        _TIME_INTERVALS,
        average_progression,
        label="Average",
        color="white",
        linestyle="--",
    )

    # Setting the title and labels
    ax.set_title("Total progression of stars per day", color="white")
    ax.set_xlabel("Time since problem open", color="white")
    ax.set_ylabel("Number of stars", color="white")
    ax.tick_params(axis="both", colors="white")
    ax.legend(
        loc="center left", bbox_to_anchor=(1, 0.5)
    )  # Positioning the legend on the right side
    plt.grid(True, which="both", ls="--", c="0.5")

    # Displaying the plot
    plt.tight_layout()
    return fig


def get_member_analysis_pt1(members: List[str], df: DataFrame, dr: range) -> Figure:
    days_list = list(dr)

    # Calculate "time to solve" for each user for each day
    time_to_solve = {}
    for user in members:
        user_data = df[df["name"] == user]
        if not user_data.empty:
            times = [
                (
                    user_data[f"day_{i}_1_ts"].values[0]
                    - get_midnight_est(user_data[f"day_{i}_1_ts"].values[0]).timestamp()
                )
                if not np.isnan(user_data[f"day_{i}_1_ts"].values[0])
                else None
                for i in dr
            ]
            time_to_solve[user] = times

    # Plotting the "time to solve" for each selected user
    fig, ax = plt.subplots(figsize=(14, 5))
    for user, times in time_to_solve.items():
        ax.plot(days_list, times, label=user)

    # Setting the title, labels, and other plot properties
    ax.set_title("Time to solve part 1 from problem open", color="white")
    ax.set_xlabel("Day", color="white")
    ax.set_ylabel("Time to solve", color="white")
    ax.set_yscale("log")
    ax.set_yticks(_TIME_SECONDS)
    ax.set_yticklabels(_TIME_INTERVALS)
    ax.set_xticks(days_list)
    ax.tick_params(axis="both", colors="white")
    ax.legend(
        loc="center left", bbox_to_anchor=(1, 0.5)
    )  # Positioning the legend on the right side
    plt.grid(True, which="both", ls="--", c="0.5")

    # Displaying the plot
    plt.tight_layout()
    return fig


def get_member_analysis_pt2(members: List[str], df: DataFrame, dr: range) -> Figure:
    # Calculate "time to solve part 2 after solving part 1" for each user for each day
    days_list = list(dr)
    time_to_solve_part2 = {}
    for user in members:
        user_data = df[df["name"] == user]
        if not user_data.empty:
            times = [
                (
                    user_data[f"day_{i}_2_ts"].values[0]
                    - user_data[f"day_{i}_1_ts"].values[0]
                )
                if not np.isnan(user_data[f"day_{i}_2_ts"].values[0])
                and not np.isnan(user_data[f"day_{i}_1_ts"].values[0])
                else None
                for i in dr
            ]
            time_to_solve_part2[user] = times

    # Plotting the "time to solve part 2 after solving part 1" for each selected user
    fig, ax = plt.subplots(figsize=(14, 5))
    for user, times in time_to_solve_part2.items():
        ax.plot(days_list, times, label=user)

    # Setting the title, labels, and other plot properties
    ax.set_title("Time to solve part 2 after solving part 1", color="white")
    ax.set_xlabel("Day", color="white")
    ax.set_ylabel("Time to solve (s)", color="white")
    ax.set_yscale("log")
    # Setting custom y-ticks to match the given image
    custom_y_ticks = [
        15,
        30,
        1 * 60,
        2 * 60,
        5 * 60,
        10 * 60,
        30 * 60,
        1 * 60 * 60,
        2 * 60 * 60,
        4 * 60 * 60,
        8 * 60 * 60,
        1 * 24 * 60 * 60,
        4 * 24 * 60 * 60,
    ]
    custom_y_labels = [
        "15s",
        "30s",
        "1m",
        "2m",
        "5m",
        "10m",
        "30m",
        "1h",
        "2h",
        "4h",
        "8h",
        "1d",
        "4d",
    ]
    ax.set_yticks(custom_y_ticks)
    ax.set_yticklabels(custom_y_labels)
    ax.set_xticks(days_list)
    ax.tick_params(axis="both", colors="white")
    ax.legend(
        loc="center left", bbox_to_anchor=(1, 0.5)
    )  # Positioning the legend on the right side
    plt.grid(True, which="both", ls="--", c="0.5")

    # Displaying the plot
    plt.tight_layout()
    return fig
