#!/bin/sh
set -eu
# Executar da raiz do repositório. Ferramenta opcional, separada da aplicação.
docker build -f scripts/documents/Dockerfile -t helpdesk-delivery-documents .
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/work" helpdesk-delivery-documents
