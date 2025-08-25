import os
from xml_to_xsd.xsd_generator import generate_xsd
from xml_to_xsd.xml_validator import xml_validator
from json_to_schema.json_schema_generator import json_schema_generator
from json_to_schema.json_validator import json_validator

def schema_generator(JSON_DIR, JSON_SCHEMA_DIR, XML_DIR, XSD_DIR, CONFIG_FILE):

    # Get all JSON files in the json directory
    json_files = []
    xml_files = []

    if os.path.exists(JSON_DIR):
        for file in os.listdir(JSON_DIR):
            if file.endswith('.json'):
                json_files.append(file)

    for filename in json_files:
        schema = json_schema_generator(f"{JSON_DIR}/{filename}", JSON_SCHEMA_DIR, CONFIG_FILE)
        result = json_validator(f"{JSON_DIR}/{filename}", schema)
        
    if os.path.exists(XML_DIR):
        for file in os.listdir(XML_DIR):
            if file.endswith('.xml'):
                xml_files.append(file)

    for filename in xml_files:
        xsd_str = generate_xsd(f"{XML_DIR}/{filename}", XSD_DIR, CONFIG_FILE)
        result = xml_validator(f"{XML_DIR}/{filename}", xsd_str)

if __name__ == "__main__":

    # === Folders ===
    JSON_DIR = "files/json"
    JSON_SCHEMA_DIR = "files/json_schema"
    XML_DIR = "files/xml"
    XSD_DIR = "files/xsd"
    CONFIG_FILE = "config.json"
    
    schema_generator(JSON_DIR, JSON_SCHEMA_DIR, XML_DIR, XSD_DIR, CONFIG_FILE)