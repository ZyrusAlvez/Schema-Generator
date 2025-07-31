import json
import hashlib

def extract_elements_from_xml(root):
    elements = []

    def recurse(element, path=""):
        tag_raw = element.tag
        tag_text = tag_raw() if callable(tag_raw) else tag_raw
        tag_str = str(tag_text)
        tag_name = tag_str.split('}')[-1] if '}' in tag_str else tag_str

        full_path = f"{path}.{tag_name}" if path else tag_name
        elements.append(full_path)

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
