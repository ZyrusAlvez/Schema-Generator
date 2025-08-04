from lxml import etree
from .xml_parser import load_xml
from .schema_inferer import infer_type
from .checksum_generator import get_xml_checksum

class XSDGenerator:
    def __init__(self):
        self.ns_map = {"xs": "http://www.w3.org/2001/XMLSchema"}
        self.xsd = None

    def generate_xsd(self, xml_path, xsd_path):
        """
        Generates an XSD schema for the given XML file.

        Parameters:
        - xml_path (str): Path to the XML file.
        - xsd_path (str): Folder directory where the XSD file will be written
        """
        xml_tree, root = load_xml(xml_path)
        checksum = get_xml_checksum(root)
        xsd_file_path = f"{xsd_path}/{checksum}.xsd"
        print(f"📄 XML: {xml_path} | 📁 XSD: {xsd_file_path}")

        try:
            with open(f"{xsd_path}/{checksum}", "rb") as f:
                existing_schema = etree.parse(f)
                print("✅ Existing schema loaded.")
                return existing_schema
        except:
            if xml_tree is not None:
                self.xsd = etree.Element("{http://www.w3.org/2001/XMLSchema}schema", nsmap=self.ns_map)
                self.process_element(xml_tree.getroot(), self.xsd)
                
                xsd_str = etree.tostring(self.xsd, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()

                with open(xsd_file_path, "w", encoding="utf-8") as f:
                    f.write(xsd_str)
                    print("✅ New schema generated and saved.")

                return xsd_str
            else:
                print("❌ Failed to parse XML.")
                return "Failed to generate XSD schema."

    def process_element(self, element, parent):
        """
        Recursively processes an XML element to generate its XSD representation.

        Parameters:
        - element (etree.Element): The current XML element.
        - parent (etree.Element): The parent element in the XSD schema.
        """
        ns = "{http://www.w3.org/2001/XMLSchema}"
        tag = element.tag() if callable(element.tag) else element.tag
        element_name = str(tag).split('}')[-1]
        element_def = etree.SubElement(parent, f"{ns}element", name=element_name)

        has_children = len(element) > 0
        has_attributes = len(element.attrib) > 0
        has_text = element.text is not None and element.text.strip() != ""

        if has_children or has_attributes:
            complex_type_attrs = {}
            if has_text:
                complex_type_attrs["mixed"] = "true"

            complex_type = etree.SubElement(element_def, f"{ns}complexType", **complex_type_attrs)
            sequence = etree.SubElement(complex_type, f"{ns}sequence")
            
            for child in element:
                self.process_element(child, sequence)

            for attr_name, attr_value in element.attrib.items():
                attr_type = infer_type(attr_value)
                etree.SubElement(complex_type, f"{ns}attribute", name=attr_name, type=attr_type)
        else:
            element_def.set("type", infer_type(element.text))