# Checklist de testes

Este checklist orienta validações manuais e futuras validações automatizadas do `melura_lms`.

O foco inicial é garantir que a customização funcione dentro da app própria, sem alterar core, com segurança básica, permissões corretas e interface em português brasileiro.

## Validações manuais gerais

- Confirmar que nenhuma mudança foi feita diretamente em `frappe/`, `lms/`, `frappe-ui/` ou `jitsi-meet/`.
- Confirmar que textos visíveis estão em português brasileiro.
- Confirmar que o usuário `Administrator` não é usado como professor operacional.
- Confirmar que botões e mensagens principais usam linguagem simples.
- Confirmar que erros não exibem stack trace, token, API key ou payload sensível.
- Confirmar que `.env`, `site_config.json` e `common_site_config.json` reais não aparecem no controle de versão.

## Instalação e ambiente

- Instalar a app em um site local com Frappe LMS.
- Rodar migrações sem erro.
- Confirmar que a app aparece como instalada no site.
- Confirmar que configurações sensíveis podem ser lidas do ambiente ou site config.
- Confirmar que valores ausentes geram erro claro para usuário autorizado.
- Confirmar que `.env.example` não contém segredos reais.

## Permissões e papéis

- Root Técnico consegue configurar o ambiente.
- Professor acessa apenas suas rotinas acadêmicas.
- Professor não acessa API keys nem configurações sensíveis.
- Professor não precisa usar `Administrator`.
- Aluno acessa apenas cursos e aulas em que está matriculado.
- Aluno não acessa logs de WhatsApp.
- Aluno não consegue iniciar aula.
- Administrador LMS acessa KPIs básicos e logs operacionais.
- Integração/Bot tem escopo mínimo para automações.
- Ações críticas bloqueiam usuário sem permissão mesmo se a chamada for feita diretamente à API.

## Permission hardening validation

- Direct API calls to `bruce-professor-dashboard` reject `LMS Student` and
  `Guest` users before returning live class, notice log, or progress data.
- Student-facing methods derive the student from `frappe.session.user`; calls
  must not accept `student_user`, `user`, `email`, `student`, or `owner` as
  authorization scope.
- `Pendente`, `Bloqueado`, `Expirado`, expired windows, and missing access do
  not unlock classes, materials, exercise lists, answers, progress, or live
  room context.
- `Bruce Student Answer.is_correct` is recomputed on the backend from the
  linked question answer key, including direct document writes.
- WhatsApp preview/send/test responses and logs do not expose API keys, tokens,
  authorization headers, webhook secrets, or raw provider secret values.

## Cache and performance validation

- Confirm cache keys use the `melura_lms:v1` namespace.
- Confirm user-scoped cache keys include `frappe.session.user` and the resolved
  backend scope, not frontend-provided student/course/batch parameters.
- Confirm `Minha Aula`, student progress, student answers, student access
  status, exercise list context, and live-room context are not cached globally.
- Confirm WhatsApp provider secrets, recipient phone, recipient name, message
  body, provider response, and notification logs are not cached.
- Confirm the Jitsi settings cache contains only non-secret `domain` and
  `room_prefix` values.
- After changing `Bruce Jitsi Settings`, confirm the Jitsi settings cache key is
  invalidated or expires within the documented TTL.
- In development and production, confirm Redis is running for Frappe cache APIs;
  if Redis is unavailable, pages must compute normally instead of bypassing
  permission checks.

## Aula ao vivo com Jitsi

- Criar aula vinculada a curso ou turma.
- Gerar `roomName` no backend.
- Confirmar que o `roomName` é único e não previsível.
- Salvar link, curso, turma, professor, data/hora e status.
- Exibir aula como `Agendada` antes do início.
- Professor autorizado consegue iniciar aula.
- Status muda para `Ao vivo` após início.
- Aluno matriculado vê `Entrar na aula` quando disponível.
- Aluno sem matrícula válida não acessa a aula.
- Aula encerrada não permite nova entrada indevida.
- Aula cancelada não pode ser iniciada sem regra explícita.
- Nenhuma credencial sensível aparece no HTML, JS ou resposta da API.

## WhatsApp

