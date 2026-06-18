import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.redcap_mock import RedCapMockClient

client = RedCapMockClient()

stats = client.get_stats()

print("\nPROJECT STATISTICS")
print("===================")

for key, value in stats.items():
    print(f"{key}: {value}")
