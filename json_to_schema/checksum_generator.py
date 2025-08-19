import json
import hashlib

def extract_keys_from_json(obj, optional_fields, allow_null_fields):
    keys = []

    def recurse(o, path=""):
        if isinstance(o, dict):
            for k in sorted(o):
                full_key = f"{path}.{k}" if path else k

                if full_key in optional_fields:
                    full_key += "0"
                if full_key in allow_null_fields:
                    full_key += "1"

                keys.append(full_key)
                
                recurse(o[k], full_key)
        elif isinstance(o, list):
            for item in o:
                recurse(item, path)

    recurse(obj)
    print(keys)
    return keys

def generate_checksum_from_keys(key_list):
    key_str = json.dumps(sorted(key_list), separators=(',', ':'))
    return hashlib.sha256(key_str.encode()).hexdigest()

def get_json_checksum(data, optional_fields, allow_null_fields):
    keys = extract_keys_from_json(data, optional_fields, allow_null_fields)
    return generate_checksum_from_keys(keys)