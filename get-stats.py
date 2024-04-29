import datetime
import itertools
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

LEVELS = ["NEW", "NOV", "INT", "ADV", "ALS", "CHMP"]
LEVEL_TO_RANK = {level: i for i, level in enumerate(LEVELS)}
LEVEL_TO_POINTS_THRESHOLD = {
    "NEW": 1,
    "NOV": 16,
    "INT": 30,
    "ADV": 60,
    "ALS": 150,
    "CHMP": 1e9,
}


def column_sort_key(column_name):
    """Sort function for dataframe columns."""
    level = column_name.split("_")[0]
    key = LEVEL_TO_RANK[level] * 2
    if "first_point_time" in column_name:
        return key
    elif "finish_time" in column_name:
        return key + 1
    else:
        raise ValueError(f"Invalid column name: {column_name}")


def to_date(date_str):
    """Convert a date string like "January 2020" to a datetime object."""
    return datetime.datetime.strptime(date_str, "%B %Y")


def get_months_between(date1, date2):
    """Get the number of months between two dates."""
    return (date1.year - date2.year) * 12 + date1.month - date2.month


data = pickle.load(open("data.pkl", "rb"))
dancer_infos = []
for dancer in tqdm(data):
    main_role_info = dancer["dominate_data"]
    level = main_role_info["level"]["allowed"]
    if level not in LEVEL_TO_RANK:
        # Ignore level "PRO", e.g., dancer 5, as I don't know how to categorize
        # it.
        continue
    rank = LEVEL_TO_RANK[level]
    placements = main_role_info["placements"]
    if isinstance(placements, list):
        # Ignore people who somehow have no placements, e.g., dancer 3. In this
        # case, `placements` is an empty list rather than a dict.
        continue
    placements = placements.get("West Coast Swing")
    if placements is None:
        continue

    dancer_info = {"id": dancer["dancer_wsdcid"]}
    for rank_i in range(rank + 1):
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
                if finish_time is None or to_date(maybe_finish_time) < to_date(
                    finish_time
                ):
                    finish_time = maybe_finish_time

        dancer_info[f"{level_i}_first_point_time"] = first_point_time
        if finish_time is not None and threshold > 1:
            dancer_info[f"{level_i}_finish_time"] = finish_time

    dancer_infos.append(dancer_info)


df = pd.DataFrame(dancer_infos).set_index("id")
df = df[sorted(df.columns, key=column_sort_key)]
for column in df.columns:
    df[column] = pd.to_datetime(df[column], format="%B %Y")

# Plot histogram of time between first NOV point and first ALS point.
col_1 = "NOV_first_point_time"
col_2 = "ALS_first_point_time"
diffs = df[col_2].dt.to_period("M") - df[col_1].dt.to_period("M")
diffs = diffs[~diffs.isnull()].apply(lambda x: x.n).astype(int)
diffs = diffs[diffs >= 0]
plt.title(f"{col_1} to {col_2} in months, n={len(diffs)}")
plt.xlabel("Months")
plt.ylabel("Density")
plt.hist(diffs, bins=np.arange(0, diffs.max() + 1) - 0.5, rwidth=0.8, density=True)
plt.minorticks_on()
plt.show()

# Print out stats for all pairs of columns.
for col_1, col_2 in itertools.combinations(df.columns, 2):
    print(f"{col_1} to {col_2} in months:")
    diffs = df[col_2].dt.to_period("M") - df[col_1].dt.to_period("M")
    diffs = diffs[~diffs.isnull()].apply(lambda x: x.n).astype(int)
    # Let's cut out people who got their first points in a lower division after
    # they finished a higher division, etc.
    # Also let's cut out gaps of 0 months as it's not interesting to see all
    # the people with a time of 0 months between NOV_finish_time and
    # INT_first_point_time because they either petitioned or they were under old
    # point thresholds. This is crude, but whatever.
    diffs = diffs[diffs > 0]

    print(
        diffs.describe(percentiles=[0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    )
    print()
