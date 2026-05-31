# Fluxos de UX

## Diretrizes gerais

A interface final deve estar em português brasileiro, usar Frappe UI sempre que possível e priorizar fluxos simples para um professor não técnico.

O usuário deve encontrar ações operacionais sem precisar entender Jitsi, Evolution API, n8n ou detalhes internos do Frappe. Termos técnicos devem aparecer apenas em telas administrativas ou logs.

## Papéis

### Professor

Objetivo: preparar, iniciar e acompanhar aulas com o menor número possível de passos.

Necessidades principais:

- ver próximas aulas;
- iniciar aula ao vivo;
- acessar turma e curso;
- identificar se os alunos receberam o link;
- solicitar reenvio de aviso quando houver falha.

### Aluno

Objetivo: acessar conteúdo e aula ao vivo de forma direta.

Necessidades principais:

- ver cursos e aulas disponíveis;
- entrar na aula ao vivo no horário correto;
- receber link por WhatsApp;
- consultar avisos e materiais sem confusão.

### Administrador LMS

Objetivo: acompanhar operação básica do LMS e resolver problemas simples.

Necessidades principais:

- ver KPIs acadêmicos básicos;
- consultar aulas agendadas e status;
- consultar logs de WhatsApp;
- reenviar mensagens com falha;
- configurar integrações sem expor credenciais no frontend.

## Fluxo: professor agenda ou prepara aula ao vivo

1. Professor acessa o painel.
2. Seleciona curso ou turma.
3. Informa título, data, horário e duração prevista da aula.
4. Sistema gera a sala Jitsi no backend com `roomName` único e não previsível.
5. Sistema salva aula com status `Agendada`.
6. Tela mostra a aula na lista de próximas aulas.

Estados esperados:

- `Agendada`: aula criada e ainda não iniciada.
- `Ao vivo`: professor iniciou a sala.
- `Encerrada`: aula finalizada ou marcada como concluída.
- `Cancelada`: aula não acontecerá.

## Fluxo: professor inicia aula ao vivo

1. Professor entra no painel.
2. Visualiza a próxima aula em destaque.
3. Clica em `Iniciar aula`.
4. Backend valida permissão e status.
5. Sistema abre ou incorpora a sala Jitsi.
6. Status muda para `Ao vivo`.
7. Alunos autorizados passam a ver ação para entrar.

Regras de UX:

- A ação principal deve ser clara e visível.
- Erros devem explicar o que fazer em português brasileiro.
- O professor não deve copiar manualmente roomName ou configurar Jitsi.

## Fluxo: aluno entra na aula ao vivo

1. Aluno acessa o LMS.
2. Entra no curso ou na área de próximas aulas.
3. Visualiza aula disponível.
4. Clica em `Entrar na aula`.
5. Sistema valida matrícula e disponibilidade.
6. Aula abre via experiência Jitsi definida para o LMS.

Estados de tela:

- antes do horário: mostrar data e horário da aula;
- disponível: mostrar botão `Entrar na aula`;
- encerrada: mostrar status e, se existir, material ou gravação futura;
- sem permissão: mostrar mensagem simples orientando contato com suporte.

## Fluxo: envio manual de link por WhatsApp

1. Professor ou administrador abre uma aula ao vivo.
2. Para teste ou validação inicial, pode preencher `Nome do destinatário
   WhatsApp` e `Telefone WhatsApp` na própria aula.
3. Clica em `Enviar link por WhatsApp`.
4. Backend valida permissão e configuração.
5. Se houver telefone manual, backend usa esse destinatário. Espaços,
   parênteses, traços e símbolos são removidos; números brasileiros com 10 ou
   11 dígitos recebem o prefixo `55` quando ainda não tiverem DDI.
6. Se não houver telefone manual, backend busca os alunos da turma vinculada à
   aula e tenta usar `User.mobile_no` ou `User.phone`.
7. Telefones repetidos são ignorados após normalização, evitando mensagens
   duplicadas para o mesmo número.
8. Se nenhum telefone for encontrado, a tela mantém erro amigável informando que
   nenhum telefone foi encontrado para a aula.
9. Backend monta a mensagem em português brasileiro.
10. Backend chama Evolution API ou webhook n8n conforme configuração.
11. Sistema registra cada tentativa no log, com uma entrada por destinatário.
12. Tela mostra resultado simples, sem expor detalhes técnicos sensíveis.

Nesta etapa o envio é somente manual. Ainda não há automações 24h/1h antes da
aula. O campo de telefone na aula continua sendo o fallback manual/teste e tem
prioridade sobre os telefones dos alunos da turma.

## Fluxo futuro: envio automático de link por WhatsApp

1. Aula é agendada ou marcada para envio.
2. Backend monta a mensagem em português brasileiro.
3. Backend chama Evolution API ou webhook n8n conforme configuração.
4. Sistema registra cada tentativa no log.
5. Administração ou professor autorizado vê status de envio.

Status de envio:

- `Pendente`: envio aguardando processamento.
- `Enviado`: provedor aceitou a mensagem.
- `Falhou`: houve erro e o envio pode exigir ação.
- `Reenviado`: tentativa manual foi executada.

Regras de UX:

- Não mostrar token, endpoint sensível ou payload técnico para professor.
- Para falhas, mostrar uma mensagem curta e uma ação de reenvio quando permitido.
- Logs detalhados ficam em área administrativa.

