# WhatsApp via Evolution API/n8n

## Escopo desta etapa

Esta etapa cria apenas a base de dados para a futura integração de WhatsApp
dentro da app `bruce_lms_custom`.

Não foram implementados nesta etapa:

- envio real de mensagens;
- automações, scheduler ou jobs;
- chamadas para Evolution API ou n8n;
- frontend Vue complexo;
- alteração em `frappe/`, `lms/`, `frappe-ui/` ou `jitsi-meet/`.

## Arquitetura prevista

O envio futuro deve acontecer exclusivamente no backend do Frappe ou por um fluxo
n8n chamado pelo backend. O frontend poderá solicitar ações autorizadas, como
reenvio manual, mas não deve conhecer tokens, API keys ou endpoints sensíveis.

O provedor ativo será definido em `Bruce Evolution Settings`:

- `Evolution API`: backend chama a Evolution API diretamente;
- `n8n`: backend chama um webhook n8n, e o n8n executa a integração externa.

A chave `EVOLUTION_API_KEY` não deve ser salva em campo aberto. Ela deve ficar em
variável de ambiente ou em `site_config.json` do site. Nenhuma tela de professor
ou aluno deve receber essa credencial.

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

As variáveis disponíveis no corpo da mensagem serão definidas na etapa futura de
envio. Nesta etapa, o cadastro existe apenas como base.

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

## Próxima etapa

A implementação futura deve criar serviços backend para:

- montar mensagens a partir dos templates;
- buscar `EVOLUTION_API_KEY` de variável de ambiente ou `site_config.json`;
- chamar Evolution API ou webhook n8n conforme `provider_mode`;
- registrar uma entrada de log para cada tentativa;
- permitir reenvio manual de mensagens com falha por usuário autorizado.
