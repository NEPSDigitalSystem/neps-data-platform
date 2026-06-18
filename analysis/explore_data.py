import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient
import pandas as pd

client = RedCapMockClient()

# Get all survey responses
responses = client.get_survey_responses()

print("Type:", type(responses))

# If responses is a dictionary
if isinstance(responses, dict):

    print("\nNumber of participants:", len(responses))

    first_pid = list(responses.keys())[0]

    print("\nFirst Participant ID:")
    print(first_pid)

    print("\nNumber of records:")
    print(len(responses[first_pid]))

    print("\nFirst Record:")
    print(responses[first_pid][0])

# Convert to dataframe
records = []

if isinstance(responses, dict):
    for pid, participant_records in responses.items():
        records.extend(participant_records)
else:
    records = responses

df = pd.DataFrame(records)

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nHead:")
print(df.head())

print("\nMONTH SUMMARY")
print(df["month"].describe())

print("\nOBSERVATIONS PER PARTICIPANT")
print(df.groupby("record_id")["month"].count().describe())
