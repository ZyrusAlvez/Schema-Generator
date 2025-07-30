from lxml import etree

def load_xml(xml_path):
    """
    Loads and parses an XML file.

    Parameters:
    - xml_path (str): The path to the XML file to be loaded.

    Returns:
    - etree.ElementTree: The parsed XML tree, or None if an error occurs.
    """
    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()
        return tree, root
    except (etree.XMLSyntaxError, FileNotFoundError) as e:
        print(f"Failed to load or parse XML file: {e}")
        return None