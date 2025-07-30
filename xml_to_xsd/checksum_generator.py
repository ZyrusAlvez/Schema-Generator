import json
import hashlib

def extract_elements_from_xml(root):
    elements = []

    def recurse(element, path=""):
        tag_name = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        full_path = f"{path}.{tag_name}" if path else tag_name

        elements.append(full_path)  # capture tag path

        for attr_name in sorted(element.attrib.keys()):
            attr_path = f"{full_path}@{attr_name}"
            elements.append(attr_path)

        for child in element:
            recurse(child, full_path)

    recurse(root)
    return elements


def generate_checksum_from_elements(element_list):
    element_str = json.dumps(sorted(element_list), separators=(',', ':'))
    return hashlib.sha256(element_str.encode()).hexdigest()

def get_xml_checksum(root):
    elements = extract_elements_from_xml(root)
    return generate_checksum_from_elements(elements)
