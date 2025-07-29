import json
import hashlib
import os
import xml.etree.ElementTree as ET
from lxml import etree
from collections import defaultdict, Counter
import re
from urllib.parse import urlparse

# === Folders ===
XML_DIR = "xml"
XSD_DIR = "xml_schema"
CONFIG_FILE = "config.json"

os.makedirs(XML_DIR, exist_ok=True)
os.makedirs(XSD_DIR, exist_ok=True)

# === Enhanced Element Analysis ===

class ElementAnalyzer:
    def __init__(self, optional_elements=None):
        self.optional_elements = set(optional_elements or [])
        self.element_stats = defaultdict(lambda: {
            'count': 0,
            'has_text': False,
            'has_children': False,
            'has_attributes': False,
            'attribute_types': defaultdict(set),
            'text_types': set(),
            'child_counts': defaultdict(Counter),
            'paths': set(),
            'parent_paths': set(),
            'is_recursive': False
        })
        self.namespace_map = {}
        self.target_namespace = None
        
    def analyze_xml_structure(self, root, path="", parent_path=""):
        """Deep analysis of XML structure for better XSD generation"""
        # Handle namespaces
        tag_name = self._extract_tag_name(root.tag)
        namespace = self._extract_namespace(root.tag)
        
        if namespace and not self.target_namespace:
            self.target_namespace = namespace
        
        full_path = f"{path}.{tag_name}" if path else tag_name
        
        # Track element statistics
        stats = self.element_stats[tag_name]
        stats['count'] += 1
        stats['paths'].add(full_path)
        if parent_path:
            stats['parent_paths'].add(parent_path)
        
        # Check for recursion (element appears in its own hierarchy)
        if tag_name in path:
            stats['is_recursive'] = True
        
        # Analyze text content
        if root.text and root.text.strip():
            stats['has_text'] = True
            text_type = self._infer_data_type(root.text.strip())
            stats['text_types'].add(text_type)
        
        # Analyze attributes
        if root.attrib:
            stats['has_attributes'] = True
            for attr_name, attr_value in root.attrib.items():
                attr_type = self._infer_data_type(attr_value)
                stats['attribute_types'][attr_name].add(attr_type)
        
        # Analyze children
        if len(root) > 0:
            stats['has_children'] = True
            child_counts = Counter()
            for child in root:
                child_tag = self._extract_tag_name(child.tag)
                child_counts[child_tag] += 1
                # Recursive analysis
                self.analyze_xml_structure(child, full_path, tag_name)
            
            # Update child count statistics
            for child_tag, count in child_counts.items():
                stats['child_counts'][child_tag].update([count])
    
    def _extract_tag_name(self, tag):
        """Extract tag name from namespaced tag"""
        if '}' in tag:
            return tag.split('}')[-1]
        return tag
    
    def _extract_namespace(self, tag):
        """Extract namespace URI from tag"""
        if '}' in tag and tag.startswith('{'):
            return tag[1:tag.find('}')]
        return None
    
    def _infer_data_type(self, value):
        """Enhanced data type inference"""
        if not value or not value.strip():
            return "xs:string"
        
        value = value.strip()
        
        # Boolean
        if value.lower() in ['true', 'false', '1', '0']:
            return "xs:boolean"
        
        # Integer
        try:
            int(value)
            return "xs:integer"
        except ValueError:
            pass
        
        # Decimal/Float
        try:
            float(value)
            return "xs:decimal"
        except ValueError:
            pass
        
        # Date patterns
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO datetime
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, value):
                return "xs:dateTime" if 'T' in value else "xs:date"
        
        # Email
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            return "xs:string"  # Could be custom pattern
        
        # URL
        try:
            result = urlparse(value)
            if result.scheme and result.netloc:
                return "xs:anyURI"
        except:
            pass
        
        return "xs:string"
    
    def get_element_type(self, tag_name):
        """Determine the best XSD type for an element"""
        stats = self.element_stats[tag_name]
        
        # Simple element with only text
        if stats['has_text'] and not stats['has_children'] and not stats['has_attributes']:
            if len(stats['text_types']) == 1:
                return list(stats['text_types'])[0]
            return "xs:string"
        
        # Complex type needed
        return f"{tag_name}Type"
    
    def get_occurrence_constraints(self, parent_tag, child_tag, path):
        """Determine minOccurs and maxOccurs for elements"""
        parent_stats = self.element_stats[parent_tag]
        child_counts = parent_stats['child_counts'][child_tag]
        
        min_occurs = "0" if path in self.optional_elements else "1"
        
        # Determine max occurs from actual usage
        if child_counts:
            max_count = max(child_counts.keys()) if child_counts.keys() else 1
            max_occurs = "unbounded" if max_count > 1 else "1"
        else:
            max_occurs = "1"

        return min_occurs, max_occurs

