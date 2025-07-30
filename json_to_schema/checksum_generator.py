import json
import hashlib

def extract_keys_from_json(obj, optional_fields):
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

def get_json_checksum(data, optional_fields):
    keys = extract_keys_from_json(data, optional_fields)
    return generate_checksum_from_keys(keys)