import json
import os
from lxml import etree
from .xml_parser import load_xml
from .schema_inferer import infer_type
from .checksum_generator import get_xml_checksum

class XSDGenerator:
    def __init__(self, config_path=None):
        self.ns_map = {"xs": "http://www.w3.org/2001/XMLSchema"}
        self.xsd = None
        self.config = self.load_config(config_path) if config_path else []
        self.optional_fields = set()
        self.current_path = []

    def load_config(self, config_path):
        """
        Loads the configuration file for optional fields.
        
        Parameters:
        - config_path (str): Path to the JSON config file
        
        Returns:
        - list: Configuration data
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️  Warning: Could not load config file {config_path}: {e}")
            return []

    def get_optional_fields_for_file(self, xml_file_name):
        """
        Gets the optional fields configuration for a specific file.
        
        Parameters:
        - xml_file_name (str): Name of the XML file
        
        Returns:
        - set: Set of optional field paths
        """
        for config_entry in self.config:
            if config_entry.get("file") == xml_file_name:
                return set(config_entry.get("optional_fields", []))
        return set()
    
    def get_allow_null_fields_for_file(self, xml_file_name):
        """
        Gets the optional fields configuration for a specific file.
        
        Parameters:
        - xml_file_name (str): Name of the XML file
        
        Returns:
        - set: Set of optional field paths
        """
        for config_entry in self.config:
            if config_entry.get("file") == xml_file_name:
                return set(config_entry.get("allow_null_fields", []))
        return set()

    def generate_xsd(self, xml_path, xsd_path):
        """
        Generates an XSD schema for the given XML file.

        Parameters:
        - xml_path (str): Path to the XML file.
        - xsd_path (str): Folder directory where the XSD file will be written
        """

        # Get the XML file name for config lookup
        xml_file_name = os.path.basename(xml_path)
        self.optional_fields = self.get_optional_fields_for_file(xml_file_name)
        self.get_allow_null_fields = self.get_allow_null_fields_for_file(xml_file_name)

        xml_tree, root = load_xml(xml_path)
        checksum = get_xml_checksum(root, self.optional_fields, self.get_allow_null_fields)
        xsd_file_path = f"{xsd_path}/{checksum}.xsd"
        
        print(f"📄 XML: {xml_path} | 📁 XSD: {xsd_file_path}")
        if self.optional_fields:
            print(f"🔧 Optional fields: {list(self.optional_fields)}")

        try:
            with open(f"{xsd_path}/{checksum}.xsd", "rb") as f:
                existing_schema = etree.parse(f)
                print("✅ Existing schema loaded.")
                return etree.tostring(existing_schema, pretty_print=True, encoding="utf-8").decode()
        except:
            if xml_tree is not None:
                self.xsd = etree.Element("{http://www.w3.org/2001/XMLSchema}schema", nsmap=self.ns_map)
                # Reset path tracking
                self.current_path = []
                # Process root element without minOccurs
                self.process_element(xml_tree.getroot(), self.xsd, is_root=True)
                
                xsd_str = etree.tostring(self.xsd, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()

                with open(xsd_file_path, "w", encoding="utf-8") as f:
                    f.write(xsd_str)
                    print("✅ New schema generated and saved.")

                return xsd_str
            else:
                print("❌ Failed to parse XML.")
                return "Failed to generate XSD schema."

    def get_current_element_path(self, element_name):
        """
        Gets the current element path for checking against optional fields.
        
        Parameters:
        - element_name (str): Name of the current element
        
        Returns:
        - str: Dot-separated path to the element
        """
        return ".".join(self.current_path + [element_name])

    def process_element(self, element, parent, is_root=False):
        """
        Recursively processes an XML element to generate its XSD representation.

        Parameters:
        - element (etree.Element): The current XML element.
        - parent (etree.Element): The parent element in the XSD schema.
        - is_root (bool): Whether this is the root element (xml/retxml)
        """
        ns = "{http://www.w3.org/2001/XMLSchema}"
        tag = element.tag() if callable(element.tag) else element.tag
        element_name = str(tag).split('}')[-1]
        
        # Get the full path to this element
        element_path = self.get_current_element_path(element_name)
        print(element_path)
        # Create element attributes dictionary
        element_attrs = {"name": element_name}
        
        # Determine minOccurs value
        if is_root:
            # Root elements don't get minOccurs
            pass

        
        elif element_path in self.optional_fields:
            # Element is marked as optional in config
            element_attrs["minOccurs"] = "0"
            print(f"🔧 Making element '{element_path}' optional (minOccurs=0)")
        else:
            # Default: required element
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
            
            # Update current path for child processing
            self.current_path.append(element_name)
            
            # Process child elements (all children are non-root, so is_root=False)
            for child in element:
                self.process_element(child, sequence, is_root=False)
            
            # Remove current element from path after processing children
            self.current_path.pop()

            for attr_name, attr_value in element.attrib.items():
                attr_type = infer_type(attr_value)
                etree.SubElement(complex_type, f"{ns}attribute", name=attr_name, type=attr_type)
        else:
            element_def.set("type", infer_type(element.text))