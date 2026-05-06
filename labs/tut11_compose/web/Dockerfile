# web/Dockerfile
FROM nginx:1.27.1-alpine@sha256:6a2f8b28e45c4adea04ec207a251fd4a2df03ddc930f782af51e315ebc76e9a9

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html

# nginx images already define HEALTHCHECK-friendly behaviour via default port 80,
# but adding an explicit one documents intent.
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD wget -q -O- http://localhost/ >/dev/null || exit 1
