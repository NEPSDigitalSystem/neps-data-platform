import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient
import pandas as pd

client = RedCapMockClient()

df = pd.DataFrame(client.get_survey_responses())

# Keep monthly records only
df = df[df["month"].notna()]

# Participant-level trends
risk_cases = []

for pid in df["record_id"].unique():

    person = df[df["record_id"] == pid].sort_values("month")

    if len(person) < 5:
        continue

    first = person.iloc[0]
    last = person.iloc[-1]

    stress_change = (
        last["perceived_stress_score"]
        - first["perceived_stress_score"]
    )

    anxiety_change = (
        last["anxiety_score"]
        - first["anxiety_score"]
    )

    depression_change = (
        last["depression_score"]
        - first["depression_score"]
    )

    if (
        stress_change > 5
        or anxiety_change > 4
        or depression_change > 4
    ):

        risk_cases.append({
            "record_id": pid,
            "stress_change": round(stress_change, 2),
            "anxiety_change": round(anxiety_change, 2),
            "depression_change": round(depression_change, 2)
        })

risk_df = pd.DataFrame(risk_cases)

print("\nHIGH RISK PARTICIPANTS")
print(risk_df.head(20))

print("\nTOTAL HIGH RISK:")
print(len(risk_df))

risk_df.to_csv(
    "analysis/outputs/high_risk_participants.csv",
    index=False
)

print("\nSaved:")
print("analysis/outputs/high_risk_participants.csv")
