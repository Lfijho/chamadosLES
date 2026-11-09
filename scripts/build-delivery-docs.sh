#!/bin/sh
set -eu
# Executar da raiz do repositório. Ferramenta opcional, separada da aplicação.
case "${1:-1}" in 1|2) ;; *) echo "Uso: $0 [1|2]" >&2; exit 2 ;; esac
docker build -f scripts/documents/Dockerfile -t helpdesk-delivery-documents .
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e DOCUMENT_SPRINT="${1:-1}" -v "$PWD:/work" helpdesk-delivery-documents
