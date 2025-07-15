from schema_generator import json_to_schema, json_validator
import json

# Load multiple configs
with open("config.json", "r", encoding="utf-8") as f:
    configs = json.load(f)

for config in configs:
    json_file = config["json_file"]
    optional_fields = config.get("optional_fields", [])
    allow_null_fields = config.get("allow_null_fields", [])
    exclude_fields = config.get("exclude_fields", [])

    # Load JSON data
    with open(f"json/{json_file}.json", "r", encoding="utf-8") as f:
        json_string = f.read()

    # Generate schema
    schema = json_to_schema(
        json_string,
        optional_fields=optional_fields,
        allow_null_fields=allow_null_fields,
        exclude_fields=exclude_fields
    )

    # Save schema
    with open(f"json_schema/{json_file}_schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    # Validate JSON against schema
    with open(f"json_schema/{json_file}_schema.json", "r", encoding="utf-8") as f:
        json_schema = f.read()

    print(f"{json_file}: {json_validator(json_string, json_schema)}")