# === Enhanced XSD Generator ===

class EnhancedXSDGenerator:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.XS_NS = "http://www.w3.org/2001/XMLSchema"
        self.generated_types = set()
        self.global_elements = set()
        
    def generate_xsd(self, root):
        """Generate comprehensive XSD schema"""
        schema = ET.Element("xs:schema")
        schema.set("xmlns:xs", self.XS_NS)
        schema.set("elementFormDefault", "qualified")
        
        # Add target namespace if detected
        if self.analyzer.target_namespace:
            schema.set("targetNamespace", self.analyzer.target_namespace)
            schema.set("xmlns", self.analyzer.target_namespace)
        
        # Generate root element
        root_tag = self.analyzer._extract_tag_name(root.tag)
        root_element = ET.SubElement(schema, "xs:element")
        root_element.set("name", root_tag)
        
        root_type = self.analyzer.get_element_type(root_tag)
        if root_type.endswith("Type"):
            root_element.set("type", root_type)
            self._generate_complex_type(schema, root_tag, root)
        else:
            root_element.set("type", root_type)
        
        return schema
    
    def _generate_complex_type(self, schema, type_name, sample_element):
        """Generate complex type definition with enhanced features"""
        if type_name in self.generated_types:
            return
        
        self.generated_types.add(type_name)
        stats = self.analyzer.element_stats[type_name]
        
        complex_type = ET.SubElement(schema, "xs:complexType")
        complex_type.set("name", f"{type_name}Type")
        
        # Handle mixed content
        if stats['has_text'] and stats['has_children']:
            complex_type.set("mixed", "true")
        
        # Generate content model
        if stats['has_children']:
            self._generate_content_model(schema, complex_type, type_name, sample_element)
        elif stats['has_text'] and stats['has_attributes']:
            # Simple content with attributes
            self._generate_simple_content_with_attributes(complex_type, type_name)
        
        # Add attributes
        if stats['has_attributes']:
            self._generate_attributes(complex_type, type_name, sample_element)
    
    def _generate_content_model(self, schema, complex_type, parent_type, sample_element):
        """Generate sophisticated content model (sequence, choice, etc.)"""
        stats = self.analyzer.element_stats[parent_type]
        
        # Determine if we need sequence or choice based on element patterns
        sequence = ET.SubElement(complex_type, "xs:sequence")
        
        # Group children by tag name and analyze patterns
        children_by_tag = defaultdict(list)
        for child in sample_element:
            child_tag = self.analyzer._extract_tag_name(child.tag)
            children_by_tag[child_tag].append(child)
        
        # Find the parent path by looking at the type name
        parent_path = ""
        for path in stats['paths']:
            if path.endswith(parent_type) or path == parent_type:
                parent_path = path
                break
        
        # Generate element declarations
        for child_tag, child_elements in children_by_tag.items():
            element_elem = ET.SubElement(sequence, "xs:element")
            
            # Handle recursive elements with refs
            child_stats = self.analyzer.element_stats[child_tag]
            if child_stats['is_recursive']:
                element_elem.set("ref", child_tag)
                # Ensure global element exists
                if child_tag not in self.global_elements:
                    self._generate_global_element(schema, child_tag, child_elements[0])
            else:
                element_elem.set("name", child_tag)
                child_type = self.analyzer.get_element_type(child_tag)
                element_elem.set("type", child_type)
                
                # Generate complex type if needed
                if child_type.endswith("Type"):
                    self._generate_complex_type(schema, child_tag, child_elements[0])
            
            # Set occurrence constraints - construct proper path
            if parent_path:
                child_path = f"{parent_path}.{child_tag}"
            else:
                child_path = f"{parent_type}.{child_tag}"
            
            min_occurs, max_occurs = self.analyzer.get_occurrence_constraints(
                parent_type, child_tag, child_path
            )
            
            element_elem.set("minOccurs", min_occurs)
            if max_occurs != "1":
                element_elem.set("maxOccurs", max_occurs)
    
    def _generate_global_element(self, schema, element_name, sample_element):
        """Generate global element for recursive references"""
        if element_name in self.global_elements:
            return
        
        self.global_elements.add(element_name)
        global_elem = ET.SubElement(schema, "xs:element")
        global_elem.set("name", element_name)
        
        element_type = self.analyzer.get_element_type(element_name)
        global_elem.set("type", element_type)
        
        if element_type.endswith("Type") and element_name not in self.generated_types:
            self._generate_complex_type(schema, element_name, sample_element)
    
    def _generate_simple_content_with_attributes(self, complex_type, type_name):
        """Generate simple content with attributes"""
        stats = self.analyzer.element_stats[type_name]
        
        simple_content = ET.SubElement(complex_type, "xs:simpleContent")
        extension = ET.SubElement(simple_content, "xs:extension")
        
        # Determine base type from text content
        if stats['text_types']:
            base_type = list(stats['text_types'])[0] if len(stats['text_types']) == 1 else "xs:string"
        else:
            base_type = "xs:string"
        
        extension.set("base", base_type)
    
    def _generate_attributes(self, parent_element, type_name, sample_element):
        """Generate attribute declarations"""
        stats = self.analyzer.element_stats[type_name]
        
        for attr_name, attr_types in stats['attribute_types'].items():
            attribute = ET.SubElement(parent_element, "xs:attribute")
            attribute.set("name", attr_name)
            
            # Determine attribute type
            if len(attr_types) == 1:
                attr_type = list(attr_types)[0]
            else:
                attr_type = "xs:string"  # Default for mixed types
            
            attribute.set("type", attr_type)
            
            # Determine if attribute is required
            attr_path = f"{type_name}@{attr_name}"
            if attr_path in self.analyzer.optional_elements:
                attribute.set("use", "optional")
            else:
                attribute.set("use", "required")

