# WhatsApp via Evolution API/n8n

## Escopo atual

Esta etapa implementa o envio manual de link de aula por WhatsApp dentro da app
`bruce_lms_custom`, usando backend Python.

Implementado:

- serviço backend para envio manual do link de uma `Bruce Live Class`;
- suporte a `Evolution API` e `n8n` conforme `Bruce Evolution Settings`;
- uso de template ativo de `Bruce WhatsApp Message Template` para o evento
  `Link de aula disponível`, quando existir;
- criação de `Bruce WhatsApp Notification Log` para cada tentativa;
- status `Pendente`, `Enviado` ou `Falhou` no log;
- atualização do `Status do WhatsApp` da aula;
- ação no formulário `Bruce Live Class`: `Enviar link por WhatsApp`;
- botão simples no `Painel do Professor`: `Enviar link por WhatsApp`;
- teste unitário com mock, sem chamada externa real.

Ainda não foram implementados nesta etapa:

- automações, scheduler ou jobs;
- frontend Vue complexo;
- alteração em `frappe/`, `lms/`, `frappe-ui/` ou `jitsi-meet/`.

## Arquitetura prevista

O envio acontece exclusivamente no backend do Frappe ou por um fluxo n8n chamado
pelo backend. O frontend apenas solicita a ação autorizada e nunca recebe tokens,
API keys ou endpoints sensíveis além do próprio link da aula já registrado.

O provedor ativo será definido em `Bruce Evolution Settings`:

- `Evolution API`: backend chama a Evolution API diretamente;
- `n8n`: backend chama um webhook n8n, e o n8n executa a integração externa.

A chave `EVOLUTION_API_KEY` não é salva em campo aberto. Ela deve ficar em
variável de ambiente ou em `site_config.json` do site, usando uma destas chaves:

```json
{
  "evolution_api_key": "valor-secreto"
}
```

ou:

```json
{
  "EVOLUTION_API_KEY": "valor-secreto"
}
```

Também é aceito `EVOLUTION_API_KEY` como variável de ambiente. Nenhuma tela de
professor ou aluno recebe essa credencial.

## DocTypes criados

### Bruce Evolution Settings

DocType único para configuração operacional não sensível.

Campos:

| Campo | Label | Tipo | Observação |
| --- | --- | --- | --- |
| `api_url` | URL da API | Data | URL base da Evolution API, sem token. |
| `instance_name` | Nome da instância | Data | Nome da instância configurada no provedor. |
| `enabled` | Ativo | Check | Liga ou desliga a integração futura. |
| `provider_mode` | Modo do provedor | Select | `Evolution API` ou `n8n`. |
| `n8n_webhook_url` | URL do webhook n8n | Small Text | Usado quando o modo for `n8n`. |
| `api_key_note` | Observação sobre credenciais | HTML | Lembra que API key fica em env/site config. |

Quando a integração estiver ativa, a validação exige:

- `api_url` e `instance_name` para modo `Evolution API`;
- `n8n_webhook_url` para modo `n8n`.

### Bruce WhatsApp Message Template

DocType para armazenar modelos de mensagem em português brasileiro.

Campos:

| Campo | Label | Tipo | Observação |
| --- | --- | --- | --- |
| `title` | Título | Data | Nome do modelo. |
| `event_type` | Tipo de evento | Select | Evento acadêmico que usará a mensagem. |
| `message_body` | Corpo da mensagem | Text Editor | Texto da mensagem. |
| `enabled` | Ativo | Check | Permite desativar modelos sem apagar histórico. |

Variáveis disponíveis no corpo da mensagem:

| Variável | Significado |
| --- | --- |
| `{nome}` | Nome do destinatário. |
| `{aula}` | Título da aula ao vivo. |
| `{curso}` | Identificador do curso vinculado. |
| `{turma}` | Identificador da turma vinculada. |
| `{inicio}` | Data/hora de início formatada pelo Frappe. |
| `{link}` | Link da aula. |
| `{meeting_url}` | Mesmo valor de `{link}`. |

### Bruce WhatsApp Notification Log

DocType para registrar tentativas futuras de envio.

Campos:

| Campo | Label | Tipo | Observação |
| --- | --- | --- | --- |
| `recipient_name` | Nome do destinatário | Data | Nome exibido para suporte. |
| `phone` | Telefone | Data | Número de destino. |
| `message` | Mensagem | Text | Mensagem enviada ou preparada. |
| `status` | Status | Select | `Pendente`, `Enviado`, `Falhou`, `Reenviado`. |
| `error_message` | Mensagem de erro | Small Text | Erro legível quando houver falha. |
| `sent_at` | Enviado em | Datetime | Data/hora do aceite ou tentativa registrada. |
| `related_live_class` | Aula ao vivo relacionada | Link | Referência a `Bruce Live Class`. |
| `provider_response` | Resposta do provedor | Code | JSON técnico sem tokens ou segredos. |

O log deve ser usado para auditoria operacional e suporte. Dados sensíveis não
devem ser persistidos no campo `provider_response`.

## Fluxo manual implementado

1. Usuário autorizado abre uma `Bruce Live Class` ou o `Painel do Professor`.
2. Clica em `Enviar link por WhatsApp`.
3. Backend valida permissão de escrita na aula.
4. Backend busca alunos da `LMS Batch Enrollment` vinculada à turma. Se não
   houver turma com alunos, tenta `LMS Enrollment` pelo curso.
5. Backend monta a mensagem com template ativo ou mensagem padrão em português.
6. Backend cria log com status `Pendente`.
7. Backend chama Evolution API ou webhook n8n, conforme `provider_mode`.
8. Backend marca o log como `Enviado` ou `Falhou`.
9. A tela mostra uma mensagem curta em português e não quebra se o provedor
   estiver indisponível.

Quando a configuração estiver desativada, incompleta ou sem API key obrigatória,
o sistema não envia a mensagem, registra log com status `Falhou` e preenche uma
mensagem de erro amigável.

## Próximas etapas

- permitir reenvio manual de mensagens com falha a partir dos logs;
- adicionar automações 24h/1h antes, quando essa fase for autorizada;
- refinar filtros de permissão por vínculo real de professor, turma e curso;
- revisar consentimento e política de uso de telefone antes de envios em massa.
