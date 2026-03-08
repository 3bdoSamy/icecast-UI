import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from lxml import etree

ICECAST_XML = Path('/usr/local/etc/icecast.xml')
BACKUP_DIR = Path('/usr/local/etc/icecast-backups')
import subprocess
from pathlib import Path
from lxml import etree

ICECAST_XML = Path("/data/icecast/icecast.xml")


class IcecastXmlEditor:
    def __init__(self, xml_path: Path = ICECAST_XML):
        self.xml_path = xml_path

    def load_tree(self):
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.parse(str(self.xml_path), parser)

    def read_xml(self) -> str:
        return self.xml_path.read_text(encoding='utf-8')

    def backup(self) -> str:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        backup_path = BACKUP_DIR / f'icecast-{ts}.xml'
        shutil.copy2(self.xml_path, backup_path)
        return str(backup_path)

    def _ensure_path(self, root: etree._Element, path: str):
        node = root
        for part in [p for p in path.strip('/').split('/') if p]:
            child = node.find(part)
            if child is None:
                child = etree.SubElement(node, part)
            node = child
        return node

    def set_value(self, xpath: str, value: str):
        tree = self.load_tree()
        root = tree.getroot()
        if xpath.startswith('/icecast/'):
            xpath = xpath.replace('/icecast/', '', 1)
        node = tree.xpath(f'/icecast/{xpath}')
        target = node[0] if node else self._ensure_path(root, xpath)
        target.text = value
        tree.write(str(self.xml_path), pretty_print=True, encoding='utf-8', xml_declaration=True)

    def upsert_mount(self, mount_name: str, values: dict):
        tree = self.load_tree()
        root = tree.getroot()
        mounts = root.find('mounts') or etree.SubElement(root, 'mounts')
        mount_node = None
        for m in mounts.findall('mount'):
            if m.get('type') == 'normal' and m.get('mount-name') == mount_name:
                mount_node = m
                break
        if mount_node is None:
            mount_node = etree.SubElement(mounts, 'mount')
            mount_node.set('type', 'normal')
            mount_node.set('mount-name', mount_name)

        for k, v in values.items():
            if v is None:
                continue
            c = mount_node.find(k)
            if c is None:
                c = etree.SubElement(mount_node, k)
            c.text = str(v)

        tree.write(str(self.xml_path), pretty_print=True, encoding='utf-8', xml_declaration=True)

    def delete_mount(self, mount_name: str):
        tree = self.load_tree()
        root = tree.getroot()
        mounts = root.find('mounts')
        if mounts is None:
            return
        for m in list(mounts.findall('mount')):
            if m.get('mount-name') == mount_name:
                mounts.remove(m)
        tree.write(str(self.xml_path), pretty_print=True, encoding='utf-8', xml_declaration=True)

    def validate(self):
        proc = subprocess.run(['xmllint', '--noout', str(self.xml_path)], capture_output=True, text=True)
        return {'valid': proc.returncode == 0, 'output': proc.stderr or 'XML is valid'}

    def backup_and_validate(self):
        backup = self.backup()
        valid = self.validate()
        return {'backup': backup, **valid}
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
