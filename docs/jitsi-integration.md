# Integração Jitsi

## Escopo desta etapa

Esta etapa cria a fundação de dados da integração Jitsi e a experiência interna
de aula ao vivo dentro da app `bruce_lms_custom`.

Não foram implementados nesta etapa:

- envio de WhatsApp;
- logs de WhatsApp;
- alterações em `frappe/`, `lms/`, `frappe-ui/` ou `jitsi-meet/`.

## DocTypes criados

### Bruce Jitsi Settings

DocType único usado para configuração operacional não sensível do Jitsi.

Campos mínimos:

| Campo | Label | Tipo | Observação |
| --- | --- | --- | --- |
| `domain` | Domínio | Data | Domínio do servidor Jitsi. Padrão: `meet.jit.si`. |
| `room_prefix` | Prefixo da sala | Data | Prefixo usado antes do token seguro da sala. |
| `use_password` | Usar senha | Check | Preparado para etapa futura. |
| `open_in_new_tab_fallback` | Abrir em nova aba se necessário | Check | Preparado para fallback futuro de UX. |

O domínio é normalizado no backend para evitar variações como protocolo duplicado
ou barra final.

### Bruce Live Class

DocType para representar aulas ao vivo vinculadas ao LMS.

Campos mínimos:

| Campo | Label | Tipo | Observação |
| --- | --- | --- | --- |
| `title` | Título | Data | Nome da aula. |
| `course` | Curso | Link | Referência para `LMS Course`. |
| `batch` | Turma | Link | Referência para `LMS Batch`. |
| `instructor` | Professor | Link | Referência para `User`. |
| `starts_at` | Início | Datetime | Data e horário de início. |
| `ends_at` | Término | Datetime | Deve ser posterior ao início. |
| `room_name` | Nome da sala | Data | Gerado no backend, único e não previsível. |
| `meeting_url` | Link da aula | Small Text | Montado a partir do domínio Jitsi e `room_name`. |
| `status` | Status | Select | `Agendada`, `Ao vivo`, `Encerrada`, `Cancelada`. |
| `whatsapp_status` | Status do WhatsApp | Select | Preparado para etapa futura, sem envio nesta etapa. |

## Geração de sala

Ao criar ou validar uma aula, o backend preenche `room_name` quando o campo está
vazio. O valor usa:

- prefixo configurado em `Bruce Jitsi Settings.room_prefix`;
- token gerado com `secrets.token_urlsafe(18)`;
- índice único no campo `room_name`.

Esse formato evita nomes previsíveis e prepara a aula para uso posterior com a
Jitsi IFrame API.

Ao salvar a aula, o backend também preenche `meeting_url` quando o campo está
vazio. A URL é montada a partir do domínio configurado em
`Bruce Jitsi Settings.domain` e do `room_name` gerado, por exemplo:

```text
https://meet.jit.si/bruce-enem-token-seguro
```

Se `Bruce Jitsi Settings` não estiver disponível, a geração usa fallback seguro:

- domínio: `meet.jit.si`;
- prefixo da sala: `bruce`.

O backend não sobrescreve `room_name` nem `meeting_url` quando esses campos já
possuem valor. Uma alteração futura que regenere esses campos deve documentar o
motivo e tratar o impacto para alunos, professor e avisos enviados.

## Ações no Desk

O formulário `Bruce Live Class` possui ações simples no grupo `Jitsi`, sem
frontend Vue nesta etapa:

- `Abrir aula`: abre a página interna `/app/bruce-live-room/<aula>` no LMS.
- `Copiar link`: copia o `meeting_url` quando o contexto do navegador permitir.
  Se a cópia automática falhar, o Desk mostra o link para cópia manual.
- `Iniciar aula`: valida permissão no backend, marca aulas `Agendada` como
  `Ao vivo` e abre a página interna da aula.

As ações não montam URL no frontend e não hardcodam domínio. Elas usam apenas o
`meeting_url` registrado no documento para cópia e fallback externo.

Se a aula ainda não tiver `meeting_url`, o usuário vê uma mensagem amigável em
português orientando salvar a aula novamente ou revisar a configuração do Jitsi.

A ação `Iniciar aula` exige permissão de escrita no documento antes de alterar o
status. Aulas `Encerrada` ou `Cancelada` não podem ser iniciadas por essa ação.

## Página interna de aula ao vivo

A página Desk `Aula ao vivo` usa a rota `/app/bruce-live-room/<aula>` e incorpora
o Jitsi com a Jitsi IFrame API carregada por `https://<domínio>/external_api.js`.

O domínio vem de `Bruce Jitsi Settings.domain`. Para `meet.jit.si`, manter
`meet.jit.si` configurado nas settings.

A API backend
`bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.get_live_room_context`
valida usuário logado, status da aula, existência de `room_name` e
`meeting_url`, URL externa HTTP/HTTPS, acesso ativo do aluno por
`Bruce Student Access`, escopo de turma/curso, professor responsável ou papel
administrativo autorizado.

O payload retornado ao navegador contém apenas dados necessários para montar a
sala: título, curso, turma, status, domínio Jitsi, `room_name` e `external_url`
para fallback. Nenhuma API key ou segredo é exposto.

Na interface, o aluno ou professor vê título da aula, curso, turma, status,
área grande com Jitsi embutido e botão `Abrir em nova aba`.

## Permissões iniciais

As permissões iniciais seguem papéis já existentes no Frappe LMS:

- `System Manager` e `Moderator`: configuração e operação completa;
- `Batch Evaluator`: operação limitada a registros próprios;
- `LMS Student`: leitura da aula ao vivo.

As regras mais refinadas por vínculo real de curso, turma e matrícula devem ser
implementadas em etapa posterior com validações backend e filtros de permissão.

## Migração

Depois de atualizar a app no bench, executar:

```bash
bench --site <site> migrate
```

Após a migração, revisar `Bruce Jitsi Settings` no Desk e confirmar o domínio e
prefixo da sala antes de criar aulas reais.
