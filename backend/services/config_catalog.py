SECTION_FIELDS = {
    'limits': [
        'limits/clients', 'limits/sources', 'limits/queue-size', 'limits/client-timeout',
        'limits/header-timeout', 'limits/source-timeout', 'limits/burst-size', 'limits/burst-on-connect'
    ],
    'authentication': [
        'authentication/source-password', 'authentication/relay-user', 'authentication/relay-password',
        'authentication/admin-user', 'authentication/admin-password'
    ],
    'directory': [
        'directory/yp-url-timeout', 'directory/yp-url', 'directory/touch-freq'
    ],
    'server': [
        'hostname', 'location', 'admin', 'fileserve', 'charset', 'mount-default'
    ],
    'listen_sockets': [
        'listen-socket/port', 'listen-socket/ssl', 'listen-socket/bind-address', 'listen-socket/shoutcast-mount'
    ],
    'http_headers': [
        'http-headers/header[name=Cache-Control]', 'http-headers/header[name=Access-Control-Allow-Origin]'
    ],
    'relays': [
        'master-server', 'master-server-port', 'master-update-interval', 'master-password',
        'relays/relay/server', 'relays/relay/port', 'relays/relay/mount', 'relays/relay/local-mount',
        'relays/relay/on-demand', 'relays/relay/relay-shoutcast-metadata', 'relays/relay/relays-on-demand'
    ],
    'paths': [
        'paths/basedir', 'paths/logdir', 'paths/pidfile', 'paths/webroot', 'paths/adminroot',
        'paths/alias/source', 'paths/alias/destination', 'paths/ssl-certificate'
    ],
    'logging': [
        'logging/accesslog', 'logging/errorlog', 'logging/playlistlog', 'logging/loglevel',
        'logging/logsize', 'logging/logarchive'
    ],
    'security': [
        'security/chroot', 'security/changeowner/user', 'security/changeowner/group'
    ],
    'mount_defaults': [
        'mount/default-type', 'mount/dump-file', 'mount/intro', 'mount/hidden',
        'mount/mp3-metadata-interval', 'mount/charset'
    ],
    'listener_auth': [
        'authentication/listener-authentication/type',
        'authentication/listener-authentication/option["mount_add"]',
        'authentication/listener-authentication/option["mount_remove"]',
        'authentication/listener-authentication/option["listener_add"]',
        'authentication/listener-authentication/option["listener_remove"]',
        'authentication/listener-authentication/option["stream_auth"]',
    ],
}
