import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

print("=" * 60)
print("NEPS RANDOM FOREST V2")
print("=" * 60)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

client = RedCapMockClient()

df = pd.DataFrame(client.get_survey_responses())

df = df[df["month"].notna()]

print("\nTotal Records:", len(df))
print("Participants:", df["record_id"].nunique())

# --------------------------------------------------
# CREATE FUTURE RISK LABEL
# --------------------------------------------------

trajectory_data = []

for pid in df["record_id"].unique():

    person = (
        df[df["record_id"] == pid]
        .sort_values("month")
    )

    if len(person) < 2:
        continue

    baseline_stress = person.iloc[0]["perceived_stress_score"]
    final_stress = person.iloc[-1]["perceived_stress_score"]

    stress_change = final_stress - baseline_stress

    trajectory_data.append({
        "record_id": pid,
        "stress_change": stress_change
    })

trajectory_df = pd.DataFrame(trajectory_data)

trajectory_df["high_risk"] = (
    trajectory_df["stress_change"] > 10
).astype(int)

print("\nHigh Risk Counts")
print(trajectory_df["high_risk"].value_counts())

# --------------------------------------------------
# BASELINE DATA ONLY
# --------------------------------------------------

baseline = df[df["month"] == 0].copy()

# --------------------------------------------------
# ENCODE CATEGORICAL VARIABLES
# --------------------------------------------------

print("\nSleep Quality Categories:")
print(baseline["sleep_quality"].unique())

sleep_map = {
    "Poor": 1,
    "Fair": 2,
    "Good": 3,
    "Excellent": 4
}

baseline["sleep_quality"] = (
    baseline["sleep_quality"]
    .map(sleep_map)
)

print("\nSubstance Use Categories:")
print(baseline["substance_use"].unique())

substance_map = {
    "None": 0,
    "Alcohol": 1,
    "Cannabis": 2,
    "Other": 3
}

baseline["substance_use"] = (
    baseline["substance_use"]
    .map(substance_map)
)

print("\nSuicidality Categories:")
print(baseline["suicidality_screening"].unique())

suicide_map = {
    "No": 0,
    "Passive thoughts": 1,
    "Active plan": 2,
    "Recent attempt": 3
}

baseline["suicidality_screening"] = (
    baseline["suicidality_screening"]
    .map(suicide_map)
)

print("\nFatigue Categories:")
print(baseline["fatigue_level"].unique())

fatigue_map = {
    "None": 0,
    "Mild": 1,
    "Moderate": 2,
    "Severe": 3
}

baseline["fatigue_level"] = (
    baseline["fatigue_level"]
    .map(fatigue_map)
)
# --------------------------------------------------
# MERGE LABELS
# --------------------------------------------------

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
# FEATURES AVAILABLE AT BASELINE
# --------------------------------------------------

predictors = [

    "anxiety_score",
    "depression_score",
    "sleep_quality",
    "social_isolation_score",
    "self_esteem_score",
    "loneliness_score",

    "daily_functioning",
    "school_attendance_days",

    "fatigue_level",

    "substance_use",
    "suicidality_screening"
]

print("\nFatigue After Encoding:")
print(baseline["fatigue_level"].unique())
X = model_df[predictors]

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
# TRAIN TEST SPLIT
# --------------------------------------------------

print("\nVariable Types After Encoding:")
print(X.dtypes)

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
    n_estimators=500,
    max_depth=10,
    random_state=42
)

rf.fit(X_train, y_train)

predictions = rf.predict(X_test)

# --------------------------------------------------
# PERFORMANCE
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
# SAVE RESULTS
# --------------------------------------------------

Path("analysis/outputs").mkdir(
    parents=True,
    exist_ok=True
)

importance.to_csv(
    "analysis/outputs/feature_importance_v2.csv",
    index=False
)

print("\nSaved:")
print("analysis/outputs/feature_importance_v2.csv")
