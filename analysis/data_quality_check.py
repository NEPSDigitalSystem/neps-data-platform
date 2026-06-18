import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient
import pandas as pd

client = RedCapMockClient()

df = pd.DataFrame(client.get_survey_responses())

print("\nMONTH SUMMARY")
print(df["month"].describe())

print("\nOBSERVATIONS PER PARTICIPANT")
print(df.groupby("record_id")["month"].count().describe())
