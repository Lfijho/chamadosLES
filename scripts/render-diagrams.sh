#!/bin/sh
set -eu
# Executar na raiz do repositório; o renderizador não participa da aplicação.
export DIAGRAM_UID="$(id -u)"
export DIAGRAM_GID="$(id -g)"
docker compose --profile tools run --rm --no-deps diagrams -charset UTF-8 -failfast2 -tsvg '*.puml'
docker compose --profile tools run --rm --no-deps diagrams -charset UTF-8 -failfast2 -tpng '*.puml'
