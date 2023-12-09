import datetime
import json
from typing import Dict

import pytz
from pydantic import BaseModel, Field


class StarChallenge(BaseModel):
    get_star_ts: int
    star_index: int


class Member(BaseModel):
    id: int
    name: str
    stars: int
    global_score: int
    local_score: int
    last_star_ts: int
    completion_day_level: Dict[str, Dict[str, StarChallenge]]

    def daily_challenge(self, day, challenge) -> StarChallenge:
        day = str(day)
        challenge = str(challenge)
        return self.completion_day_level.get(day, {}).get(challenge)

    def daily_time_diff(self, day) -> int:
        s1 = self.daily_challenge(day, 1)
        s2 = self.daily_challenge(day, 2)
        if s1 and s2:
            return s2.get_star_ts - s1.get_star_ts
        return None

    @property
    def datarow(self):
        d = self.model_dump()
        del d["completion_day_level"]
        for i in range(1, 26):
            p = f"day_{i}"
            s1 = self.daily_challenge(i, 1)
            if s1:
                d[f"{p}_1_ts"] = s1.get_star_ts
            s2 = self.daily_challenge(i, 2)
            if s2:
                d[f"{p}_2_ts"] = s2.get_star_ts
            d[f"{p}_diff"] = self.daily_time_diff(i)
        return d


class Leaderboard(BaseModel):
    event: str
    owner_id: int
    members: Dict[str, Member]


# Function to read and parse the JSON file
def read_and_parse_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
        root = Leaderboard(**data)
        return root


def parse_json(json_str):
    data = json.loads(json_str)
    root = Leaderboard(**data)
    return root


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
