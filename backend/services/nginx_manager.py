import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

SETTINGS_PATH = Path('/data/control/nginx_settings.json')
TEMPLATE_PATH = Path('/data/control/templates/icecast.conf.tpl')
OUTPUT_PATH = Path('/etc/nginx/conf.d/icecast.conf')
CERT_DIR = Path('/etc/ssl/certs')
KEY_DIR = Path('/etc/ssl/private')
BACKUP_DIR = Path('/etc/nginx/backups')

DEFAULT_SETTINGS = {
    'domain': 'localhost',
    'https_enabled': False,
    'ssl_mode': 'none',
    'cloudflare_enabled': False,
    'icecast_port': 8000,
}


def _run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {'ok': proc.returncode == 0, 'stdout': proc.stdout.strip(), 'stderr': proc.stderr.strip()}


def get_settings() -> dict:
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding='utf-8')
        return DEFAULT_SETTINGS
    return json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))


def save_settings(settings: dict) -> dict:
    merged = {**DEFAULT_SETTINGS, **settings}
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(merged, indent=2), encoding='utf-8')
    return merged


def render_config(settings: dict) -> str:
    template = TEMPLATE_PATH.read_text(encoding='utf-8')
    return (
        template.replace('{{DOMAIN}}', settings['domain'])
        .replace('{{ICECAST_PORT}}', str(settings['icecast_port']))
        .replace('{{HTTPS_BLOCK}}', _https_block(settings))
        .replace('{{CLOUDFLARE_REAL_IP}}', _cloudflare_real_ip(settings['cloudflare_enabled']))
    )


def _https_block(settings: dict) -> str:
    if not settings.get('https_enabled'):
        return ''

    cert_path, key_path = '/etc/ssl/certs/custom.pem', '/etc/ssl/private/custom.key'
    if settings.get('ssl_mode') == 'cloudflare':
        cert_path, key_path = '/etc/ssl/certs/cloudflare-origin.pem', '/etc/ssl/private/cloudflare-origin.key'
    elif settings.get('ssl_mode') == 'letsencrypt':
        d = settings['domain']
        cert_path = f'/etc/letsencrypt/live/{d}/fullchain.pem'
        key_path = f'/etc/letsencrypt/live/{d}/privkey.pem'

    return f'''
server {{
    listen 443 ssl http2;
    server_name {settings['domain']};
    ssl_certificate {cert_path};
    ssl_certificate_key {key_path};

    proxy_buffering off;
    proxy_request_buffering off;
    proxy_set_header Accept-Encoding "";

    location / {{
        proxy_pass http://127.0.0.1:{settings['icecast_port']};
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;
        sub_filter_once off;
        sub_filter ':8000/' '/';
        sub_filter '@localhost' '@{settings['domain']}';
        sub_filter 'localhost' '{settings['domain']}';

        more_clear_headers Server;
        more_clear_headers X-Powered-By;
        more_set_headers "Cache-Control: no-store";
    }}
}}
'''


def _cloudflare_real_ip(enabled: bool) -> str:
    if not enabled:
        return ''
    ranges = [
        '173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22',
        '141.101.64.0/18', '108.162.192.0/18', '190.93.240.0/20', '188.114.96.0/20',
        '197.234.240.0/22', '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/13',
        '104.24.0.0/14', '172.64.0.0/13', '131.0.72.0/22'
    ]
    lines = ['real_ip_header CF-Connecting-IP;'] + [f'set_real_ip_from {r};' for r in ranges]
    return '\n    '.join(lines)




def backup_nginx_config() -> str:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    target = BACKUP_DIR / f'icecast-{ts}.conf'
    if OUTPUT_PATH.exists():
        shutil.copy2(OUTPUT_PATH, target)
    else:
        target.write_text('', encoding='utf-8')
    return str(target)

def apply_nginx_config(settings: dict) -> dict:
    backup = backup_nginx_config()
    rendered = render_config(settings)
    OUTPUT_PATH.write_text(rendered, encoding='utf-8')
    test = _run(['nginx', '-t'])
    if not test['ok']:
        return {'ok': False, 'step': 'nginx -t', **test}
    reload_res = _run(['systemctl', 'reload', 'nginx'])
    return {'ok': reload_res['ok'], 'backup': backup, 'config_path': str(OUTPUT_PATH), 'test': test, 'reload': reload_res}


def nginx_restart():
    return _run(['systemctl', 'restart', 'nginx'])


def nginx_reload():
    return _run(['systemctl', 'reload', 'nginx'])


def nginx_test():
    return _run(['nginx', '-t'])


def run_certbot(domain: str):
    return _run(['certbot', '--nginx', '-d', domain, '--non-interactive', '--agree-tos', '-m', f'admin@{domain}'])


def save_cloudflare_cert(cert_pem: str, key_pem: str):
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    (CERT_DIR / 'cloudflare-origin.pem').write_text(cert_pem, encoding='utf-8')
    (KEY_DIR / 'cloudflare-origin.key').write_text(key_pem, encoding='utf-8')


def save_custom_cert(cert_pem: str, key_pem: str):
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    (CERT_DIR / 'custom.pem').write_text(cert_pem, encoding='utf-8')
    (KEY_DIR / 'custom.key').write_text(key_pem, encoding='utf-8')
