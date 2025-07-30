from lxml import etree

def xml_validator(xml_path, xsd_str):
    try:
        xsd_doc = etree.fromstring(xsd_str.encode())
        schema = etree.XMLSchema(xsd_doc)
        xml_doc = etree.parse(xml_path)
        schema.assertValid(xml_doc)
        return True
    except etree.DocumentInvalid as e:
        print("Validation failed:", e)
        return False
    except Exception as e:
        print("Error:", e)
        return False