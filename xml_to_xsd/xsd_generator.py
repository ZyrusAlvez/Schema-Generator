import json
import os
from lxml import etree
from .xml_parser import load_xml
from .schema_inferer import infer_type
from .checksum_generator import get_xml_checksum

NS_MAP = {"xs": "http://www.w3.org/2001/XMLSchema"}

def load_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Warning: Could not load config file {config_path}: {e}")
        return []

def get_optional_fields_for_file(config, xml_file_name):
    for config_entry in config:
        if config_entry.get("file") == xml_file_name:
            return set(config_entry.get("optional_fields", []))
    return set()

def get_allow_null_fields_for_file(config, xml_file_name):
    for config_entry in config:
        if config_entry.get("file") == xml_file_name:
            return set(config_entry.get("allow_null_fields", []))
    return set()

def get_current_element_path(current_path, element_name):
    return ".".join(current_path + [element_name])

def process_element(element, parent, optional_fields, current_path, is_root=False):
    ns = "{http://www.w3.org/2001/XMLSchema}"
    tag = element.tag() if callable(element.tag) else element.tag
    element_name = str(tag).split('}')[-1]

    element_path = get_current_element_path(current_path, element_name)

    element_attrs = {"name": element_name}

    if not is_root:
        if element_path in optional_fields:
            element_attrs["minOccurs"] = "0"
            print(f"🔧 Making element '{element_path}' optional (minOccurs=0)")
        else:
            element_attrs["minOccurs"] = "1"

    element_def = etree.SubElement(parent, f"{ns}element", **element_attrs)

    has_children = len(element) > 0
    has_attributes = len(element.attrib) > 0
    has_text = element.text is not None and element.text.strip() != ""

    if has_children or has_attributes:
        complex_type_attrs = {}
        if has_text:
            complex_type_attrs["mixed"] = "true"

        complex_type = etree.SubElement(element_def, f"{ns}complexType", **complex_type_attrs)
        sequence = etree.SubElement(complex_type, f"{ns}sequence")

        current_path.append(element_name)
        for child in element:
            process_element(child, sequence, optional_fields, current_path, is_root=False)
        current_path.pop()

        for attr_name, attr_value in element.attrib.items():
            attr_type = infer_type(attr_value)
            etree.SubElement(complex_type, f"{ns}attribute", name=attr_name, type=attr_type)
    else:
        element_def.set("type", infer_type(element.text))

def generate_xsd(xml_path, xsd_path, config_path=None):
    config = load_config(config_path) if config_path else []

    xml_file_name = os.path.basename(xml_path)
    optional_fields = get_optional_fields_for_file(config, xml_file_name)
    allow_null_fields = get_allow_null_fields_for_file(config, xml_file_name)

    xml_tree, root = load_xml(xml_path)
    checksum = get_xml_checksum(root, optional_fields, allow_null_fields)
    xsd_file_path = f"{xsd_path}/{checksum}.xsd"

    print(f"📄 XML: {xml_path} | 📁 XSD: {xsd_file_path}")
    if optional_fields:
        print(f"🔧 Optional fields: {list(optional_fields)}")

    try:
        with open(xsd_file_path, "rb") as f:
            existing_schema = etree.parse(f)
            print("✅ Existing schema loaded.")
            return etree.tostring(existing_schema, pretty_print=True, encoding="utf-8").decode()
    except:
        if xml_tree is not None:
            xsd = etree.Element("{http://www.w3.org/2001/XMLSchema}schema", nsmap=NS_MAP)
            process_element(xml_tree.getroot(), xsd, optional_fields, [], is_root=True)

            xsd_str = etree.tostring(xsd, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()
            with open(xsd_file_path, "w", encoding="utf-8") as f:
                f.write(xsd_str)
                print("✅ New schema generated and saved.")
            return xsd_str
        else:
            print("❌ Failed to parse XML.")
            return "Failed to generate XSD schema."