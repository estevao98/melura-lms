# Checklist de testes

Este checklist orienta validações manuais e futuras validações automatizadas do `melura_lms`.

O foco inicial é garantir que a customização funcione dentro da app própria, sem alterar core, com segurança básica, permissões corretas e interface em português brasileiro.

## Validações manuais gerais

- Confirmar que nenhuma mudança foi feita diretamente em `frappe/`, `lms/` ou `frappe-ui/`.
- Confirmar que textos visíveis estão em português brasileiro.
- Confirmar que o usuário `Administrator` não é usado como professor operacional.
- Confirmar que botões e mensagens principais usam linguagem simples.
- Confirmar que erros não exibem stack trace, token, API key ou payload sensível.
- Confirmar que `.env`, `site_config.json` e `common_site_config.json` reais não aparecem no controle de versão.

## Instalação e ambiente

- Instalar a app em um site local com Frappe LMS.
- Rodar migrações sem erro.
- Confirmar que a app aparece como instalada no site.
- Confirmar que o Workspace `Melura` é sincronizado após `migrate`.
- Confirmar que configurações sensíveis podem ser lidas do ambiente ou site config.
- Confirmar que valores ausentes geram erro claro para usuário autorizado.
- Confirmar que `.env.example` não contém segredos reais.

## Workspace Melura

- Abrir `/app`.
- Confirmar que o Workspace `Melura` aparece no Frappe Desk.
- Confirmar que `Agenda de aulas ao vivo` abre o DocType `Melura Live Class Schedule`.
- Confirmar que `Aulas ao vivo` abre o DocType técnico `Bruce Live Class`, mas
  o rótulo visível no Workspace não expõe o nome legado.
- Confirmar que `Minha Aula` abre `/app/minha-aula`.
- Confirmar que `Painel do professor` abre `/app/bruce-professor-dashboard`
  com rótulo visível neutro.
- Confirmar que `Painel operacional` abre `/app/bruce-operational-dashboard`
  com rótulo visível neutro.
- Confirmar que `Configurações de WhatsApp`, `Modelos de mensagem` e
  `Logs de WhatsApp` abrem seus DocTypes técnicos existentes sem expor o nome
  legado no Workspace.
- Confirmar que `Materiais didáticos`, `Questões ENEM` e `Listas de exercícios`
  abrem os DocTypes técnicos existentes sem expor o nome legado no Workspace.
- Confirmar que `Acessos dos alunos` e `Respostas dos alunos` abrem os DocTypes
  técnicos existentes sem expor o nome legado no Workspace.
- Confirmar que nenhum rótulo visível do Workspace usa o nome pessoal legado.
- Confirmar que as rotas diretas existentes, como `/app/minha-aula`,
  `/app/bruce-professor-dashboard`, `/app/bruce-operational-dashboard` e
  `/app/bruce-live-room/<aula>`, continuam funcionando conforme permissões.

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
- Confirm live-class pages do not cache student-specific Google Meet links
  globally.
- In development and production, confirm Redis is running for Frappe cache APIs;
  if Redis is unavailable, pages must compute normally instead of bypassing
  permission checks.

## Aula ao vivo com Google Meet

- Criar aula vinculada a curso ou turma.
- Configurar link `https://meet.google.com/...`.
- Confirmar que `http`, `javascript:`, `data:`, `file:`, `ftp:` e hosts que não
  sejam `meet.google.com` são rejeitados.
- Salvar link, curso, turma, professor, data/hora e status.
- Exibir aula como `Agendada` antes do início.
- Professor autorizado consegue iniciar aula.
- Status muda para `Ao vivo` após início.
- Aluno matriculado vê `Entrar na aula` quando disponível.
- Aluno sem matrícula válida não acessa a aula.
- Aula encerrada não permite nova entrada indevida.
- Aula cancelada não pode ser iniciada sem regra explícita.
- Nenhuma credencial sensível aparece no HTML, JS ou resposta da API.
- `/app/bruce-live-room/<aula>` retorna `external_url` somente após validação
  backend e não retorna campos antigos de sala embutida.
- A página não carrega scripts de vídeo externo, não cria iframe de vídeo e
  abre o Google Meet em nova aba/app.

## Google Meet automatic live-flow validation

- Confirmar que `docs/decisions/ADR-0002-google-meet-only-live-flow.md` está
  aceito antes do go-live.
- Confirmar que não há roadmap de provedor de vídeo pago, auto-hospedado,
  gerenciado, embutido ou via SDK/API.
- Confirmar que `Melura Live Class Schedule` valida link do Google Meet,
  duração, janela de geração e lembretes.
