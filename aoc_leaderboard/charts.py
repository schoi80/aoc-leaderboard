import datetime
from functools import reduce
from typing import List

import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import plotly.subplots as sp
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
    fig = px.bar(
        df,
        x="name",
        y="stars",
        title="Number of stars won per member",
        log_y=True,
    )
    fig.update_layout(
        showlegend=False,
        yaxis_title="Number of Stars",
        xaxis_title="Name",
        xaxis={"categoryorder": "total ascending"},
        hovermode="x unified",
    )
    fig.update_traces(hovertemplate="%{y:,.0f}<extra></extra>")
    return fig


def num_stars_won(df: DataFrame, dr: range):
    star_1_columns = [f"day_{i}_1_ts" for i in dr]
    star_2_columns = [f"day_{i}_2_ts" for i in dr]

    star_1_counts = [df[col].notna().sum() for col in star_1_columns]
    star_2_counts = [df[col].notna().sum() for col in star_2_columns]

    days = list(dr)

    # Creating a Plotly figure for the stacked bar chart
    fig = sp.make_subplots()

    # Adding the first set of bars (Star 1)
    fig.add_trace(go.Bar(x=days, y=star_1_counts, name="Star 1", marker_color="green"))

    # Adding the second set of bars (Star 2)
    fig.add_trace(
        go.Bar(
            x=days,
            y=star_2_counts,
            name="Star 2",
            marker_color="teal",
            base=star_1_counts,
        )
    )

    # Updating layout
    fig.update_layout(
        title="Number of stars won per day",
        xaxis=dict(title="Day", tickmode="array", tickvals=days),
        yaxis=dict(title="Total stars won"),
        legend=dict(x=0, y=1.0),
        barmode="stack",
    )

    # Adding annotations
    for i, (count1, count2) in enumerate(zip(star_1_counts, star_2_counts)):
        fig.add_annotation(
            x=days[i],
            y=count1 / 2,
            text=str(count1),
            showarrow=False,
            font=dict(color="white"),
        )
        fig.add_annotation(
            x=days[i],
            y=count1 + count2 / 2,
            text=str(count2),
            showarrow=False,
            font=dict(color="white"),
        )

    return fig


def daily_stars_progression(df: DataFrame, dr: range):
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

    # Creating a Plotly figure
    fig = sp.make_subplots()

    # Adding traces for each day
    for day, counts in cumulative_counts.items():
        fig.add_trace(go.Scatter(x=_TIME_INTERVALS, y=counts, mode="lines", name=day))

    # Adding trace for the average progression
    fig.add_trace(
        go.Scatter(
            x=_TIME_INTERVALS,
            y=average_progression,
            mode="lines",
            name="Average",
            line=dict(color="white", dash="dash"),
        )
    )

    # Updating the layout of the plot
    fig.update_layout(
        title="Total progression of stars per day",
        xaxis_title="Time since problem open",
        yaxis_title="Number of stars",
        legend=dict(x=1.05, y=0.5, xanchor="left", yanchor="middle"),
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # Setting colors for x-axis, y-axis, and title
    fig.update_xaxes(tickcolor="white", title_font=dict(color="white"))
    fig.update_yaxes(tickcolor="white", title_font=dict(color="white"))
    fig.update_layout(title_font=dict(color="white"))

    return fig


def get_member_analysis_part1(members: List[str], df: DataFrame, dr: range):
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

    # Creating a Plotly figure
    fig = sp.make_subplots()

    # Adding traces for each user
    for user, times in time_to_solve.items():
        fig.add_trace(go.Scatter(x=days_list, y=times, mode="lines", name=user))

    # Updating the layout of the plot
    fig.update_layout(
        title="Time to solve part 1 from problem open",
        xaxis_title="Day",
        yaxis_title="Time to solve",
        yaxis_type="log",
        yaxis=dict(tickvals=_TIME_SECONDS, ticktext=_TIME_INTERVALS),
        legend=dict(x=1.05, y=0.5, xanchor="left", yanchor="middle"),
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # Setting colors for x-axis, y-axis, and title
    fig.update_xaxes(tickcolor="white", title_font=dict(color="white"))
    fig.update_yaxes(tickcolor="white", title_font=dict(color="white"))
    fig.update_layout(title_font=dict(color="white"))

    return fig


def get_member_analysis_pt2(members: List[str], df: DataFrame, dr: range):
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

    # Creating a Plotly figure
    fig = sp.make_subplots()

    # Adding traces for each user
    for user, times in time_to_solve_part2.items():
        # Converting seconds to minutes for the y-values
        times_in_minutes = [time / 60 if time is not None else None for time in times]
        fig.add_trace(
            go.Scatter(x=days_list, y=times_in_minutes, mode="lines", name=user)
        )

    # Setting custom y-ticks and labels
    custom_y_ticks = [
        t / 60
        for t in [
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
    ]
    custom_y_labels = [
        "0.25m",
        "0.5m",
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

    # Updating the layout of the plot
    fig.update_layout(
        title="Time to solve part 2 after solving part 1 (in minutes)",
        xaxis_title="Day",
        yaxis_title="Time to solve (minutes)",
        yaxis_type="log",
        yaxis=dict(tickvals=custom_y_ticks, ticktext=custom_y_labels),
        legend=dict(x=1.05, y=0.5, xanchor="left", yanchor="middle"),
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # Setting colors for x-axis, y-axis, and title
    fig.update_xaxes(tickcolor="white", title_font=dict(color="white"))
    fig.update_yaxes(tickcolor="white", title_font=dict(color="white"))
    fig.update_layout(title_font=dict(color="white"))

    return fig
