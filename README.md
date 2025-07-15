# Schema Generator

A Python module for automatically generating JSON schemas from JSON data and validating JSON objects against those schemas. This tool is designed for internal use as an integration module.

## Features

- **Automatic Schema Generation**: Generate JSON schemas from existing JSON data
- **Flexible Configuration**: Support for optional fields, nullable fields, and field exclusion
- **Batch Processing**: Process multiple JSON files using a single configuration file
- **Schema Validation**: Validate JSON objects against generated schemas
- **Custom Field Handling**: Fine-grained control over field requirements and types

## Main Functions

The `schema_generator` module provides two main functions:
- `json_to_schema()`: Generates a JSON schema from a JSON object
- `json_validator()`: Validates a JSON object against a schema

## Usage

### Simple Integration (In-Memory)

```python
from schema_generator import json_to_schema, json_validator

# Simple data object
data = {
    "is_admin": True,
    "notifications_enabled": False
}

# Generate schema from data
schema = json_to_schema(data)

# Validate data against generated schema
print(json_validator(data, schema))  # Output: True
```

### Basic Integration with JSON Files

```python
from schema_generator import json_to_schema, json_validator
import json

# Load JSON data
with open("data.json", "r", encoding="utf-8") as f:
    json_obj = json.load(f)

# Generate schema
schema = json_to_schema(json_obj)

# Validate data against schema
is_valid = json_validator(json_obj, schema)
print(f"Validation result: {is_valid}")
```

### Advanced Usage with Configuration

The module supports batch processing using a configuration file approach:

```python
from schema_generator import json_to_schema, json_validator
import json

# Load configuration
with open("config.json", "r", encoding="utf-8") as f:
    configs = json.load(f)

# Process each configuration
for config in configs:
    json_file = config["json_file"]
    optional_fields = config.get("optional_fields", [])
    allow_null_fields = config.get("allow_null_fields", [])
    exclude_fields = config.get("exclude_fields", [])

    # Load JSON data
    with open(f"json/{json_file}.json", "r", encoding="utf-8") as f:
        json_obj = json.load(f)

    # Generate schema with custom options
    schema = json_to_schema(
        json_obj,
        optional_fields=optional_fields,
        allow_null_fields=allow_null_fields,
        exclude_fields=exclude_fields
    )

    # Save generated schema
    with open(f"json_schema/{json_file}_schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    # Validate and report
    validation_result = json_validator(json_obj, schema)
    print(f"{json_file}: {validation_result}")
```

## Configuration Format

The configuration file (`config.json`) should contain an array of configuration objects:

```json
[
  {
    "json_file": "example-data",
    "optional_fields": ["user.profile.bio"],
    "allow_null_fields": ["user.last_login"],
    "exclude_fields": ["internal_id", "temp_data"]
  }
]
```

### Configuration Options

- **`json_file`** (required): Name of the JSON file (without extension) to process
- **`optional_fields`** (optional): Array of field paths that should be marked as optional in the schema
- **`allow_null_fields`** (optional): Array of field paths that should allow null values
- **`exclude_fields`** (optional): Array of field paths to exclude from the generated schema

### Field Path Notation

Field paths use dot notation for nested objects:
- `"name"` - Root level field
- `"user.email"` - Nested field
- `"user.profile.bio"` - Deeply nested field

## Functions

### `json_to_schema(json_obj, optional_fields=[], allow_null_fields=[], exclude_fields=[])`

Generates a JSON schema from a JSON object.

**Parameters:**
- `json_obj`: The JSON object to generate schema from
- `optional_fields`: List of field paths to mark as optional
- `allow_null_fields`: List of field paths to allow null values
- `exclude_fields`: List of field paths to exclude from schema

**Returns:** JSON schema object

### `json_validator(json_obj, schema)`

Validates a JSON object against a schema.

**Parameters:**
- `json_obj`: The JSON object to validate
- `schema`: The JSON schema to validate against

**Returns:** Boolean indicating validation result

## Directory Structure

The tool expects the following directory structure:

```
project/
├── config.json
├── json/
│   ├── example1.json
│   ├── example2.json
│   └── ...
├── json_schema/
│   ├── example1_schema.json
│   ├── example2_schema.json
│   └── ...
└── your_script.py
```

## Example Configuration

```json
[
  {
    "json_file": "user-data",
    "optional_fields": ["user.middle_name", "user.phone"],
    "allow_null_fields": ["user.last_login"],
    "exclude_fields": ["internal_tracking_id"]
  },
  {
    "json_file": "product-catalog",
    "optional_fields": [],
    "allow_null_fields": ["product.discontinued_date"],
    "exclude_fields": ["internal_notes"]
  }
]
```

## Error Handling

The module handles standard JSON loading and processing errors. Ensure that:
- JSON files are valid and properly formatted
- File paths exist and are accessible
- Required directories (`json/`, `json_schema/`) exist
- Configuration file follows the expected format

## Integration Notes

- This module is designed for internal use and integration into larger systems
- Generated schemas follow JSON Schema specification
- The tool processes files sequentially and provides validation feedback
- Output schemas are saved with `_schema.json` suffix
- All file operations use UTF-8 encoding for proper character handling