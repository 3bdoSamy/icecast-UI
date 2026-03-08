import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from lxml import etree

ICECAST_XML = Path('/usr/local/etc/icecast.xml')
BACKUP_DIR = Path('/etc/icecast/backups')


class IcecastXmlEditor:
    def __init__(self, xml_path: Path = ICECAST_XML):
        self.xml_path = xml_path

    def load_tree(self):
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.parse(str(self.xml_path), parser)

    def _write_tree(self, tree):
        tree.write(str(self.xml_path), pretty_print=True, encoding='utf-8', xml_declaration=True)

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
        self._write_tree(tree)

    def set_values(self, updates: list[tuple[str, str]]):
        for xpath, value in updates:
            self.set_value(xpath, value)

    def upsert_mount(self, mount_name: str, values: dict):
        tree = self.load_tree()
        root = tree.getroot()
        mounts = root.find('mounts') or etree.SubElement(root, 'mounts')
        mount_node = None
        for m in mounts.findall('mount'):
            key = m.get('mount-name') or (m.findtext('mount-name') or '')
            if key == mount_name:
                mount_node = m
                break
        if mount_node is None:
            mount_node = etree.SubElement(mounts, 'mount')
            etree.SubElement(mount_node, 'mount-name').text = mount_name

        for k, v in values.items():
            if v is None:
                continue
            c = mount_node.find(k)
            if c is None:
                c = etree.SubElement(mount_node, k)
            c.text = str(v)

        self._write_tree(tree)

    def delete_mount(self, mount_name: str):
        tree = self.load_tree()
        root = tree.getroot()
        mounts = root.find('mounts')
        if mounts is None:
            return
        for m in list(mounts.findall('mount')):
            key = m.get('mount-name') or (m.findtext('mount-name') or '')
            if key == mount_name:
                mounts.remove(m)
        self._write_tree(tree)

    def list_sockets(self):
        tree = self.load_tree()
        root = tree.getroot()
        out = []
        for idx, node in enumerate(root.findall('listen-socket')):
            out.append({
                'id': idx,
                'port': node.findtext('port', ''),
                'bind-address': node.findtext('bind-address', ''),
                'ssl': node.findtext('ssl', '0'),
                'shoutcast-mount': node.findtext('shoutcast-mount', ''),
            })
        return out

    def add_socket(self, payload: dict):
        tree = self.load_tree()
        root = tree.getroot()
        s = etree.SubElement(root, 'listen-socket')
        for k in ['port', 'bind-address', 'ssl', 'shoutcast-mount']:
            if payload.get(k) is not None:
                etree.SubElement(s, k).text = str(payload[k])
        self._write_tree(tree)

    def update_socket(self, socket_id: int, payload: dict):
        tree = self.load_tree()
        root = tree.getroot()
        sockets = root.findall('listen-socket')
        node = sockets[socket_id]
        for k in ['port', 'bind-address', 'ssl', 'shoutcast-mount']:
            if payload.get(k) is None:
                continue
            child = node.find(k)
            if child is None:
                child = etree.SubElement(node, k)
            child.text = str(payload[k])
        self._write_tree(tree)

    def delete_socket(self, socket_id: int):
        tree = self.load_tree()
        root = tree.getroot()
        sockets = root.findall('listen-socket')
        root.remove(sockets[socket_id])
        self._write_tree(tree)

    def get_relays(self):
        tree = self.load_tree()
        root = tree.getroot()
        relays = []
        relays_node = root.find('relays')
        if relays_node is not None:
            for idx, relay in enumerate(relays_node.findall('relay')):
                relays.append({
                    'id': idx,
                    'server': relay.findtext('server', ''),
                    'port': relay.findtext('port', ''),
                    'mount': relay.findtext('mount', ''),
                    'local-mount': relay.findtext('local-mount', ''),
                    'username': relay.findtext('username', ''),
                    'password': relay.findtext('password', ''),
                    'relay-shoutcast-metadata': relay.findtext('relay-shoutcast-metadata', '0'),
                    'on-demand': relay.findtext('on-demand', '0'),
                })
        master = {
            'master-server': root.findtext('master-server', ''),
            'master-server-port': root.findtext('master-server-port', ''),
            'master-update-interval': root.findtext('master-update-interval', ''),
            'master-password': root.findtext('master-password', ''),
            'relays-on-demand': root.findtext('relays-on-demand', ''),
        }
        return {'master': master, 'specific': relays}

    def set_master_relay(self, payload: dict):
        updates = [
            ('master-server', payload.get('master-server', '')),
            ('master-server-port', str(payload.get('master-server-port', ''))),
            ('master-update-interval', str(payload.get('master-update-interval', ''))),
            ('master-password', payload.get('master-password', '')),
            ('relays-on-demand', str(payload.get('relays-on-demand', ''))),
        ]
        self.set_values([(k, v) for k, v in updates if v != ''])

    def add_specific_relay(self, payload: dict):
        tree = self.load_tree()
        root = tree.getroot()
        relays = root.find('relays') or etree.SubElement(root, 'relays')
        relay = etree.SubElement(relays, 'relay')
        for k in ['server', 'port', 'mount', 'local-mount', 'username', 'password', 'relay-shoutcast-metadata', 'on-demand']:
            if payload.get(k) is not None:
                etree.SubElement(relay, k).text = str(payload[k])
        self._write_tree(tree)

    def update_specific_relay(self, relay_id: int, payload: dict):
        tree = self.load_tree()
        root = tree.getroot()
        relays = (root.find('relays') or etree.SubElement(root, 'relays')).findall('relay')
        relay = relays[relay_id]
        for k in ['server', 'port', 'mount', 'local-mount', 'username', 'password', 'relay-shoutcast-metadata', 'on-demand']:
            if payload.get(k) is None:
                continue
            c = relay.find(k)
            if c is None:
                c = etree.SubElement(relay, k)
            c.text = str(payload[k])
        self._write_tree(tree)

    def delete_specific_relay(self, relay_id: int):
        tree = self.load_tree()
        root = tree.getroot()
        relays_node = root.find('relays')
        if relays_node is None:
            return
        relays = relays_node.findall('relay')
        relays_node.remove(relays[relay_id])
        self._write_tree(tree)

    def validate(self):
        proc = subprocess.run(['xmllint', '--noout', str(self.xml_path)], capture_output=True, text=True)
        return {'valid': proc.returncode == 0, 'output': proc.stderr or 'XML is valid'}

    def backup_and_validate(self):
        backup = self.backup()
        valid = self.validate()
        return {'backup': backup, **valid}