# === Updated Processing Functions ===

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

def get_xml_checksum(root, filename, configs):
    elements = extract_elements_from_xml(root)
    return generate_checksum_from_elements(elements)

def enhanced_xml_to_xsd(root, optional_elements=None):
    """Enhanced XML to XSD conversion with better complex structure handling"""
    analyzer = ElementAnalyzer(optional_elements)
    analyzer.analyze_xml_structure(root)
    
    generator = EnhancedXSDGenerator(analyzer)
    return generator.generate_xsd(root)

def xml_validator(xml_file_path, xml_schema):
    """Validate XML against XSD schema"""
    try:
        # Parse XSD
        xsd_doc = etree.fromstring(ET.tostring(xml_schema))
        schema = etree.XMLSchema(xsd_doc)
        
        # Parse XML
        xml_doc = etree.parse(xml_file_path)
        
        # Validate
        if schema.validate(xml_doc):
            return True
        else:
            print("❌ XML validation failed:\n")
            for error in schema.error_log:
                print(f"Line {error.line}: {error.message}")
            return False
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

# === Debug Helper Functions ===

def debug_xml_structure(root, path="", level=0):
    """Debug function to show XML structure and paths"""
    tag_name = root.tag.split('}')[-1] if '}' in root.tag else root.tag
    full_path = f"{path}.{tag_name}" if path else tag_name
    
    indent = "  " * level
    print(f"{indent}{full_path}")
    
    # Show attributes
    for attr_name in root.attrib:
        attr_path = f"{full_path}@{attr_name}"
        print(f"{indent}  └─ {attr_path}")
    
    # Recurse through children
    for child in root:
        debug_xml_structure(child, full_path, level + 1)

# === Configuration Helper ===

