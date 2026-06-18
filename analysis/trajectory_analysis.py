import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.mixture import GaussianMixture

client = RedCapMockClient()

df = pd.DataFrame(client.get_survey_responses())

# Keep monthly records
df = df[df["month"].notna()]

# Create participant × month matrix
trajectory = df.pivot_table(
    index="record_id",
    columns="month",
    values="perceived_stress_score"
)

# Fill missing values
imputer = SimpleImputer(strategy="mean")
X = imputer.fit_transform(trajectory)

# 4 trajectory groups
gmm = GaussianMixture(
    n_components=4,
    random_state=42
)

clusters = gmm.fit_predict(X)

trajectory["trajectory_group"] = clusters

print("\nTRAJECTORY GROUP COUNTS")
print(
    trajectory["trajectory_group"]
    .value_counts()
    .sort_index()
)

print("\nSAMPLE PARTICIPANTS")
print(
    trajectory["trajectory_group"]
    .head(20)
)
