server {
    listen 80;
    server_name {{DOMAIN}};

    {{CLOUDFLARE_REAL_IP}}

    location / {
        proxy_pass http://127.0.0.1:{{ICECAST_PORT}};
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_buffering off;
        proxy_request_buffering off;
        proxy_set_header Accept-Encoding "";

        sub_filter_once off;
        sub_filter ':8000/' '/';
        sub_filter '@localhost' '@{{DOMAIN}}';
        sub_filter 'localhost' '{{DOMAIN}}';

        more_clear_headers Server;
        more_clear_headers X-Powered-By;
        more_set_headers "Cache-Control: no-store";
    }
}

server {
    listen 80;
    server_name {{DOMAIN}};
    return 301 https://$host$request_uri;
}

{{HTTPS_BLOCK}}
