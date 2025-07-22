import json
import hashlib
import os
from jsonschema import Draft7Validator

# === Folders ===
JSON_DIR = "json"
SCHEMA_DIR = "json_schema"
CONFIG_FILE = "config.json"

os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(SCHEMA_DIR, exist_ok=True)

# === Checksum Functions ===

def extract_keys_from_json(obj, filename, configs):
    # Get file-specific config
    file_config = get_file_config(filename, configs)
    optional_fields = set(file_config.get("optional_fields", [])) if file_config else set()
    keys = []

    def recurse(o, path=""):
        if isinstance(o, dict):
            for k in sorted(o):
                full_key = f"{path}.{k}" if path else k
                if full_key not in optional_fields:
                    keys.append(full_key)
                recurse(o[k], full_key)
        elif isinstance(o, list):
            for item in o:
                recurse(item, path)

    recurse(obj)
    return keys


def generate_checksum_from_keys(key_list):
    key_str = json.dumps(sorted(key_list), separators=(',', ':'))
    return hashlib.sha256(key_str.encode()).hexdigest()

def get_json_checksum(data, filename, configs):
    keys = extract_keys_from_json(data, filename, configs)
    return generate_checksum_from_keys(keys)

# === Schema Generator ===

def json_to_schema(json_obj, optional_fields=None, allow_null_fields=None, exclude_fields=None):
    optional_fields = set(optional_fields or [])
    allow_null_fields = set(allow_null_fields or [])
    exclude_fields = set(exclude_fields or [])

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
            item_schemas = []
            for item in value:
                item_schema = infer_type(None, item, current_path)
                if item_schema and item_schema not in item_schemas:
                    item_schemas.append(item_schema)
            if item_schemas:
                base_type["items"] = item_schemas[0] if len(item_schemas) == 1 else {"anyOf": item_schemas}
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

    properties, required_fields = {}, []
    for k, v in json_obj.items():
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

# === JSON Validator ===

def json_validator(json_obj, schema_obj):
    validator = Draft7Validator(schema_obj)
    errors = sorted(validator.iter_errors(json_obj), key=lambda e: e.path)
    
    if not errors:
        return True
    
    print("❌ JSON validation failed:\n")
    for error in errors:
        path = ".".join(str(x) for x in error.path) or "root"
        print(f"[{path}] {error.message}")
    return False

# === Configuration Helper ===

def load_config():
    """Load configuration file if it exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  Warning: Could not load config file - {e}")
    return []

def get_file_config(filename, configs):
    """Get configuration for a specific file"""
    for config in configs:
        if config.get("json_file") == filename:
            return config
    return {}

# === File Processing ===

def process_json_file(filename, configs):
    json_file_path = os.path.join(JSON_DIR, f"{filename}.json")
    
    # Get configuration for this file
    file_config = get_file_config(filename, configs)
    optional_fields = file_config.get("optional_fields", [])
    allow_null_fields = file_config.get("allow_null_fields", [])
    
    # Load JSON
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {json_file_path}: {e}")
        return False
    
    # Generate checksum
    checksum_id = get_json_checksum(json_data, filename, configs)
    
    # Schema file path based on checksum ID
    schema_file_path = os.path.join(SCHEMA_DIR, f"{checksum_id}.json")
    try:
        with open(schema_file_path, "r", encoding="utf-8") as f:
            existing_schema = json.load(f)

        # Validate JSON against existing schema
        if json_validator(json_data, existing_schema):
            return True
        else:
            return False
        
    # Generate new schema (only reached if no matching schema exists)
    except:
        schema_data = json_to_schema(json_data, optional_fields, allow_null_fields)
        schema_data["checksum_id"] = checksum_id
        
        # Save new schema with checksum ID as filename
        try:
            with open(schema_file_path, "w", encoding="utf-8") as f:
                json.dump(schema_data, f, indent=2)
        except Exception as e:
            return False
        
        # Validate JSON against new schema
        if json_validator(json_data, schema_data):
            return True
        else:
            return False

# === Main Logic ===

def main():
    print("🚀 Starting JSON Schema Generator and Validator")
    print(f"📁 JSON Directory: {JSON_DIR}")
    print(f"📁 Schema Directory: {SCHEMA_DIR}")
    
    # Load configurations
    configs = load_config()
    
    # Get all JSON files in the json directory
    json_files = []
    if os.path.exists(JSON_DIR):
        for file in os.listdir(JSON_DIR):
            if file.endswith('.json'):
                filename = file[:-5]  # Remove .json extension
                json_files.append(filename)
    
    if not json_files:
        print(f"❌ No JSON files found in {JSON_DIR} directory")
        return
    
    for filename in json_files:
        process_json_file(filename, configs)
    print("✅ All JSON files processed successfully")
    
# === Run ===

if __name__ == "__main__":
    main()