import json
from jsonschema import Draft7Validator

def json_validator(json_path, schema_obj):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_obj = json.load(f)

        validator = Draft7Validator(schema_obj)
        errors = sorted(validator.iter_errors(json_obj), key=lambda e: e.path)

        if not errors:
            return True

        print("❌ JSON validation failed:\n")
        for error in errors:
            path = ".".join(str(x) for x in error.path) or "root"
            print(f"[{path}] {error.message}")
        return False

    except Exception as e:
        print("Error:", e)
        return False