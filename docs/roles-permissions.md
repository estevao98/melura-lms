# Papéis e permissões

Este documento define a base documental de papéis e permissões do projeto
`bruce_lms_custom`.

Esta etapa é apenas documental. Ela não cria DocTypes, não cria papéis no banco,
não altera permissões reais e não implementa código. A implementação futura deve
acontecer dentro da app `bruce_lms_custom`, sem modificar diretamente `frappe/`,
`lms/`, `frappe-ui/` ou `jitsi-meet/`.

## Objetivos

- Separar responsabilidades entre operação acadêmica, administração LMS,
  integração e manutenção técnica.
- Garantir que professor, aluno e administração tenham apenas o acesso necessário.
- Evitar o uso do usuário `Administrator` como usuário operacional.
- Preparar a futura implementação de permissões para aulas ao vivo, WhatsApp,
  KPIs e configurações.
- Manter a experiência e a documentação em português brasileiro.

## Regra sobre o usuário Administrator

O usuário `Administrator` do Frappe é uma conta técnica de alto privilégio. Ele
não deve ser usado como usuário operacional do professor, nem para rotina diária
de aulas, turmas, envio de WhatsApp ou acompanhamento do painel.

Para o professor, deve existir um usuário humano próprio, com o papel `Professor`
e permissões limitadas ao fluxo acadêmico necessário. O `Administrator` deve ser
reservado para manutenção técnica excepcional, instalação, recuperação de acesso
ou diagnóstico controlado.

Essa separação reduz risco operacional, melhora auditoria e evita que uma ação
cotidiana do professor seja registrada como se tivesse sido feita por uma conta
técnica global.

## Princípios de permissão

- Aplicar o menor privilégio necessário.
- Validar ações críticas no backend, mesmo quando o frontend ocultar botões.
- Impedir que alunos acessem operações administrativas, logs internos ou
  configurações.
- Não expor API keys, tokens, endpoints sensíveis ou segredos no frontend.
- Registrar ações operacionais relevantes, como início de aula e reenvio de
  WhatsApp.
- Manter logs úteis para suporte sem armazenar dados sensíveis desnecessários.
- Relacionar permissões aos vínculos reais de curso, turma, aula e matrícula.

## Papéis previstos

### Root Técnico

Papel de manutenção técnica do ambiente e da app.

Responsabilidades:

- instalar, atualizar e migrar apps;
- configurar variáveis de ambiente e `site_config.json`;
- configurar segredos e integrações sensíveis;
- revisar logs técnicos;
- apoiar incidentes e recuperação de acesso;
- criar ou ajustar usuários operacionais quando necessário.

Permissões esperadas:

- acesso técnico amplo quando indispensável;
- acesso a configurações sensíveis;
- acesso a logs técnicos;
- suporte a aulas ao vivo, WhatsApp, KPIs e configurações.

Limites:

- não deve ser usado para operação diária do professor;
- não deve substituir papéis operacionais em fluxos normais;
- não deve expor credenciais em telas, mensagens ou documentação funcional.

### Professor

Papel humano responsável pela operação acadêmica das aulas.

Responsabilidades:

- acompanhar cursos e turmas sob sua responsabilidade;
- preparar ou agendar aulas ao vivo quando autorizado;
- iniciar aulas ao vivo;
- acompanhar status simples de avisos relacionados às suas aulas;
- solicitar ou executar reenvio de avisos quando permitido;
- acessar materiais e informações acadêmicas necessárias para sua turma.

Permissões esperadas:

- visualizar seu painel;
- visualizar aulas, cursos e turmas vinculados a ele;
- criar ou preparar aula ao vivo quando a política do LMS permitir;
- iniciar aula ao vivo se for o professor responsável;
- visualizar status resumido de WhatsApp das suas aulas;
- reenviar aviso de WhatsApp apenas dentro do seu escopo, se autorizado;
- visualizar KPIs simples ligados à sua rotina, como próximas aulas e falhas
  operacionais relevantes.

Limites:

- não acessa API keys, tokens ou endpoints sensíveis;
- não altera configurações globais de integração;
- não consulta logs técnicos completos;
- não opera com o usuário `Administrator`;
- não acessa turmas fora de sua responsabilidade sem permissão explícita;
- não altera dados financeiros nem administra o sistema como um todo.

### Aluno

Papel humano responsável por consumir conteúdos, aulas e avisos do curso.

Responsabilidades:

- acessar cursos em que está matriculado;
- acompanhar aulas e materiais liberados;
- entrar na aula ao vivo quando disponível;
- receber avisos operacionais por WhatsApp conforme cadastro e consentimento
  aplicável.

Permissões esperadas:

- visualizar cursos e aulas em que possui matrícula válida;
- visualizar data, horário e status de aulas ao vivo disponíveis;
- entrar na aula ao vivo quando a aula estiver liberada;
- visualizar mensagens simples de erro ou orientação.

Limites:

