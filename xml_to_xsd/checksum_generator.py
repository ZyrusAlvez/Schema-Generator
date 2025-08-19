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

def generate_checksum_from_elements(element_list, optional_fields=None, allow_null_fields=None):
    """
    Generate checksum from elements with config modifications.
    
    Parameters:
    - element_list: List of element paths
    - optional_fields: Set of optional field paths
    - nullable_fields: Set of nullable field paths
    """
    optional_fields = optional_fields or set()
    allow_null_fields = allow_null_fields or set()
    
    # Modify elements based on config
    modified_elements = []
    for element in element_list:
        modified_element = element
        
        # Add "1" suffix if element is optional
        if element in optional_fields:
            modified_element += "1"
            print(element)
        # Add "0" suffix if element is nullable
        if element in allow_null_fields:
            modified_element += "0"
            
        modified_elements.append(modified_element)
    print(modified_elements)
    element_str = json.dumps(sorted(modified_elements), separators=(',', ':'))
    return hashlib.sha256(element_str.encode()).hexdigest()

def get_xml_checksum(root, optional_fields=None, allow_null_fields=None):
    """
    Get XML checksum with optional config modifications.
    
    Parameters:
    - root: XML root element
    - optional_fields: Set of optional field paths
    - nullable_fields: Set of nullable field paths
    """
    elements = extract_elements_from_xml(root)
    return generate_checksum_from_elements(elements, optional_fields, allow_null_fields)