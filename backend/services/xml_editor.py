import subprocess
from pathlib import Path
from lxml import etree

ICECAST_XML = Path("/usr/local/etc/icecast.xml")


class IcecastXmlEditor:
    def __init__(self, xml_path: Path = ICECAST_XML):
        self.xml_path = xml_path

    def load_tree(self):
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.parse(str(self.xml_path), parser)

    def read_xml(self) -> str:
        return self.xml_path.read_text(encoding="utf-8")

    def write_xml(self, xml_content: str):
        self.xml_path.write_text(xml_content, encoding="utf-8")

    def update_value(self, xpath: str, value: str):
        tree = self.load_tree()
        node = tree.xpath(xpath)
        if not node:
            raise ValueError(f"XPath not found: {xpath}")
        node[0].text = value
        tree.write(str(self.xml_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

    def validate(self):
        proc = subprocess.run(["xmllint", "--noout", str(self.xml_path)], capture_output=True, text=True)
        return {"valid": proc.returncode == 0, "output": proc.stderr or "XML is valid"}