- Confirmar que agenda ativa gera aulas futuras.
- Confirmar que agenda desativada não gera aulas.
- Confirmar que a geração não duplica aula para a mesma agenda e horário.
- Confirmar que aulas geradas copiam curso, turma, professor, início, término,
  link do Google Meet e referência da agenda.
- Confirmar que lembrete automático dos alunos respeita `Bruce Student Access`
  `Ativo` e escopo de curso/turma.
- Confirmar que lembrete do professor é separado do lembrete dos alunos.
- Confirmar que integração de WhatsApp desativada registra aviso/log seguro e
  não quebra scheduler.
- Confirmar que o fluxo do professor abre/inicia a aula com conta operacional
  não-`Administrator`.
- Confirmar que o fluxo do aluno `Ativo` entra na sala correta a partir de
  `Minha Aula` ou `/app/bruce-live-room/<aula>`.
- Confirmar em staging que aluno `Pendente`, `Bloqueado`, `Expirado`, sem
  acesso ou de outra turma/curso não recebe `meeting_url` nem `external_url`.
- Confirmar que professor/admin autorizado consegue abrir a sala sem usar
  `Administrator` como conta operacional.
- Confirmar que HTML, JS, respostas de API, logs, fixtures e testes não expõem
  segredo, token, API key, credencial de provedor ou dado real de aluno.

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

## WhatsApp real sending and retry validation

- Confirm preview does not call Evolution API or n8n and does not create
  `Bruce WhatsApp Notification Log`.
- Confirm disabled provider mode creates a safe failed log and makes no external
  provider call.
- Confirm missing `EVOLUTION_API_KEY` fails safely without exposing the missing
  value or any configured secret.
- Confirm mocked provider success returns only minimal status, counts, log name,
  and Portuguese user-facing message.
- Confirm mocked provider failure stores only a short redacted error and
  redacted `provider_response`.
- Confirm nested API keys, tokens, authorization headers, passwords, and
  secrets are redacted recursively before storage.
- Confirm `Enviado` and `Reenviado` logs are not retryable and do not trigger a
  duplicate provider call.
- Confirm `Pendente` and `Falhou` live-class logs are retryable only when the
  backend permission check allows the user.
- Confirm retry failure does not expose provider secrets in the response, log,
  or exception summary.
- Confirm retry tests mock provider calls and never call a real external API.
- Confirm current retry history limitation is understood: the existing log is
  updated because there is no retry count, attempt table, provider message ID,
  or idempotency key field yet.

## External student status integration

- Confirmar que o segredo do webhook fica fora do Git, em ambiente ou
  `site_config.json`.
- Confirmar que segredo ausente, assinatura ausente e assinatura inválida
  falham antes de localizar ou atualizar `Bruce Student Access`.
- Confirmar que payload assinado e válido mapeia status externo para `Ativo`,
  `Pendente`, `Bloqueado` ou `Expirado`.
- Confirmar que status externo desconhecido é rejeitado.
- Confirmar que campos de cartão, pagamento, checkout, invoice, assinatura,
  transação ou perfil financeiro de cliente são rejeitados.
- Confirmar que somente `access_status`, `source` e `external_reference`
  existentes são alterados.
- Confirmar que a mesma chamada válida pode ser processada mais de uma vez sem
  corromper o acesso.
- Confirmar que a resposta não expõe segredo, assinatura, payload financeiro,
  dados de cartão ou dados privados do aluno.
- Confirmar que nenhuma lógica de billing, checkout, assinatura, CRM, blog,
  newsletter ou captação de leads foi adicionada ao LMS.

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

## Backup/restore validation

- Confirmar que `docs/backup-restore/` contém overview, policy, backup
  runbook, restore runbook, restore test plan, disaster recovery checklist e
  security/retention guidance.
- Rodar `python3 scripts/check_backup_restore_readiness.py` a partir da raiz da
  app.
- Confirmar que os docs mencionam backup, restore, staging/test, retention,
  encryption, secrets, personal data, rollback e smoke tests.
- Confirmar que todos os comandos usam placeholders e não incluem domínio, IP,
  credencial, caminho sensível, telefone, e-mail, backup real ou dado real de
  aluno.
- Confirmar que nenhum restore real foi executado contra produção.
- Confirmar que restore real, quando necessário, é tratado como procedimento
  manual de staging/test antes de qualquer uso em produção.

## Futuras validações automatizadas

### Testes unitários

- Validação de link Google Meet.
- Geração automática de aulas por agenda recorrente.
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