- Configurar provedor por ambiente ou site config.
- Enviar aviso de aula pelo backend ou n8n.
- Registrar log para cada tentativa.
- Registrar status `Pendente`, `Enviado`, `Falhou` ou `Reenviado`.
- Registrar erro resumido quando o provedor falhar.
- Não registrar API key, token ou header sensível no log.
- Professor visualiza apenas falhas relacionadas às suas aulas, quando permitido.
- Administrador LMS consegue consultar falhas.
- Usuário autorizado consegue reenviar mensagem com falha.
- Reenvio manual preserva histórico da falha original.
- Reenvio em lote exige confirmação quando houver risco operacional.

## Painel do professor

- Próxima aula aparece em destaque.
- Lista de próximas aulas está correta.
- Ação `Iniciar aula` aparece apenas quando aplicável.
- Ação indisponível mostra motivo em português brasileiro.
- Status de avisos importantes aparece sem detalhes técnicos.
- Falha de envio oferece ação clara quando o professor tiver permissão.
- Interface evita excesso de métricas e termos administrativos.

## Área do aluno

- Aluno vê cursos matriculados.
- Aluno vê data e horário da próxima aula.
- Antes do horário, tela informa que aula ainda não está disponível.
- Durante disponibilidade, botão `Entrar na aula` aparece.
- Sem permissão, mensagem orienta contato com suporte.
- Textos estão em português brasileiro.
- Não há exposição de links ou dados de outras turmas.

## Painel administrativo básico

- Exibe alunos ativos.
- Exibe matrículas por curso ou turma.
- Exibe próximas aulas.
- Exibe aulas recentes ou status de aulas ao vivo.
- Exibe envios WhatsApp por status.
- Exibe falhas recentes de integração.
- Indicadores têm origem de dados rastreável.
- Painel não inclui secretaria financeira completa.

## Segurança antes de merge

- Procurar segredos no diff.
- Verificar que `.env` real não foi incluído.
- Verificar que `site_config.json` e `common_site_config.json` não foram incluídos.
- Confirmar que APIs novas validam permissão no backend.
- Confirmar que logs não armazenam dados sensíveis desnecessários.
- Confirmar que respostas para frontend não incluem API keys.
- Confirmar que endpoints de integração rejeitam chamadas sem autenticação ou escopo válido.

## Deployment readiness validation

- Confirmar que `docs/deployment/` contém os documentos exigidos de prontidão
  de deploy e produção.
- Rodar `python3 scripts/check_deployment_readiness.py` a partir da raiz da app.
- Confirmar que os docs mencionam segredos fora do Git, Redis, workers,
  scheduler, backup, restore, HTTPS e rollback.
- Confirmar que os exemplos usam placeholders, sem domínio, IP, credencial,
  telefone, e-mail ou dado real de aluno.
- Confirmar que `migrate` não é necessário quando a mudança for apenas
  documentação ou script de validação de repositório.

## Futuras validações automatizadas

### Testes unitários

- Geração de `roomName` único e não previsível.
- Montagem de link Jitsi.
- Validação de status de aula.
- Normalização de telefone para WhatsApp.
- Mapeamento de status do provedor.
- Sanitização de erro antes de salvar log.

### Testes de permissão

- Professor inicia apenas aula autorizada.
- Aluno entra apenas em aula de matrícula válida.
- Aluno não consulta logs.
- Administrador LMS consulta logs e KPIs.
- Integração/Bot executa apenas ações permitidas.
- Usuário sem papel adequado recebe erro de permissão.

### Testes de integração

- Envio WhatsApp com provedor mockado.
- Falha de provedor gera log com status `Falhou`.
- Reenvio cria nova tentativa ou histórico conforme regra definida.
- Callback de n8n ou Evolution API atualiza status sem expor segredo.
- Configuração ausente retorna erro controlado.

### Testes de interface

- Textos principais aparecem em português brasileiro.
- Botão `Iniciar aula` respeita status e permissão.
- Botão `Entrar na aula` respeita matrícula e disponibilidade.
- Mensagens de erro não expõem detalhes técnicos.
- Painéis carregam estados vazio, sucesso e erro.

### Testes de regressão

- Instalação da app em site limpo.
- Migração de DocTypes customizados.
- Atualização sem alteração direta no core.
- Fluxo completo: agendar aula, iniciar aula, aluno entrar, enviar aviso, registrar log.
