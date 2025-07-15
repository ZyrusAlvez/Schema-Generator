from schema_generator import json_to_schema, json_validator
import json

# json to json schema
json_file = "client-sample-delivery"

with open(f"json/{json_file}.json", "r", encoding="utf-8") as f:
    json_string = f.read()

schema = json_to_schema(json_string, optional_fields=["clip.source_metadata.ave"])

with open(f"json_schema/{json_file}_schema.json", "w", encoding="utf-8") as f:
    json.dump(schema, f, indent=2)

# validation
with open(f"json/{json_file}.json", "r", encoding="utf-8") as f:
    json_string = f.read()
with open(f"json_schema/{json_file}_schema.json", "r", encoding="utf-8") as f:
    json_schema = f.read()

print(json_validator(json_string, json_schema))