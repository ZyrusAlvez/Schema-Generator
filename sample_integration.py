from schema_generator import schema_generator
from xml_to_xsd import XSDGenerator
from xml_to_xsd.xml_validator import xml_validator
from json_to_schema.json_schema_generator import json_schema_generator
from json_to_schema.json_validator import json_validator

JSON_DIR = "files/json"
JSON_SCHEMA_DIR = "files/json_schema"
XML_DIR = "files/xml"
XSD_DIR = "files/xsd"
CONFIG_FILE = "config.json"

schema_generator(JSON_DIR, JSON_SCHEMA_DIR, XML_DIR, XSD_DIR, CONFIG_FILE)