import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient
import pandas as pd

client = RedCapMockClient()

df = pd.DataFrame(client.get_survey_responses())

df = df[df["month"].notna()]

trend = (
    df.groupby("month")
    [
        [
            "perceived_stress_score",
            "anxiety_score",
            "depression_score"
        ]
    ]
    .mean()
    .reset_index()
)

print(trend.head())

trend.to_csv(
    "analysis/outputs/trend_summary.csv",
    index=False
)

print("\nSaved:")
print("analysis/outputs/trend_summary.csv")
