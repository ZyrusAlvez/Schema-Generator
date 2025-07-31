import json
import os
from lxml import etree

# Generate countless JSON files
for i in range(100):  # change to while True for truly endless
    data = {
        "id": i,
        "name": f"Item {i}",
        "active": i % 2 == 0
    }
    with open(f"files/json/file_{i}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# # Generate countless XML files
# for i in range(1, 10001):  # change to while True for truly endless
#     root = etree.Element("item")
#     etree.SubElement(root, "id").text = str(i)
#     etree.SubElement(root, "name").text = f"Item {i}"
#     etree.SubElement(root, "active").text = str(i % 2 == 0).lower()

#     tree = etree.ElementTree(root)
#     tree.write(f"output/xml/file_{i}.xml", pretty_print=True, xml_declaration=True, encoding="utf-8")
#     print(f"✅ XML file_{i}.xml created")