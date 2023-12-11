from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from aoc_leaderboard import charts
from aoc_leaderboard.leaderboard import parse_json

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

analysis_tabs = st.tabs(["Star Count", "Daily Analysis", "Member Analysis", "Raw Data"])
if st.session_state["leaderboard_data"] is not None:
    # Plotting the data
    plt.style.use("dark_background")

    # Sorting the data by stars in descending order
    members_data = st.session_state["leaderboard_data"]
    df = pd.DataFrame([m.datarow for m in members_data])
    df = df.sort_values(by=["stars", "last_star_ts"], ascending=[True, False])
    dr = charts.get_days_range(members_data)

    with analysis_tabs[3]:
        st.dataframe(df)

    with analysis_tabs[0]:
        fig = charts.get_local_score(df)
        st.pyplot(fig)

    with analysis_tabs[1]:
        fig = charts.num_stars_won(df, dr)
        st.pyplot(fig)

        fig = charts.daily_stars_progression(df, dr)
        st.pyplot(fig)

    with analysis_tabs[2]:
        selected_users = st.multiselect(
            "Participants",
            [m.name for m in members_data],
            default=None,
        )
        fig = charts.get_member_analysis_pt1(selected_users, df, dr)
        st.pyplot(fig)

        fig = charts.get_member_analysis_pt2(selected_users, df, dr)
        st.pyplot(fig)

st.session_state["disabled"] = False
