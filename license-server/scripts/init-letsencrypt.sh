#!/bin/bash
# One-time bootstrap for Nginx + Let's Encrypt (certbot, webroot mode).
#
# Nginx won't start with the SSL server block in nginx.conf until a real
# certificate file exists at the path it references, but certbot can't issue
# a certificate until Nginx is up to serve the HTTP-01 challenge — this
# script breaks that chicken-and-egg loop the standard way: start Nginx with
# a throwaway self-signed cert, request the real one, then reload.
#
# Run this once from the license-server/ directory, after editing DOMAIN and
# EMAIL below (and the matching values in compose/production/nginx/nginx.conf).
# Safe to re-run — it skips issuance if a real cert already exists.

set -o errexit
set -o pipefail
set -o nounset

DOMAIN="license.cispam.org"   # TODO: must match compose/production/nginx/nginx.conf
EMAIL="admin@example.com"     # TODO: Let's Encrypt sends expiry/revocation notices here
STAGING=1                     # 1 = Let's Encrypt staging (no rate limits, untrusted cert)
                               # Set to 0 only once you've confirmed the flow works.

COMPOSE="docker compose -f docker-compose.production.yml"
CERTBOT_CONF_PATH="/etc/letsencrypt"

if $COMPOSE run --rm --entrypoint sh certbot -c \
    "[ -d ${CERTBOT_CONF_PATH}/live/${DOMAIN} ]" > /dev/null 2>&1; then
  echo "Certificate for ${DOMAIN} already exists — skipping issuance."
  echo "Delete the certbot_conf volume first if you need to re-issue."
  exit 0
fi

echo "### Creating a temporary self-signed certificate so Nginx can start..."
$COMPOSE run --rm --entrypoint sh certbot -c "\
  mkdir -p ${CERTBOT_CONF_PATH}/live/${DOMAIN} && \
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout '${CERTBOT_CONF_PATH}/live/${DOMAIN}/privkey.pem' \
    -out '${CERTBOT_CONF_PATH}/live/${DOMAIN}/fullchain.pem' \
    -subj '/CN=localhost'"

echo "### Starting Nginx..."
$COMPOSE up --force-recreate -d nginx

echo "### Deleting the temporary certificate..."
$COMPOSE run --rm --entrypoint sh certbot -c "rm -rf ${CERTBOT_CONF_PATH}/live/${DOMAIN} \
  ${CERTBOT_CONF_PATH}/archive/${DOMAIN} ${CERTBOT_CONF_PATH}/renewal/${DOMAIN}.conf"

echo "### Requesting the real certificate from Let's Encrypt..."
staging_arg=""
if [ "${STAGING}" != "0" ]; then
  staging_arg="--staging"
fi
$COMPOSE run --rm --entrypoint certbot certbot certonly \
  ${staging_arg} \
  --webroot -w /var/www/certbot \
  --email "${EMAIL}" -d "${DOMAIN}" \
  --agree-tos --no-eff-email --non-interactive

echo "### Reloading Nginx with the real certificate..."
$COMPOSE exec nginx nginx -s reload

echo "Done. If STAGING=1 above, the browser will show an untrusted-cert"
echo "warning — that's expected. Set STAGING=0 and re-run once you've"
echo "confirmed the flow to get a trusted certificate."
