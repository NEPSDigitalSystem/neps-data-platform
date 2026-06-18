import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

print("=" * 60)
print("NEPS RANDOM FOREST MODEL")
print("=" * 60)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

client = RedCapMockClient()

df = pd.DataFrame(client.get_survey_responses())

df = df[df["month"].notna()]

print(f"\nTotal Records: {len(df)}")
print(f"Participants: {df['record_id'].nunique()}")

# --------------------------------------------------
# CREATE OUTCOME VARIABLE
# --------------------------------------------------

features = []

for pid in df["record_id"].unique():

    person = (
        df[df["record_id"] == pid]
        .sort_values("month")
    )

    if len(person) < 2:
        continue

    baseline = person.iloc[0]["perceived_stress_score"]
    final = person.iloc[-1]["perceived_stress_score"]

    change = final - baseline

    features.append({
        "record_id": pid,
        "stress_change": change
    })

trajectory_df = pd.DataFrame(features)

# High-risk trajectory:
# Stress increased by more than 10 points

trajectory_df["high_risk"] = (
    trajectory_df["stress_change"] > 10
).astype(int)

print("\nHigh Risk Counts")
print(trajectory_df["high_risk"].value_counts())

# --------------------------------------------------
# BASELINE PREDICTORS
# --------------------------------------------------

baseline = df[df["month"] == 0]

model_df = baseline.merge(
    trajectory_df[
        [
            "record_id",
            "high_risk"
        ]
    ],
    on="record_id"
)

# --------------------------------------------------
# CONVERT CATEGORICAL VARIABLES
# --------------------------------------------------

print("\nSleep Quality Categories:")
print(model_df["sleep_quality"].unique())

sleep_map = {
    "Poor": 1,
    "Fair": 2,
    "Good": 3,
    "Excellent": 4
}

model_df["sleep_quality"] = (
    model_df["sleep_quality"]
    .map(sleep_map)
)

# --------------------------------------------------
# SELECT FEATURES
# --------------------------------------------------

X = model_df[
    [
        "anxiety_score",
        "depression_score",
        "sleep_quality",
        "social_isolation_score",
        "self_esteem_score",
        "loneliness_score"
    ]
]

y = model_df["high_risk"]

# --------------------------------------------------
# REMOVE MISSING VALUES
# --------------------------------------------------

combined = pd.concat([X, y], axis=1)

combined = combined.dropna()

X = combined.drop(columns=["high_risk"])
y = combined["high_risk"]

print("\nTraining Dataset Shape:")
print(X.shape)

print("\nVariable Types:")
print(X.dtypes)

# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

# --------------------------------------------------
# RANDOM FOREST MODEL
# --------------------------------------------------

rf = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

rf.fit(X_train, y_train)

predictions = rf.predict(X_test)

# --------------------------------------------------
# MODEL PERFORMANCE
# --------------------------------------------------

print("\nMODEL PERFORMANCE")
print("=" * 60)

print(
    classification_report(
        y_test,
        predictions
    )
)

# --------------------------------------------------
# FEATURE IMPORTANCE
# --------------------------------------------------

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": rf.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

print("\nTOP PREDICTORS")
print("=" * 60)

print(importance)

# --------------------------------------------------
# SAVE OUTPUT
# --------------------------------------------------

Path("analysis/outputs").mkdir(
    parents=True,
    exist_ok=True
)

importance.to_csv(
    "analysis/outputs/feature_importance.csv",
    index=False
)

print("\nSaved:")
print("analysis/outputs/feature_importance.csv")

print("\nMODEL COMPLETE")
