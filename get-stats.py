import datetime
import itertools
import pickle

import numpy as np
import pandas as pd
from tqdm import tqdm

LEVELS = ["NEW", "NOV", "INT", "ADV", "ALS", "CHMP"]
LEVEL_TO_RANK = {level: i for i, level in enumerate(LEVELS)}
LEVEL_TO_POINTS_THRESHOLD = {"NOV": 16, "INT": 30, "ADV": 60, "ALS": 150, "CHMP": 1e9}
NOVICE_RANK = LEVEL_TO_RANK["NOV"]
INTERMEDIATE_RANK = LEVEL_TO_RANK["INT"]

data = pickle.load(open("data.pkl", "rb"))
dancer_infos = []
for dancer in tqdm(data):
    main_role_info = dancer["dominate_data"]
    level = main_role_info["level"]["allowed"]
    if level not in LEVEL_TO_RANK:
        # Invalid ranks: "PRO" (e.g., dancer 5)
        continue
    rank = LEVEL_TO_RANK[level]
    if rank < INTERMEDIATE_RANK:
        continue
    placements = main_role_info["placements"].get("West Coast Swing")
    if placements is None:
        continue

    dancer_info = {"id": dancer["dancer_wsdcid"]}
    for rank_i in range(NOVICE_RANK, rank + 1):
        level_i = LEVELS[rank_i]
        if level_i not in placements:
            continue
        level_results = placements[level_i]["competitions"]

        first_point_time = level_results[-1]["event"]["date"]
        finish_time = None
        cumulative_points = 0
        threshold = LEVEL_TO_POINTS_THRESHOLD[level_i]
        for result in level_results[::-1]:
            cumulative_points += result["points"]
            if cumulative_points >= threshold:
                finish_time = result["event"]["date"]
                break

        # Also check if they got out of this division by pointing in the
        # division above.
        if rank_i + 1 < len(LEVELS):
            next_level_results = placements.get(LEVELS[rank_i + 1])
            if next_level_results is not None:
                maybe_finish_time = next_level_results["competitions"][-1]["event"][
                    "date"
                ]
                if finish_time is None or datetime.datetime.strptime(
                    maybe_finish_time, "%B %Y"
                ) < datetime.datetime.strptime(finish_time, "%B %Y"):
                    finish_time = maybe_finish_time

        dancer_info[f"{level_i}_first_point_time"] = first_point_time
        if finish_time is not None:
            dancer_info[f"{level_i}_finish_time"] = finish_time
    dancer_infos.append(dancer_info)



def column_sort_key(column_name):
    level = column_name.split("_")[0]
    key = LEVEL_TO_RANK[level] * 2
    if "first_point_time" in column_name:
        return key
    elif "finish_time" in column_name:
        return key + 1
    else:
        raise ValueError(f"Invalid column name: {column_name}")


df = pd.DataFrame(dancer_infos).set_index("id")
df = df[sorted(df.columns, key=column_sort_key)]


for column in df.columns:
    df[column] = pd.to_datetime(df[column], format="%B %Y")

for col_1, col_2 in itertools.combinations(df.columns, 2):
    print(f"{col_1} to {col_2} in months:")
    diffs = df[col_2].dt.to_period("M") - df[col_1].dt.to_period("M")
    diffs = diffs[~diffs.isnull()].apply(lambda x: x.n).astype(int)
    # There's weird stuff like people who got their first points in a lower
    # division after they finished a higher division, let's cut all those people
    # out.
    # Also going to cut out gaps of 0 months, it's not that interesting to see
    # all the people who finished novice by first competing in intermediate
    # (either by petitioning, or under old point thresholds)
    diffs = diffs[diffs > 0]

    print(diffs.describe(
            percentiles=[0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
        )
    )
    print()
