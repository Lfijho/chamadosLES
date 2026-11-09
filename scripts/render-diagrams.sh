#!/bin/sh
set -eu
# Executar na raiz do repositório; o renderizador não participa da aplicação.
docker build -f scripts/diagrams/Dockerfile -t helpdesk-diagrams:1.2025.10 .
if [ "$#" -eq 0 ]; then set -- '*.puml'; fi
for format in svg png; do
  docker run --rm --network none --user "$(id -u):$(id -g)" \
    -e PLANTUML_LIMIT_SIZE=8192 -v "$PWD/docs/diagrams:/work" -w /work \
    helpdesk-diagrams:1.2025.10 -charset UTF-8 -failfast2 "-t$format" "$@"
done
