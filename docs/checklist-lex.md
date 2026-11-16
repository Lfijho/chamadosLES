# Checklist da entrega final no LEX

Projeto: HelpDesk. Responsável: Leandro Pinzon Filho. Prazo previsto: 03/12/2026.

## Arquivos e preparação

- [x] Implementação versionada com RF01 a RF06, migrações, catálogo e testes.
- [x] Dockerfile, compose.yml e instruções de execução no README.
- [x] Roteiro do vídeo em `docs/roteiro-video-final.md`.
- [x] Conferir `docs/entrega-sprint-3.pdf` como documento final.
- [x] Conferir fonte Markdown, DOCX editável e fontes/imagens UML da entrega.
- [x] Conferir pacote de implementação sem `.env`, senhas, bancos ou estado de runtime.

## Ações que dependem da realização efetiva

- [ ] Gravar o vídeo demonstrando os dois perfis e RF01 a RF06.
- [ ] Rever o vídeo e confirmar que não expõe credenciais ou dados pessoais reais.
- [ ] Realizar a apresentação ao professor.
- [ ] Postar PDF, implementação e vídeo no LEX, conforme o formato solicitado pela disciplina.
- [ ] Conferir os arquivos após a postagem e guardar a confirmação do envio.

Nenhuma gravação, apresentação ou postagem foi realizada nesta implementação. S3-12 permanece pendente no quadro. Preparar este checklist ou o roteiro não conclui essas ações.

Depois do último commit, um pacote de arquivos versionados pode ser gerado sem incluir estado local:

```bash
mkdir -p runtime
git archive --format=zip --output=runtime/entrega-helpdesk.zip HEAD
```

O PDF é `docs/entrega-sprint-3.pdf`; o ZIP contém a revisão versionada correspondente. Vídeo deve ser acrescentado somente após a gravação e conferência. As entregas das Sprints 1 e 2 permanecem no repositório como registros históricos.
