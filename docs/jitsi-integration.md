# Integração Jitsi

## Escopo desta etapa

Esta etapa cria apenas a fundação de dados da integração Jitsi dentro da app
`bruce_lms_custom`.

Não foram implementados nesta etapa:

- frontend para professor ou aluno;
- incorporação com Jitsi IFrame API;
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
