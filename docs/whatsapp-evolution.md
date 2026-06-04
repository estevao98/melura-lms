# WhatsApp via Evolution API/n8n

## Escopo atual

Esta etapa implementa o envio manual de link de aula por WhatsApp dentro da app
`melura_lms`, usando backend Python.

Implementado:

- serviço backend para envio manual do link de uma `Bruce Live Class`;
- suporte a `Evolution API` e `n8n` conforme `Bruce Evolution Settings`;
- uso de template ativo de `Bruce WhatsApp Message Template` para o evento
  `Link de aula disponível`, quando existir;
- criação de `Bruce WhatsApp Notification Log` para cada tentativa;
- status `Pendente`, `Enviado` ou `Falhou` no log;
- atualização do `Status do WhatsApp` da aula;
- fallback manual/teste na `Bruce Live Class` com nome e telefone do
  destinatário;
- resolução automática de destinatários da turma da `Bruce Live Class` quando o
  telefone manual não estiver preenchido;
- deduplicação por telefone normalizado antes do envio;
- pré-visualização da mensagem final de WhatsApp na `Bruce Live Class`, usando
  os mesmos destinatários resolvidos do envio manual;
- registro de eventos operacionais em `Bruce Live Class Notice Log` quando há
  pré-visualização, tentativa manual, falha de envio ou integração desativada;
- ação no formulário `Bruce Live Class`: `Enviar link por WhatsApp`;
- ação no formulário `Bruce Live Class`: `Pré-visualizar WhatsApp`;
- status visual de WhatsApp no `Painel do Professor`;
- ação no `Painel do Professor`: `Pré-visualizar WhatsApp`, sem envio real;
- verificação administrativa segura no `Bruce Evolution Settings` com a ação
  `Testar configuração`;
- envio real, manual e controlado de uma única mensagem de teste pela
  `Evolution API`, acionado em `Bruce Evolution Settings`;
- teste unitário com mock, sem chamada externa real.

Ainda não foram implementados nesta etapa:

- automações, scheduler ou jobs;
- frontend Vue complexo;
- alteração em `frappe/`, `lms/`, `frappe-ui/` ou `jitsi-meet/`.
- automação de lembretes de WhatsApp.

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

A ação `Testar configuração` valida a configuração básica da Evolution API sem
enviar mensagem e sem chamar endpoint externo. Ela verifica:

- se `Bruce Evolution Settings` está disponível;
- se a integração está ativa;
- se `api_url` está preenchida;
- se `instance_name` está preenchido;
- se `EVOLUTION_API_KEY` existe em variável de ambiente ou `site_config.json`,
  sem mostrar o valor.

Mensagens possíveis para o administrador:

- `Configuração da Evolution API válida. A integração está ativa e a API key foi encontrada.`
- `A integração de WhatsApp está desativada em Bruce Evolution Settings.`
- `Informe a URL da API em Bruce Evolution Settings.`
- `Informe o nome da instância em Bruce Evolution Settings.`
- `Configure EVOLUTION_API_KEY em variável de ambiente ou site_config.json.`
- `Bruce Evolution Settings não foi encontrado. Revise a instalação da app.`

O resultado do teste é mostrado no Desk e registrado no logger
`melura_lms.whatsapp` apenas com o status técnico, sem credenciais.

A ação `Enviar mensagem de teste` envia uma mensagem real e única pela Evolution
API para um telefone informado manualmente. Antes do envio, o Desk solicita o
telefone e pede confirmação. O backend:

- valida permissão de escrita em `Bruce Evolution Settings`;
- normaliza o telefone brasileiro com a mesma regra usada no envio manual;
- reutiliza a validação de configuração da Evolution API;
- não expõe API key, endpoint sensível ou payload técnico no frontend;
- não usa turma, não resolve destinatários automaticamente e não envia em massa;
- cria um `Bruce WhatsApp Notification Log` com status `Pendente`;
- marca o log como `Enviado` ou `Falhou` conforme o resultado do provedor.

Mensagem enviada:

```text
Teste de integração do WhatsApp do Bruce LMS. Se você recebeu esta mensagem, a conexão está funcionando.
```

Quando a integração estiver desativada, a configuração estiver incompleta ou a
API key não existir em ambiente/site config, a mensagem real não é enviada e o
log é marcado como `Falhou` com uma mensagem amigável.

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

### Bruce Live Class Notice Log

DocType para registrar o histórico operacional de uma `Bruce Live Class`.

Ele complementa o `Bruce WhatsApp Notification Log`: o log de notificação guarda
uma entrada por destinatário/tentativa, enquanto o histórico da aula mostra uma
linha curta sobre a ação ou aviso ocorrido naquela aula.

Eventos de WhatsApp registrados nesta etapa:

| Evento | Quando é registrado |
| --- | --- |
| `Pré-visualização de WhatsApp gerada` | Ao gerar a prévia, sem envio real. |
| `Tentativa de envio manual` | Ao solicitar manualmente envio do link. |
| `Falha de envio` | Quando uma tentativa manual falha. |
| `Integração desativada` | Quando a prévia ou tentativa identifica a integração desligada. |

Campos principais:

