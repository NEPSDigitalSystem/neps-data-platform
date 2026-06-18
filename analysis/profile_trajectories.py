import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.mixture import GaussianMixture

client = RedCapMockClient()

df = pd.DataFrame(client.get_survey_responses())

df = df[df["month"].notna()]

# Wide stress matrix
trajectory = df.pivot_table(
    index="record_id",
    columns="month",
    values="perceived_stress_score"
)

imputer = SimpleImputer(strategy="mean")
X = imputer.fit_transform(trajectory)

gmm = GaussianMixture(
    n_components=4,
    random_state=42
)

clusters = gmm.fit_predict(X)

trajectory["trajectory_group"] = clusters

# Merge back to original data
group_df = trajectory["trajectory_group"].reset_index()

merged = df.merge(group_df, on="record_id")

# Mean stress by group and month
profile = (
    merged
    .groupby(["trajectory_group", "month"])
    ["perceived_stress_score"]
    .mean()
    .reset_index()
)

print(profile.head(50))

# Summary by group
summary = (
    merged
    .groupby("trajectory_group")
    ["perceived_stress_score"]
    .agg(["mean", "min", "max"])
)

print("\nGROUP SUMMARY")
print(summary)
