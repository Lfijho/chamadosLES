# HelpDesk

## Platform
web

## Stack
Python, Flask, Jinja2, SQLite, SQLAlchemy, Alembic/Flask-Migrate, Gunicorn, Docker Compose.

## Users
Solicitantes registram problemas de TI. Técnicos consultam todos os chamados, definem prioridade e conduzem o atendimento até a conclusão.

## Product Purpose
Centralizar solicitações de suporte. As três Sprints permitem autenticar, abrir, consultar e atender chamados, acompanhar registros e consultar indicadores por perfil.

## Operating Context
Projeto individual de Laboratório de Engenharia de Software, responsável Leandro Pinzon Filho. Entrega final prevista em 03/12/2026. Demonstração local em http://localhost:8080.

## Capabilities and Constraints
Login e logout; abertura pelo solicitante; confirmação privada; consulta com filtros e paginação; prioridade e status pelo técnico, com solução obrigatória na conclusão; histórico de status e anotações; indicadores reais por status e prioridade exclusivos do técnico; quadro Kanban auxiliar separado. Sem cadastro público, edição ou exclusão de anotações. Recursos essenciais locais e persistência após recriar containers.

## Brand Commitments
HelpDesk. Português do Brasil, tom direto e profissional de ferramenta interna.

## Accessibility & Inclusion
Layout desktop/celular, labels, mensagens úteis, teclado, foco visível e contraste adequado.
