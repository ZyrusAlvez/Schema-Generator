# Import necessary modules and functions for generating and validating schemas
from schema_generator import schema_generator
from xml_to_xsd import XSDGenerator
from xml_to_xsd.xml_validator import xml_validator
from json_to_schema.json_schema_generator import json_schema_generator
from json_to_schema.json_validator import json_validator

# Define directories for input/output files and configuration
JSON_DIR = "files/json"                 # Folder containing JSON files
JSON_SCHEMA_DIR = "files/json_schema"   # Folder to save generated JSON Schemas
XML_DIR = "files/xml"                   # Folder containing XML files
XSD_DIR = "files/xsd"                   # Folder to save generated XSD (XML Schema Definition) files
CONFIG_FILE = "config.json"             # Config file used by the schema generator

# Generate schemas and validate all files in the specified directories based on the config file
schema_generator(JSON_DIR, JSON_SCHEMA_DIR, XML_DIR, XSD_DIR, CONFIG_FILE)

# --- Sample usage for JSON ---

# Specify a target JSON file for validation
target_json = f"{JSON_DIR}/client.json"

# Generate a JSON Schema for the target file and save it to JSON_SCHEMA_DIR
schema = json_schema_generator(target_json, JSON_SCHEMA_DIR)

# Validate the target JSON file using the generated schema
result = json_validator(target_json, schema)
print(result)  # Output the validation result (True if valid, error details if invalid)

# --- Sample usage for XML ---

# Specify a target XML file for validation
target_xml = f"{XML_DIR}/nama1.xml"

# Create an instance of the XSD generator
xsd_generator = XSDGenerator()

# Generate an XSD (XML Schema) from the target XML file and save it to XSD_DIR
schema = xsd_generator.generate_xsd(target_xml, XSD_DIR)

# Validate the target XML file using the generated schema
result = xml_validator(target_xml, schema)
print(result)  # Output the validation result (True if valid, error details if invalid)