- não inicia, agenda, cancela ou encerra aula;
- não gera link ou `roomName` do Jitsi;
- não acessa aulas de turmas sem matrícula válida;
- não acessa logs de WhatsApp;
- não vê dados de outros alunos;
- não acessa KPIs administrativos;
- não acessa configurações.

Implementação atual:

- a página Desk `Minha Aula` (`/app/minha-aula`) está liberada para o papel
  `LMS Student`;
- a tela consulta somente a próxima `Bruce Live Class` ativa ou agendada visível
  pelas permissões do usuário;
- a ação do aluno é restrita a abrir o link da aula já salvo ou copiar esse
  link;
- a tela não inicia aula, não agenda aula, não envia WhatsApp, não consulta logs
  e não expõe configurações sensíveis;
- o filtro por vínculo real de matrícula/turma ainda será refinado em etapa
  posterior.

### Administrador LMS

Papel operacional responsável pela administração básica do LMS, sem assumir
função técnica irrestrita.

Responsabilidades:

- acompanhar operação acadêmica;
- apoiar professor e alunos em problemas de acesso;
- consultar aulas agendadas, status e falhas;
- acompanhar KPIs básicos do LMS;
- consultar logs de WhatsApp;
- reenviar mensagens com falha;
- ajustar configurações operacionais não sensíveis quando permitido.

Permissões esperadas:

- criar, editar e acompanhar aulas ao vivo;
- consultar status de aulas e mensagens;
- reenviar WhatsApp com falha;
- visualizar KPIs administrativos básicos;
- visualizar logs operacionais com dados sensíveis ocultos;
- alterar configurações não sensíveis, como provedor ativo, templates
  operacionais ou preferências permitidas.

Limites:

- não acessa segredos diretamente, salvo quando também possuir atribuição técnica
  formal;
- não usa conta de Root Técnico para rotina administrativa;
- não transforma o LMS em secretaria financeira completa;
- não altera core do Frappe, Frappe LMS, Frappe UI ou Jitsi Meet.

### Integração/Bot

Papel técnico de escopo limitado para automações, webhooks, callbacks e jobs.

Responsabilidades:

- registrar tentativas de envio de WhatsApp;
- atualizar status de mensagens;
- receber callbacks de n8n, Evolution API ou provedor equivalente;
- executar jobs em background com escopo controlado;
- registrar origem e resultado das ações automatizadas.

Permissões esperadas:

- criar ou atualizar logs de WhatsApp dentro do escopo da integração;
- atualizar status de mensagens e callbacks;
- executar ações automatizadas autorizadas pelo backend;
- acessar apenas dados mínimos necessários para a automação.

Limites:

- não possui permissão ampla de administrador;
- não acessa telas humanas sem necessidade;
- não carrega credenciais no frontend;
- não modifica cursos, turmas, usuários ou configurações globais fora do escopo;
- deve usar credencial rotacionável e revogável.

## Permissões por domínio funcional

### Aulas ao vivo

As aulas ao vivo serão representadas futuramente por DocType customizado, como
`Bruce Live Class`, mas este documento não cria esse DocType.

Permissões esperadas:

| Ação | Root Técnico | Professor | Aluno | Administrador LMS | Integração/Bot |
| --- | --- | --- | --- | --- | --- |
| Criar aula ao vivo | Suporte técnico | Sim, se autorizado | Não | Sim | Não |
| Editar dados da aula | Suporte técnico | Somente suas aulas, se autorizado | Não | Sim | Não |
| Gerar `roomName` seguro | Backend | Backend | Não | Backend | Não |
| Ver link da aula | Suporte técnico | Sim, se responsável | Sim, se matriculado e liberado | Sim | Não |
| Iniciar aula | Suporte técnico | Sim, se responsável | Não | Sim, se necessário | Não |
| Entrar como aluno | Não operacional | Não operacional | Sim, se matriculado | Suporte | Não |
| Cancelar ou encerrar aula | Suporte técnico | Sim, se autorizado | Não | Sim | Não |
| Ver status da aula | Sim | Sim, se vinculada | Sim, se matriculado | Sim | Não |

Regras importantes:

- o `roomName` deve ser gerado no backend, de forma única e não previsível;
- o aluno só entra na aula se tiver matrícula válida e a aula estiver disponível;
- o professor só inicia aula em turma ou curso sob sua responsabilidade;
- ações de iniciar, cancelar ou encerrar aula devem ser auditáveis.

### Logs de WhatsApp

Os logs de WhatsApp serão representados futuramente por DocType customizado,
como `Bruce WhatsApp Message Log`, mas este documento não cria esse DocType.

Permissões esperadas:

| Ação | Root Técnico | Professor | Aluno | Administrador LMS | Integração/Bot |
| --- | --- | --- | --- | --- | --- |
| Criar log de envio | Suporte técnico | Não direto | Não | Sim, por ação administrativa | Sim |
| Ver status resumido | Sim | Somente aulas vinculadas | Não | Sim | Próprios registros |
| Ver log operacional | Sim | Limitado, sem detalhe técnico | Não | Sim | Próprios registros |
| Ver payload técnico | Sim, quando necessário | Não | Não | Parcial, sem segredo | Não |
| Reenviar mensagem falha | Suporte técnico | Sim, se autorizado e vinculada | Não | Sim | Sim, por job autorizado |
| Atualizar status por callback | Suporte técnico | Não | Não | Não direto | Sim |

