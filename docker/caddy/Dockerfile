FROM abiosoft/caddy:1.0.3

RUN mkdir -p /srv/www \
    /srv/caddy

WORKDIR /srv/caddy

ARG MKCERT_VERSION=1.4.1
RUN wget -O /usr/local/bin/mkcert https://github.com/FiloSottile/mkcert/releases/download/v${MKCERT_VERSION}/mkcert-v${MKCERT_VERSION}-linux-amd64
RUN chmod +x /usr/local/bin/mkcert

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["/bin/parent", "caddy", "--log", "stdout", "--agree=$ACME_AGREE"]
