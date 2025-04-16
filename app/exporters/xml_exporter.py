from typing import Dict, List
import xml.etree.ElementTree as ET
from xml.dom import minidom

class XMLExporter:
    @staticmethod
    def generate_xml(product_data: Dict) -> str:
        """
        Generate XML from product data with proper namespace handling
        """
        # Create root element with namespaces
        root = ET.Element("produkt", {
            "xmlns:g": "http://base.google.com/ns/1.0"
        })

        # Add basic product information
        ET.SubElement(root, "artikelnummer").text = product_data.get("artikelnummer", "")
        ET.SubElement(root, "name").text = product_data.get("name", "")
        
        # Add sizes
        sizes = ", ".join(product_data.get("groessen", []))
        ET.SubElement(root, "groessen").text = sizes

        # Add images
        bilder = ET.SubElement(root, "bilder")
        for img_url in product_data.get("bilder", []):
            ET.SubElement(bilder, "bild").text = img_url

        # Add details with CDATA
        details = ET.SubElement(root, "details")
        details_text = product_data.get("details", "")
        details.text = f"<![CDATA[{details_text}]]>" if details_text else ""

        # Add fit description
        ET.SubElement(root, "passform").text = product_data.get("passform", "")

        # Add category
        if product_data.get("kategorie"):
            ET.SubElement(root, "kategorie").text = product_data.get("kategorie")

        # Add metafields
        metafields = ET.SubElement(root, "metafields")
        meta_data = product_data.get("metafields", {})
        
        # Add all metafields with proper namespace
        for key, value in meta_data.items():
            if key.startswith("meta_google:"):
                # Convert meta_google:key to g:key format
                tag_name = key.replace("meta_google:", "g:")
                ET.SubElement(metafields, tag_name).text = str(value)

        # Convert to string with pretty printing
        xml_str = minidom.parseString(ET.tostring(root, encoding='unicode')).toprettyxml(indent="  ")
        
        # Remove empty lines while keeping indentation
        xml_str = "\n".join([line for line in xml_str.split("\n") if line.strip()])
        
        return xml_str
