import json
from jsonschema import Draft7Validator

# By default (if no arguments are passed):
# ✅ All fields are included in "properties"
# ✅ All fields are marked as "required"
# ✅ All fields must not be null (unless in allow_null_fields)

def json_to_schema(
    json_str,
    optional_fields=None,
    allow_null_fields=None,
    exclude_fields=None
):
    optional_fields = set(optional_fields or [])
    allow_null_fields = set(allow_null_fields or [])
    exclude_fields = set(exclude_fields or [])

    try:
        json_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string: {e}")

    def infer_type(key, value, path=""):
        current_path = f"{path}.{key}" if path and key else key or path

        if current_path in exclude_fields:
            return None

        if isinstance(value, str):
            base_type = {"type": "string"}
        elif isinstance(value, bool):
            base_type = {"type": "boolean"}
        elif isinstance(value, int) or isinstance(value, float):
            base_type = {"type": "number"}
        elif isinstance(value, list):
            base_type = {"type": "array"}
            if value:
                base_type["items"] = infer_type(None, value[0], current_path)
        elif isinstance(value, dict):
            props, reqs = {}, []
            for k, v in value.items():
                inferred = infer_type(k, v, current_path)
                if inferred is not None:
                    props[k] = inferred
                    full_key = f"{current_path}.{k}" if current_path else k
                    if full_key not in optional_fields:
                        reqs.append(k)
            result = {"type": "object", "properties": props}
            if reqs:
                result["required"] = reqs
            return result
        else:
            base_type = {"type": "null"}

        if current_path in allow_null_fields and base_type["type"] != "null":
            base_type = {"anyOf": [base_type, {"type": "null"}]}

        return base_type

    properties = {}
    required_fields = []
    for k, v in json_data.items():
        inferred = infer_type(k, v)
        if inferred:
            properties[k] = inferred
            if k not in optional_fields:
                required_fields.append(k)

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": properties
    }

    if required_fields:
        schema["required"] = required_fields

    return schema

def json_validator(json_str, schema_str):
    try:
        json_obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON string: {e}")
        return False

    try:
        schema = json.loads(schema_str)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid schema string: {e}")
        return False

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(json_obj), key=lambda e: e.path)
    if not errors:
        return True

    print("❌ JSON validation failed:\n")
    for error in errors:
        path = ".".join(str(x) for x in error.path) or "root"
        print(f"[{path}] {error.message}")
    return False
