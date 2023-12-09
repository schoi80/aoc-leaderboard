from functools import reduce
from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from aoc_leaderboard.leaderboard import convert_to_est, get_midnight_est, parse_json

st.session_state["leaderboard_data"] = None


def disable(b):
    st.session_state["disabled"] = b


def is_disabled() -> bool:
    return (
        st.session_state.get("disabled", False)
        or st.session_state["file_uploader"] is None
    )


st.set_page_config(
    page_title="Advent of Code: Leaderboard Analysis", page_icon="🔥", layout="wide"
)

# Remove "Deploy" button
# https://discuss.streamlit.io/t/removing-the-deploy-button/53621
st.markdown(
    """
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.file_uploader("Choose a file", type=["json"], key="file_uploader")

if st.session_state["file_uploader"] is not None:
    # Copy uploaded file into data path
    uploaded_file = st.session_state["file_uploader"]
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    df = parse_json(stringio.read())
    st.session_state["leaderboard_data"] = list(df.members.values())

st.markdown(
    """
    # Advent of Code Leaderboard Analysis
    Because we need data insights 🔥🔥🔥
    """
)

import matplotlib.pyplot as plt

analysis_tabs = st.tabs(["Star Count", "Daily Analysis", "Member Analysis", "Raw Data"])
if st.session_state["leaderboard_data"] is not None:
    # Plotting the data
    plt.style.use("dark_background")

    # Sorting the data by stars in descending order
    members_data = st.session_state["leaderboard_data"]
    df = pd.DataFrame([m.datarow for m in members_data])
    df = df.sort_values(by=["stars", "last_star_ts"], ascending=[True, False])
    curr_day = reduce(lambda x, y: max(x, len(y.completion_day_level)), members_data, 0)
    print(f"curr day is {curr_day}")

    days_range = range(1, curr_day + 1)

    with analysis_tabs[3]:
        st.dataframe(df)

    with analysis_tabs[0]:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(df["name"], df["stars"], color="yellow")
        ax.set_xlabel("Number of stars won", color="white")
        ax.set_ylabel("Name", color="white")
        ax.set_title("Number of stars won per member", color="white")
        ax.grid(axis="x", color="gray")

        # To ensure labels and ticks are visible on the dark background
        ax.tick_params(axis="both", colors="white")
        st.pyplot(fig)

    with analysis_tabs[1]:
        # Columns related to star 1 and star 2 timestamps for each day
        star_1_columns = [f"day_{i}_1_ts" for i in days_range]
        star_2_columns = [f"day_{i}_2_ts" for i in days_range]

        # Calculate the counts for star 1 and star 2 for each day
        star_1_counts = [df[col].notna().sum() for col in star_1_columns]
        star_2_counts = [df[col].notna().sum() for col in star_2_columns]

        # Plotting the stacked bar chart
        days = list(days_range)
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
        st.pyplot(fig)

        # Create a list to store time intervals for x-axis
        time_intervals = ["5m", "10m", "30m", "1h", "2h", "4h", "8h", "1d", "2d", "4d"]

        # Convert the time intervals to seconds for calculations
        time_seconds = [
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

        # Create a dictionary to store cumulative counts for each day over the time intervals
        cumulative_counts = {f"Day {i}": [] for i in days_range}

        # Calculate the cumulative counts for each day
        for i in days_range:
            for t in time_seconds:
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
            np.mean([cumulative_counts[f"Day {i}"][j] for i in days_range])
            for j in range(len(time_seconds))
        ]

        # Plotting the progression of stars per day with the legend on the right side of the graph
        fig, ax = plt.subplots(figsize=(14, 7))

        # Plotting the lines for each day
        for day, counts in cumulative_counts.items():
            ax.plot(time_intervals, counts, label=day)

        # Plotting the average progression
        ax.plot(
            time_intervals,
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
        st.pyplot(fig)

    with analysis_tabs[2]:
        selected_users = st.multiselect(
            "Participants",
            [m.name for m in members_data],
            default=None,
        )
        days_list = list(days_range)

        # Calculate "time to solve" for each user for each day
        time_to_solve = {}
        for user in selected_users:
            user_data = df[df["name"] == user]
            if not user_data.empty:
                times = [
                    (
                        user_data[f"day_{i}_1_ts"].values[0]
                        - get_midnight_est(
                            user_data[f"day_{i}_1_ts"].values[0]
                        ).timestamp()
                    )
                    if not np.isnan(user_data[f"day_{i}_1_ts"].values[0])
                    else None
                    for i in days_range
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
        ax.set_yticks(time_seconds)
        ax.set_yticklabels(time_intervals)
        ax.set_xticks(days_list)
        ax.tick_params(axis="both", colors="white")
        ax.legend(
            loc="center left", bbox_to_anchor=(1, 0.5)
        )  # Positioning the legend on the right side
        plt.grid(True, which="both", ls="--", c="0.5")

        # Displaying the plot
        plt.tight_layout()
        st.pyplot(fig)

        # Calculate "time to solve part 2 after solving part 1" for each user for each day
        time_to_solve_part2 = {}
        for user in selected_users:
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
                    for i in days_range
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
        st.pyplot(fig)

st.session_state["disabled"] = False
