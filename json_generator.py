# This is only for testing purposes
# It generates JSON files in the "json" directory

import os
import json

# Create folder if it doesn't exist
os.makedirs("json", exist_ok=True)

# Generate and save JSON files
for i in range(100):
    data = {"id": i, "name": f"user_{i}", "active": i % 2 == 0}
    with open(f"json/user_{i}.json", "w") as f:
        json.dump(data, f)