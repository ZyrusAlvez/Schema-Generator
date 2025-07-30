from schema_generator import schema_generator

JSON_DIR = "files/json"
JSON_SCHEMA_DIR = "files/json_schema"
XML_DIR = "files/xml"
XSD_DIR = "files/xsd"
CONFIG_FILE = "config.json"


schema_generator(JSON_DIR, JSON_SCHEMA_DIR, XML_DIR, XSD_DIR, CONFIG_FILE)