## Fluxo: reenvio manual de WhatsApp

1. Usuário autorizado acessa mensagens com falha.
2. Seleciona uma mensagem ou lote pequeno.
3. Clica em `Reenviar`.
4. Backend valida permissão e dispara nova tentativa.
5. Sistema registra nova entrada ou atualiza histórico.
6. Tela mostra resultado.

Regras de UX:

- Evitar reenvio acidental em massa.
- Confirmar antes de reenviar muitos destinatários.
- Preservar histórico da falha original.

### Base atual para WhatsApp

Nesta etapa, o sistema possui cadastros, logs e envio manual backend do link de
aula. Quando o telefone manual da aula está vazio, o backend resolve
destinatários a partir da turma da aula. Ainda não existe automação, scheduler
ou botão de reenvio a partir do log.

O administrador configura o provedor em `Bruce Evolution Settings`, escolhendo
`Evolution API` ou `n8n`. A API key da Evolution deve ficar em variável de
ambiente ou `site_config.json`, nunca em campo aberto nem no frontend.

O administrador também pode cadastrar mensagens em `Bruce WhatsApp Message
Template`, em português brasileiro, e consultar registros em `Bruce WhatsApp
Notification Log`.

O template ativo para o tipo `Link de aula disponível` pode usar:

- `{nome}`;
- `{aula}`;
- `{curso}`;
- `{turma}`;
- `{inicio}`;
- `{link}`;
- `{meeting_url}`.

Fluxo manual de reenvio futuro previsto:

1. Administrador ou professor autorizado visualiza avisos de WhatsApp com
   status `Falhou`.
2. A tela mostra destinatário, aula relacionada, telefone, mensagem resumida e
   erro legível.
3. Usuário escolhe `Reenviar aviso`.
4. Backend valida permissão, busca credenciais fora do frontend e cria nova
   tentativa.
5. O resultado fica registrado em `Bruce WhatsApp Notification Log`.

## Fluxo: painel do professor

Conteúdo sugerido:

- próxima aula em destaque;
- lista curta de próximas aulas;
- status de envios importantes;
- atalhos para curso, turma e materiais;
- avisos operacionais relevantes.

Ações principais:

- `Iniciar aula`;
- `Ver turma`;
- `Reenviar aviso`, quando aplicável;
- `Copiar link`, somente se fizer sentido operacional e sem substituir o fluxo automático.

O painel deve evitar métricas excessivas, tabelas densas e termos administrativos que não ajudem a rotina do professor.

### Primeira versão no Desk

A primeira versão do painel é uma Page Desk simples chamada `Painel do Professor`.
Ela usa dados reais do DocType `Bruce Live Class` e mostra apenas uma aula:

- aula com status `Ao vivo`, quando existir;
- caso contrário, a próxima aula `Agendada` com início futuro.

Campos exibidos:

- título da aula;
- curso, com título legível quando disponível e fallback para o identificador;
- turma, com nome legível quando disponível e fallback para o identificador;
- horário de início;
- status da aula;
- status do WhatsApp;
- link da aula, quando existir.

Ações disponíveis:

- `Abrir aula`, quando a aula tiver link;
- `Iniciar aula`, para aula `Agendada`, chamando a validação backend já existente
  de `Bruce Live Class`.
- `Copiar link`, quando a aula tiver link e o navegador permitir cópia simples.
- `Enviar link por WhatsApp`, quando a aula tiver link, chamando o backend de
  envio manual e registrando `Bruce WhatsApp Notification Log`.

Se não houver aula agendada ou ao vivo visível para o usuário, o painel mostra:
`Nenhuma aula ao vivo encontrada.`

Nesta versão, o painel envia o link manualmente quando solicitado. Ele ainda não
reenviará avisos a partir dos logs e não substitui os fluxos administrativos do
Desk.

## Fluxo: painel administrativo básico

Conteúdo sugerido:

- alunos ativos;
- matrículas por curso ou turma;
- próximas aulas;
- aulas ao vivo recentes;
- envios WhatsApp por status;
- falhas recentes de integração.

Fora da tela:

- cobrança;
- inadimplência detalhada;
- conciliação;
- emissão fiscal;
- contratos financeiros.

Regras de UX:

- O painel deve apoiar operação acadêmica e suporte.
- KPIs devem ser poucos, claros e acionáveis.
- Cada indicador deve ter uma origem de dados rastreável.

## Mensagens e linguagem

Padrões:

- usar frases curtas;
- evitar jargão técnico para professor e aluno;
- usar verbos de ação claros;
- manter tom direto e profissional.

Exemplos:

- `Aula agendada com sucesso.`
- `A aula ainda não está disponível.`
- `Não foi possível enviar o aviso pelo WhatsApp. Tente reenviar ou verifique o log.`
- `Você não tem permissão para iniciar esta aula.`

## Casos de erro importantes

- Jitsi indisponível;
- aula sem turma vinculada;
- aluno sem matrícula válida;
- WhatsApp sem configuração ativa;
- provedor de WhatsApp retornando erro;
- usuário sem permissão;
- aula já encerrada;
- tentativa de iniciar aula cancelada.

Cada erro deve ter mensagem em português brasileiro e, quando possível, uma ação de recuperação.
