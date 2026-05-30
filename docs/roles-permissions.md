# Papéis e permissões

Este documento define os papéis operacionais esperados para o `bruce_lms_custom`.

As permissões devem ser implementadas dentro da app customizada e integradas aos papéis do Frappe/Frappe LMS quando fizer sentido. O usuário `Administrator` não deve ser usado como usuário operacional do professor.

## Princípios

- Usar o menor privilégio necessário.
- Separar operação acadêmica, administração LMS, integração e manutenção técnica.
- Validar ações críticas no backend.
- Evitar acesso de aluno a qualquer operação administrativa.
- Não expor configurações sensíveis para professor ou aluno.
- Manter permissões auditáveis.

## Root Técnico

Responsável por manutenção técnica do ambiente.

Pode:

- instalar e atualizar apps;
- executar migrações;
- configurar variáveis de ambiente e `site_config.json`;
- configurar integrações sensíveis;
- revisar logs técnicos;
- corrigir incidentes;
- criar usuários operacionais quando necessário.

Não deve:

- ser usado como usuário diário do professor;
- substituir papéis operacionais em fluxos normais;
- expor credenciais em telas ou documentação.

Observação: este papel pode corresponder a administradores técnicos do Frappe, mas deve ser usado com parcimônia.

## Professor

Responsável pela operação acadêmica das aulas.

Pode:

- acessar seu painel;
- ver cursos e turmas sob sua responsabilidade;
- ver próximas aulas;
- agendar ou preparar aula quando autorizado;
- iniciar aula ao vivo;
- ver status básico de envio de avisos relacionados às suas aulas;
- solicitar reenvio de aviso quando permitido;
- acessar links e materiais de suas turmas.

Não deve:

- acessar API keys;
- editar configurações globais de integração;
- consultar logs técnicos completos;
- operar como `Administrator`;
- acessar turmas fora de sua responsabilidade sem permissão explícita;
- alterar dados financeiros.

Permissões críticas:

- iniciar aula somente se for professor responsável ou usuário autorizado;
- reenviar aviso somente para aulas/turmas permitidas;
- visualizar dados de alunos apenas no contexto acadêmico necessário.

## Aluno

Responsável por acessar conteúdo e aulas do curso.

Pode:

- acessar cursos nos quais está matriculado;
- ver aulas e materiais liberados;
- entrar na aula ao vivo quando disponível;
- ver data, horário e status da aula;
- receber avisos por WhatsApp conforme cadastro e consentimento operacional aplicável.

Não deve:

- iniciar ou cancelar aula;
- gerar link Jitsi;
- acessar sala de aula de turma sem matrícula válida;
- ver logs de WhatsApp;
- ver dados de outros alunos;
- acessar configurações administrativas.

Permissões críticas:

- entrada na aula deve validar matrícula e disponibilidade;
- materiais devem respeitar regras do LMS;
- mensagens de erro devem orientar contato com suporte sem expor detalhes internos.

## Administrador LMS

Responsável pela operação administrativa básica do LMS.

Pode:

- acompanhar KPIs acadêmicos básicos;
- consultar aulas agendadas e status;
- consultar logs de WhatsApp;
- reenviar mensagens com falha;
- configurar opções operacionais não sensíveis;
- acompanhar falhas recentes de integração;
- apoiar professor e alunos em problemas de acesso.

Não deve:

- acessar segredos diretamente se não tiver função técnica;
- transformar o LMS em secretaria financeira completa;
- usar conta de Root Técnico para operação cotidiana;
- alterar core do Frappe ou LMS.

Permissões críticas:

- reenvio manual deve ser auditado;
- alterações de configuração devem registrar responsável quando possível;
- logs devem ocultar tokens e payloads sensíveis.

## Integração/Bot

Usuário técnico usado por automações, webhooks ou integrações.

Pode:

- executar ações específicas de integração;
- registrar logs de envio;
- atualizar status de mensagens;
- receber callbacks de n8n ou provedor quando configurado;
- executar jobs em background com escopo limitado.

Não deve:

- ter permissão ampla de administrador;
- acessar telas humanas sem necessidade;
- carregar credenciais no frontend;
- modificar cursos, turmas ou usuários fora do escopo da integração.

Permissões críticas:

- usar token ou credencial rotacionável;
- ter escopo mínimo;
- registrar origem da ação;
- permitir revogação sem afetar usuários humanos.

## Matriz inicial de permissões

| Ação | Root Técnico | Professor | Aluno | Administrador LMS | Integração/Bot |
| --- | --- | --- | --- | --- | --- |
| Configurar segredos | Sim | Não | Não | Não, salvo exceção controlada | Não |
| Ver painel do professor | Suporte | Sim | Não | Suporte | Não |
| Ver cursos matriculados | Suporte | Conforme vínculo | Sim | Suporte | Não |
| Agendar aula ao vivo | Suporte | Sim, se autorizado | Não | Sim | Não |
| Iniciar aula ao vivo | Suporte | Sim, se responsável | Não | Suporte | Não |
| Entrar em aula como aluno | Não operacional | Não operacional | Sim, se matriculado | Suporte | Não |
| Enviar aviso WhatsApp | Suporte | Solicitar, se autorizado | Não | Sim | Sim, por job |
| Reenviar aviso com falha | Suporte | Sim, se permitido | Não | Sim | Sim, por job |
| Ver logs resumidos | Sim | Apenas relacionados | Não | Sim | Apenas próprios |
| Ver logs técnicos completos | Sim | Não | Não | Parcial | Não |
| Ver KPIs básicos | Sim | Limitado | Não | Sim | Não |

## DocTypes customizados previstos

### Bruce Live Class

Representa uma aula ao vivo.

Permissões esperadas:

- Professor responsável pode visualizar e iniciar.
- Administrador LMS pode criar, editar e acompanhar.
- Aluno pode visualizar apenas aulas disponíveis de turmas em que está matriculado.
- Root Técnico pode dar suporte.

### Bruce WhatsApp Message Log

Registra tentativas de envio.

Permissões esperadas:

- Administrador LMS pode consultar e reenviar.
- Professor pode ver resumo relacionado às suas aulas quando necessário.
- Aluno não acessa.
- Integração/Bot pode criar ou atualizar entradas conforme escopo.

### Bruce Integration Settings

Guarda configurações operacionais e referências para segredos externos.

Permissões esperadas:

- Root Técnico gerencia segredos e configuração sensível.
- Administrador LMS pode alterar opções não sensíveis se permitido.
- Professor e aluno não acessam.
- Integração/Bot não altera configuração global.

### Bruce Admin KPI Snapshot

Armazena métricas administrativas básicas quando necessário.

Permissões esperadas:

- Administrador LMS visualiza.
- Root Técnico dá suporte.
- Professor vê apenas indicadores ligados à sua rotina, se houver necessidade.
- Aluno e Integração/Bot não acessam.

## Regras de validação no backend

Toda ação crítica deve validar:

- usuário autenticado;
- papel adequado;
- vínculo com curso, turma ou aula;
- status atual da aula ou mensagem;
- escopo da integração;
- ausência de exposição de segredos na resposta.

Validações de frontend ajudam a experiência, mas não substituem permissão no backend.
