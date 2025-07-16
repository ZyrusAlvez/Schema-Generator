import json
import os
from schema_generator import json_validator

schema_name = "client-sample_schema.json"  # <-- Change this to your target schema

# Load the selected schema
with open(f"json_schema/{schema_name}", "r", encoding="utf-8") as sf:
    schema = json.load(sf)

# Auto-load all JSON files in the /json folder
json_files = [f for f in os.listdir("json") if f.endswith(".json")]

# Validate each JSON file
for filename in json_files:
    with open(f"json/{filename}", "r", encoding="utf-8") as jf:
        data = json.load(jf)

    print(f"🔍 Validating {filename}...")
    result = json_validator(data, schema)
    print("✅ Valid\n" if result else "❌ Invalid\n")