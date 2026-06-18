import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

client = RedCapMockClient()

df = pd.DataFrame(client.get_survey_responses())
df = df[df["month"].notna()]

features = []

for pid in df["record_id"].unique():

    person = df[df["record_id"] == pid].sort_values("month")

    if len(person) < 10:
        continue

    baseline = person.iloc[0]["perceived_stress_score"]
    final = person.iloc[-1]["perceived_stress_score"]

    slope = np.polyfit(
        person["month"],
        person["perceived_stress_score"],
        1
    )[0]

    features.append({
        "record_id": pid,
        "baseline": baseline,
        "final": final,
        "change": final - baseline,
        "mean_stress": person["perceived_stress_score"].mean(),
        "max_stress": person["perceived_stress_score"].max(),
        "slope": slope
    })

features_df = pd.DataFrame(features)

kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

features_df["trajectory_group"] = kmeans.fit_predict(
    features_df[
        ["baseline",
         "final",
         "change",
         "mean_stress",
         "max_stress",
         "slope"]
    ]
)

print("\nGROUP COUNTS")
print(features_df["trajectory_group"].value_counts())

print("\nGROUP PROFILE")
print(
    features_df.groupby("trajectory_group")[
        ["baseline","final","change","mean_stress","slope"]
    ].mean()
)

features_df.to_csv(
    "analysis/outputs/trajectory_groups.csv",
    index=False
)

print("\nSaved:")
print("analysis/outputs/trajectory_groups.csv")