| Campo | Label | Tipo | Observação |
| --- | --- | --- | --- |
| `related_live_class` | Aula ao vivo relacionada | Link | Referência a `Bruce Live Class`. |
| `event_type` | Tipo de evento | Select | Evento operacional registrado. |
| `title` | Título | Data | Resumo curto em português. |
| `message` | Mensagem | Text | Detalhe amigável, sem segredo. |
| `status` | Status | Select | `Registrado`, `Sucesso`, `Falhou` ou `Aviso`. |
| `created_by` | Criado por | Link | Usuário que acionou o evento. |
| `created_at` | Criado em | Datetime | Data/hora do evento. |

Esse histórico não envia WhatsApp, não chama Evolution API/n8n e não substitui
o log técnico por destinatário.

## Fluxo manual implementado

1. Usuário autorizado abre uma `Bruce Live Class` ou o `Painel do Professor`.
2. Para validação operacional, preenche opcionalmente `Nome do destinatário
   WhatsApp` e `Telefone WhatsApp` na aula.
3. Clica em `Enviar link por WhatsApp`.
4. Backend valida permissão de escrita na aula.
5. Se `Telefone WhatsApp` estiver preenchido, backend usa esse destinatário
   manual/teste. O telefone é normalizado removendo espaços, parênteses, traços
   e símbolos; quando tiver 10 ou 11 dígitos sem DDI, recebe o prefixo `55`.
6. Se não houver telefone manual, backend busca alunos vinculados à turma em
   `LMS Batch Enrollment`, usa `User.mobile_no` ou `User.phone` e remove
   telefones duplicados após normalização.
7. Se nenhum telefone for encontrado, o fluxo mantém a mensagem amigável:
   `Nenhum telefone de WhatsApp foi encontrado para esta aula.`
8. Backend monta a mensagem com template ativo ou mensagem padrão em português.
9. Backend cria um log com status `Pendente` para cada destinatário resolvido.
10. Backend chama Evolution API ou webhook n8n, conforme `provider_mode`.
11. Backend marca cada log como `Enviado` ou `Falhou`.
12. A tela mostra uma mensagem curta em português e não quebra se o provedor
   estiver indisponível.

Quando a configuração estiver desativada, incompleta ou sem API key obrigatória,
o sistema não envia a mensagem, registra log com status `Falhou` e preenche uma
mensagem de erro amigável.

## Fluxo de pré-visualização de WhatsApp

1. Usuário autorizado abre uma `Bruce Live Class`.
2. Clica em `Pré-visualizar WhatsApp`.
3. Backend valida permissão na aula.
4. Backend resolve destinatários usando a mesma regra do envio manual:
   destinatário manual/teste quando preenchido ou alunos da turma quando o
   telefone manual estiver vazio.
5. Backend monta a mensagem final usando o template ativo de
   `Bruce WhatsApp Message Template` ou a mensagem padrão em português.
6. Backend retorna somente dados de prévia:
   - quantidade de destinatários;
   - nome e telefone dos destinatários;
   - texto final da mensagem;
   - aviso quando a integração estiver desativada em `Bruce Evolution Settings`.
7. A tela mostra a prévia em um diálogo de leitura.

Esse fluxo não chama Evolution API, não chama webhook n8n, não envia mensagem
real e não cria `Bruce WhatsApp Notification Log`. Ele cria apenas um registro
operacional em `Bruce Live Class Notice Log`.

## Status no Painel do Professor

O `Painel do Professor` mostra a próxima aula ao vivo ou agendada com um status
simples de WhatsApp:

- `WhatsApp pendente`: aula sem envio registrado ou com status `Pendente`;
- `WhatsApp enviado`: aula com status `Enviado` ou `Reenviado`;
- `WhatsApp falhou`: aula com status `Falhou`;
- `Integração desativada`: `Bruce Evolution Settings` desativado ou indisponível.

A ação `Pré-visualizar WhatsApp` no painel usa o mesmo backend de prévia da
`Bruce Live Class`. Ela não chama Evolution API, não chama n8n, não envia
mensagem real e não cria log.

## Fluxo de teste de configuração

1. Administrador abre `Bruce Evolution Settings`.
2. Clica em `Testar configuração`.
3. Se houver alteração não salva, a tela pede para salvar antes de testar.
4. Backend valida somente os campos básicos e a presença de `EVOLUTION_API_KEY`.
5. Backend não envia WhatsApp e não chama a Evolution API.
6. Tela mostra mensagem curta em português, sem token, payload ou API key.

## Fluxo de mensagem real de teste

1. Administrador abre `Bruce Evolution Settings`.
2. Clica em `Enviar mensagem de teste`.
3. Se houver alteração não salva, a tela pede para salvar antes de continuar.
4. A tela solicita um único telefone WhatsApp.
5. A tela pede confirmação explícita antes do envio.
6. Backend normaliza o telefone e valida a configuração da Evolution API.
7. Backend envia uma única mensagem simples de teste pela Evolution API.
8. Backend registra o resultado em `Bruce WhatsApp Notification Log`.
9. Tela mostra resultado curto em português, sem API key ou dados sensíveis.

## Próximas etapas

- permitir reenvio manual de mensagens com falha a partir dos logs;
- adicionar automações 24h/1h antes, quando essa fase for autorizada;
- refinar filtros de permissão por vínculo real de professor, turma e curso;
- revisar consentimento e política de uso de telefone antes de envios em massa.
