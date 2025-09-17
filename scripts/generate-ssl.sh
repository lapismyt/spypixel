#!/bin/bash

# Generate self-signed SSL certificates for nginx
# This creates certificates that will work immediately without external dependencies

SSL_DIR="./ssl"
mkdir -p "$SSL_DIR"

echo "### Generating self-signed SSL certificate..."

# Generate private key
openssl genrsa -out "$SSL_DIR/nginx.key" 2048

# Generate certificate
openssl req -new -x509 -key "$SSL_DIR/nginx.key" -out "$SSL_DIR/nginx.crt" -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "### SSL certificate generated successfully!"
echo "Certificate: $SSL_DIR/nginx.crt"
echo "Private key: $SSL_DIR/nginx.key"
echo ""
echo "Note: This is a self-signed certificate. Browsers will show a security warning."
echo "For production, consider using a proper SSL certificate from a CA."
