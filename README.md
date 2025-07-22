# JSON Schema Generator

A Python script that automatically generates JSON schemas based on checksums of JSON file structures.

## How It Works

### Checksum Generation Process

1. **Key Extraction**: The script extracts all keys from JSON files recursively, creating a flattened list of field paths (e.g., `user.name`, `user.address.street`)

2. **Configuration Consideration**: Optional fields defined in `config.json` are excluded from the checksum calculation, allowing structural variations without generating new schemas

3. **Checksum Creation**: A SHA-256 hash is generated from the sorted list of extracted keys, creating a unique identifier for each JSON structure

4. **Schema Identification**: The checksum serves as both the filename and ID for the generated schema file

### Processing Flow

- Script processes all `.json` files in the `json/` folder
- For each file, generates a structural checksum
- Checks if a schema with that checksum already exists in `json_schema/` folder
- If schema exists: validates JSON against existing schema
- If schema doesn't exist: generates new schema file named `{checksum}.json`

## Directory Structure

```
├── json/              # Input JSON files
├── json_schema/       # Generated schema files (named by checksum)
├── config.json        # Optional configuration for field handling
└── script.py          # Main script
```

## Key Benefits

- **Efficient**: Only generates schemas for unique JSON structures
- **Consistent**: Same structure = same checksum = same schema
- **Configurable**: Supports optional and nullable field definitions
- **Automated**: Processes all JSON files in batch