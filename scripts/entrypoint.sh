#!/bin/sh
set -eu
umask 077
mkdir -p "$HELPDESK_STATE_DIR"
if [ ! -w "$HELPDESK_STATE_DIR" ]; then
  echo "Erro: diretório de estado sem permissão de escrita para o usuário da aplicação." >&2
  exit 1
fi
echo "Aplicando migrações..."
flask db upgrade
echo "Preparando dados iniciais..."
flask seed
echo "Iniciando servidor..."
exec "$@"
