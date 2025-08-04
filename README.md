# Schema Generator

A powerful tool for automatically generating JSON Schemas and XSD (XML Schema Definition) files from JSON and XML files respectively. The tool uses checksum-based caching for rapid processing and includes built-in validators to verify files against their generated schemas.

## Features

- **JSON to JSON Schema**: Generate JSON Schema (Draft 07) from JSON files
- **XML to XSD**: Generate XSD schema from XML files
- **Checksum-based Caching**: Uses file checksums as filenames for rapid schema retrieval
- **Built-in Validation**: Validates JSON/XML files against their generated schemas
- **Configuration Support**: Customize schema generation with optional fields and nullable fields
- **Batch Processing**: Process entire directories of files at once

## Project Structure

```
Schema-Generator/
├── schema_generator.py                   # Main entry point and batch processor
├── sample_integration.py                 # Usage examples and integration guide
├── test.py                               # Sample file generations
├── config.json                           # Configuration file for schema customization
├── README.md                             # This documentation
│
├── json_to_schema/                       # JSON Schema generation module
│   ├── __init__.py                       # Module initialization
│   ├── json_schema_generator.py          # Core JSON to JSON Schema conversion logic
│   ├── json_validator.py                 # JSON validation against schemas
│   └── checksum_generator.py             # JSON checksum utilities for caching
│
├── xml_to_xsd/                           # XSD generation module  
│   ├── __init__.py                       # Module initialization
│   ├── xsd_generator.py                  # Core XML to XSD conversion logic
│   ├── xml_parser.py                     # XML parsing utilities
│   ├── xml_validator.py                  # XML validation against XSD schemas
│   ├── schema_inferer.py                 # Type inference for XSD generation
│   └── checksum_generator.py             # XML checksum utilities for caching
│
└── files/                                # Data directories
    ├── json/                             # Input JSON files (100+ files supported)
    ├── json_schema/                      # Generated JSON schemas (checksum-named)
    ├── xml/                              # Input XML files (various types supported)
    └── xsd/                              # Generated XSD files (checksum-named)
```

## Quick Start

### Basic Usage

```python
from schema_generator import schema_generator

# Define directories
JSON_DIR = "files/json"
JSON_SCHEMA_DIR = "files/json_schema"
XML_DIR = "files/xml"
XSD_DIR = "files/xsd"
CONFIG_FILE = "config.json"

# Process all files in directories
schema_generator(JSON_DIR, JSON_SCHEMA_DIR, XML_DIR, XSD_DIR, CONFIG_FILE)
```

### Individual File Processing

#### JSON Schema Generation

```python
from json_to_schema.json_schema_generator import json_schema_generator
from json_to_schema.json_validator import json_validator

# Generate schema for a specific JSON file
target_json = "files/json/client.json"
schema = json_schema_generator(target_json, "files/json_schema")

# Validate the JSON file against its schema
result = json_validator(target_json, schema)
print(result)  # True if valid, error details if invalid
```

#### XSD Generation

```python
from xml_to_xsd.xsd_generator import XSDGenerator
from xml_to_xsd.xml_validator import xml_validator

# Generate XSD for a specific XML file
target_xml = "files/xml/nama1.xml"
xsd_generator = XSDGenerator()
schema = xsd_generator.generate_xsd(target_xml, "files/xsd")

# Validate the XML file against its schema
result = xml_validator(target_xml, schema)
print(result)  # True if valid, error details if invalid
```

## Configuration

Create a `config.json` file to customize schema generation:

```json
[
  {
    "file": "client.json",
    "optional_fields": ["middle_name", "phone"],
    "allow_null_fields": ["email", "address.apartment"]
  },
  {
    "file": "products.json", 
    "optional_fields": ["description", "tags"],
    "allow_null_fields": ["discount_price"],
  }
]
```

### Configuration Options

- **`file`**: Target filename to apply configuration to
- **`optional_fields`**: Array of field paths that should not be required
- **`allow_null_fields`**: Array of field paths that can accept null values

Field paths support dot notation for nested objects (e.g., `"address.apartment"`).

## How It Works

### Checksum-Based Caching

1. **Generate Checksum**: Creates a unique checksum based on file content and configuration
2. **Check Existing Schema**: Looks for existing schema file using checksum as filename
3. **Load or Generate**: 
   - If schema exists: Loads and returns existing schema
   - If not exists: Generates new schema and saves with checksum filename

### Benefits

- **Fast Processing**: Avoids regenerating schemas for unchanged files
- **Efficient Storage**: Each unique data structure gets one schema file  
- **Automatic Updates**: Schema regenerates only when source data changes
- **Scalable**: Handles large datasets (100+ JSON files, 20+ XML files as demonstrated)
- **SHA-256 Checksums**: Uses secure hash-based filenames for reliable caching

## Example Output

### JSON Schema Example

Input JSON:
```json
{
  "name": "John Doe",
  "age": 30,
  "email": "john@example.com",
  "address": {
    "street": "123 Main St",
    "city": "Anytown"
  }
}
```

Generated Schema (saved as `6cd4967660b2b322aa2b96aab0d056d5c42c9c1920f889361b7181f9b1731f2a.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "number"},
    "email": {"type": "string"},
    "address": {
      "type": "object",
      "properties": {
        "street": {"type": "string"},
        "city": {"type": "string"}
      },
      "required": ["street", "city"]
    }
  },
  "required": ["name", "age", "email", "address"],
  "checksum_id": "6cd4967660b2b322aa2b96aab0d056d5c42c9c1920f889361b7181f9b1731f2a"
}
```

## Console Output

```
📄 JSON: files/json/client.json | 📁 Schema: files/json_schema/6cd4967660b2b322aa2b96aab0d056d5c42c9c1920f889361b7181f9b1731f2a.json
✅ New schema generated and saved.

📄 XML: files/xml/nama1.xml | 📁 XSD: files/xsd/05e09de8a872ee5fc36309608eda07436098f248cf26bd078230c603e6c3f762.xsd  
✅ Existing schema loaded.
```

## Error Handling

The tool provides clear error messages for common issues:

- **Invalid JSON/XML**: Reports parsing errors with line numbers
- **File Access Issues**: Handles missing directories and permission errors  
- **Configuration Errors**: Warns about malformed config files
- **Validation Failures**: Detailed error messages for schema validation

## API Reference

### Functions

#### `schema_generator(json_dir, json_schema_dir, xml_dir, xsd_dir, config_file)`
Processes all JSON and XML files in specified directories.

#### `json_schema_generator(json_path, json_schema_path, config_file=None)`
Generates JSON Schema for a single JSON file.

#### `json_validator(json_path, schema)`
Validates JSON file against a schema.

#### `xml_validator(xml_path, schema)`
Validates XML file against XSD schema.

### Classes

#### `XSDGenerator`
Main class for XML to XSD conversion located in `xml_to_xsd/xsd_generator.py`.

**Methods:**
- `generate_xsd(xml_path, xsd_path)`: Generate XSD schema from XML file