Regras importantes:

- o envio deve acontecer no backend ou via n8n;
- tokens e endpoints sensíveis não devem aparecer no frontend;
- cada tentativa deve registrar status, origem, data/hora e erro quando houver;
- reenvio manual deve preservar histórico e registrar responsável;
- professor deve ver apenas informação operacional suficiente, sem payload técnico.

### KPIs

Os KPIs administrativos básicos poderão ser consultados em tempo real ou
armazenados futuramente em estrutura como `Bruce Admin KPI Snapshot`, mas este
documento não cria esse DocType.

Permissões esperadas:

| Ação | Root Técnico | Professor | Aluno | Administrador LMS | Integração/Bot |
| --- | --- | --- | --- | --- | --- |
| Ver alunos ativos | Suporte técnico | Limitado às suas turmas, se necessário | Não | Sim | Não |
| Ver matrículas por curso/turma | Suporte técnico | Limitado ao seu escopo | Não | Sim | Não |
| Ver próximas aulas | Sim | Sim, vinculadas | Sim, quando matriculado | Sim | Não |
| Ver aulas realizadas | Sim | Sim, vinculadas | Limitado ao próprio curso | Sim | Não |
| Ver envios por status | Sim | Resumo das suas aulas | Não | Sim | Não |
| Ver falhas operacionais recentes | Sim | Somente relacionadas às suas aulas | Não | Sim | Não |

Regras importantes:

- KPIs devem apoiar operação acadêmica e suporte;
- o LMS não deve virar secretaria financeira completa;
- indicadores financeiros detalhados, cobrança e inadimplência ficam fora do
  escopo inicial;
- cada indicador deve ter origem rastreável e respeitar permissões.

### Configurações

As configurações operacionais poderão ser representadas futuramente por DocType
customizado, como `Bruce Integration Settings`, mas este documento não cria esse
DocType.

Permissões esperadas:

| Ação | Root Técnico | Professor | Aluno | Administrador LMS | Integração/Bot |
| --- | --- | --- | --- | --- | --- |
| Configurar segredos | Sim | Não | Não | Não, salvo atribuição técnica formal | Não |
| Ver referência de configuração | Sim | Não | Não | Sim, se não sensível | Não |
| Alterar provedor operacional | Sim | Não | Não | Sim, se permitido | Não |
| Alterar templates de mensagem | Sim | Não | Não | Sim, se permitido | Não |
| Ver status da integração | Sim | Resumo operacional, se relacionado | Não | Sim | Próprio status |
| Rotacionar credenciais | Sim | Não | Não | Não, salvo atribuição técnica formal | Não |

Regras importantes:

- segredos devem ficar em variável de ambiente ou `site_config.json`, nunca em
  código versionado;
- configurações sensíveis não devem ser expostas para professor, aluno ou
  frontend;
- alterações de configuração devem registrar responsável quando possível;
- o bot não deve alterar configuração global.

## Matriz geral resumida

| Ação | Root Técnico | Professor | Aluno | Administrador LMS | Integração/Bot |
| --- | --- | --- | --- | --- | --- |
| Usar o painel do professor | Suporte | Sim | Não | Suporte | Não |
| Usar painel administrativo | Suporte | Não | Não | Sim | Não |
| Acessar cursos matriculados | Suporte | Conforme vínculo | Sim | Suporte | Não |
| Agendar aula ao vivo | Suporte | Sim, se autorizado | Não | Sim | Não |
| Iniciar aula ao vivo | Suporte | Sim, se responsável | Não | Sim, se necessário | Não |
| Entrar em aula ao vivo | Não operacional | Não operacional | Sim, se matriculado | Suporte | Não |
| Consultar logs de WhatsApp | Sim | Resumo vinculado | Não | Sim | Próprios registros |
| Reenviar WhatsApp | Suporte | Sim, se autorizado | Não | Sim | Sim, por job |
| Ver KPIs básicos | Sim | Limitado | Não | Sim | Não |
| Alterar configurações não sensíveis | Sim | Não | Não | Sim, se permitido | Não |
| Alterar configurações sensíveis | Sim | Não | Não | Não, salvo atribuição técnica | Não |

## Validações obrigatórias no backend

Toda implementação futura deve validar:

- usuário autenticado;
- papel adequado;
- vínculo com curso, turma, aula ou matrícula;
- responsabilidade do professor pela aula;
- status atual da aula;
- status atual da mensagem de WhatsApp;
- escopo da integração ou bot;
- ausência de segredos na resposta;
- permissão específica para ações críticas, como iniciar aula, gerar link,
  reenviar WhatsApp e alterar configuração.

Validações no frontend ajudam a experiência, mas não substituem permissões e
checagens no backend.
