import json
from .checksum_generator import get_json_checksum
import os

# === Schema Generator ===

def json_to_schema(json_obj, optional_fields=None, allow_null_fields=None, exclude_fields=None) -> dict:
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

# === Configuration Helper ===

def load_config(config_file):
    """Load configuration file"""
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  Warning: Could not load config file - {e}")
    return []

def get_file_config(filename, configs):
    """Get configuration for a specific file"""
    for config in configs:
        if config.get("file") == filename:
            return config
    return {}

# === File Processing ===
def json_schema_generator(json_path, json_schema_path, config_file = None):
    filename = json_path.split("/")[-1]
    
    # Get configuration for this file
    optional_fields = []
    allow_null_fields = []
    if config_file:
        configs = load_config(config_file)
        file_config = get_file_config(filename, configs)
        optional_fields = file_config.get("optional_fields", [])
        allow_null_fields = file_config.get("allow_null_fields", [])
    
    # Load JSON
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {json_path}: {e}")
        return False
    
    # Generate checksum
    checksum_id = get_json_checksum(json_data, optional_fields)
    
    # Schema file path based on checksum ID
    schema_file_path = os.path.join(json_schema_path, f"{checksum_id}.json")
    print(f"📄 JSON: {json_path} | 📁 Schema: {schema_file_path}")
    
    try:
        with open(schema_file_path, "r", encoding="utf-8") as f:
            existing_schema = json.load(f)
            print("✅ Existing schema loaded.")
            return existing_schema
        
    except:
        schema_data = json_to_schema(json_data, optional_fields, allow_null_fields)
        schema_data["checksum_id"] = checksum_id
        
        try:
            with open(schema_file_path, "w", encoding="utf-8") as f:
                json.dump(schema_data, f, indent=2)
                print("✅ New schema generated and saved.")
        except Exception as e:
            print(f"❌ Failed to write schema: {e}")
            return False
        
        return schema_data