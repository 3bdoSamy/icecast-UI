from fastapi import HTTPException
from services.xml_editor import IcecastXmlEditor
from services import nginx_manager, icecast_controller

editor = IcecastXmlEditor()


def runtime_endpoints(settings: dict | None = None) -> dict:
    cfg = settings or nginx_manager.get_settings()
    scheme = 'https' if cfg.get('https_enabled') else 'http'
    domain = cfg.get('domain') or 'localhost'
    port = int(cfg.get('icecast_port', 8000))
    return {
        'frontend_api_base_url': f'{scheme}://{domain}/api',
        'stream_base_url': f'{scheme}://{domain}',
        'status_json_endpoint_public': f'{scheme}://{domain}/status-json.xsl',
        'status_json_endpoint_local': f'http://127.0.0.1:{port}/status-json.xsl',
        'icecast_port': port,
    }


def sync_services(domain: str, icecast_port: int, https_enabled: bool, ssl_mode: str, cloudflare_enabled: bool) -> dict:
    backup = editor.backup()

    editor.set_value('listen-socket/port', str(icecast_port))
    xml_validation = editor.validate()
    if not xml_validation['valid']:
        raise HTTPException(status_code=400, detail={'message': 'icecast.xml validation failed', 'backup': backup, 'validation': xml_validation})

    settings = nginx_manager.save_settings({
        'domain': domain,
        'icecast_port': icecast_port,
        'https_enabled': https_enabled,
        'ssl_mode': ssl_mode,
        'cloudflare_enabled': cloudflare_enabled,
    })

    nginx_result = nginx_manager.apply_nginx_config(settings)
    if not nginx_result.get('ok'):
        raise HTTPException(status_code=400, detail={'message': 'nginx configuration failed', 'backup': backup, 'nginx': nginx_result})

    icecast_result = icecast_controller.restart_icecast()

    return {
        'status': 'synced',
        'backup': backup,
        'icecast_xml': xml_validation,
        'nginx': nginx_result,
        'icecast_restart': icecast_result,
        'runtime_endpoints': runtime_endpoints(settings),
    }
