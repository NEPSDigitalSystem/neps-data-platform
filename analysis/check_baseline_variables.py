import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient

import pandas as pd

client = RedCapMockClient()

df = pd.DataFrame(client.get_survey_responses())

baseline = df[df["month"] == 0]

print("\nBaseline Missing Values\n")

print(
    baseline.isnull().sum()
    .sort_values(ascending=False)
)