def load_config():
    """Load configuration file if it exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  Warning: Could not load config file - {e}")
    return []

def get_file_config(filename, configs):
    """Get configuration for a specific file"""
    for config in configs:
        if config.get("file") == filename:
            return config
    return {}

def normalize_config(file_config):
    """Normalize config keys to handle both optional_fields and optional_elements"""
    normalized = {}
    
    # Handle optional elements/fields - support both naming conventions
    optional_elements = []
    if "optional_elements" in file_config:
        optional_elements.extend(file_config["optional_elements"])
    if "optional_fields" in file_config:
        optional_elements.extend(file_config["optional_fields"])
    
    normalized["optional_elements"] = optional_elements
    
    # Handle allow_null_fields
    normalized["allow_null_fields"] = file_config.get("allow_null_fields", [])
    
    return normalized

# === File Processing ===

def process_xml_file(filename, configs):
    xml_file_path = os.path.join(XML_DIR, filename)
    
    # Get configuration for this file
    file_config = get_file_config(filename, configs)
    normalized_config = normalize_config(file_config)
    optional_elements = normalized_config.get("optional_elements", [])
    
    # Load XML
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"❌ Invalid XML in {xml_file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {xml_file_path}: {e}")
        return False
    
    # Generate checksum
    checksum_id = get_xml_checksum(root, filename, configs)
    print(f"🔧 Generated checksum: {checksum_id}")
    
    # Schema file path based on checksum ID
    xsd_file_path = os.path.join(XSD_DIR, f"{checksum_id}.xsd")
    
    # Force regeneration if config has optional elements but schema doesn't exist or is different
    force_regenerate = False
    if optional_elements and os.path.exists(xsd_file_path):
        force_regenerate = True
    
    try:
        # Try to load existing schema only if not forcing regeneration
        if not force_regenerate:
            existing_schema_tree = ET.parse(xsd_file_path)
            existing_schema = existing_schema_tree.getroot()
            
            # Validate XML against existing schema
            if xml_validator(xml_file_path, existing_schema):
                print(f"✅ {filename} validated against existing schema")
                return True
            else:
                print(f"❌ {filename} failed validation against existing schema")
        else:
            raise FileNotFoundError("Forcing regeneration")
            
    except (ET.ParseError, FileNotFoundError):
        # Generate new schema using enhanced generator
        print(f"📝 Generating new XSD schema for {filename}")
        xml_schema = enhanced_xml_to_xsd(root, optional_elements)
        
        # Add checksum as comment
        comment = ET.Comment(f" Generated schema with checksum: {checksum_id} ")
        xml_schema.insert(0, comment)
        
        # Save new schema with checksum ID as filename
        try:
            # Register namespace for proper formatting
            ET.register_namespace('xs', 'http://www.w3.org/2001/XMLSchema')
            
            # Convert to string and reparse for proper formatting
            rough_string = ET.tostring(xml_schema, encoding='unicode')
            
            # Use minidom for pretty printing
            try:
                from xml.dom import minidom
                # Parse the string to create a proper DOM
                dom = minidom.parseString(rough_string)
                # Get pretty printed version
                pretty_xml = dom.toprettyxml(indent="  ", encoding=None)
                # Remove extra blank lines
                pretty_lines = [line for line in pretty_xml.split('\n') if line.strip()]
                pretty_xml = '\n'.join(pretty_lines)
                
                with open(xsd_file_path, "w", encoding="utf-8") as f:
                    f.write(pretty_xml)
            except Exception as e:
                print(f"Warning: Could not pretty print XSD: {e}")
                # Fallback to basic formatting
                with open(xsd_file_path, "w", encoding="utf-8") as f:
                    f.write(rough_string)
                    
            print(f"💾 Saved schema to {xsd_file_path}")
            
        except Exception as e:
            print(f"❌ Error saving schema: {e}")
            return False
        
        # Validate XML against new schema
        if xml_validator(xml_file_path, xml_schema):
            print(f"✅ {filename} validated against new schema")
            return True
        else:
            print(f"❌ {filename} failed validation against new schema")
            return False

# === Main Logic ===

def main():
    
    # Load configurations
    configs = load_config()
    
    # Get all XML files in the xml directory
    xml_files = []
    if os.path.exists(XML_DIR):
        for file in os.listdir(XML_DIR):
            if file.endswith('.xml'):
                xml_files.append(file)
    
    if not xml_files:
        print(f"❌ No XML files found in {XML_DIR} directory")
        return
    
    print(f"📋 Found {len(xml_files)} XML files to process")
    
    success_count = 0
    for filename in xml_files:
        print(f"\n🔄 Processing {filename}...")
        if process_xml_file(filename, configs):
            success_count += 1
    
    print(f"\n✅ Successfully processed {success_count}/{len(xml_files)} XML files")

# === Run ===

if __name__ == "__main__":
    main()