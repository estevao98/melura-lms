# Sistema de design

Este documento define padrões simples de interface para as customizações do `bruce_lms_custom`.

O objetivo não é criar um sistema de design completo paralelo ao Frappe UI. A prioridade é manter uma experiência clara, em português brasileiro, fácil para professor não técnico e consistente com o Frappe LMS.

## Princípios

- Usar Frappe UI sempre que possível.
- Manter o Frappe LMS reconhecível e atualizável.
- Evitar telas complexas para tarefas simples.
- Usar português brasileiro em todos os textos visíveis.
- Priorizar ações claras: iniciar aula, entrar na aula, reenviar aviso, ver turma.
- Separar telas operacionais de telas técnicas.
- Não mostrar tokens, endpoints sensíveis ou payloads técnicos para professor e aluno.

## Público principal

### Professor

Precisa iniciar aulas, ver turmas e resolver falhas simples sem depender de operação técnica.

Interface recomendada:

- painel com próxima aula em destaque;
- poucos botões por tela;
- estados claros de aula;
- mensagens de erro com ação de recuperação;
- termos técnicos escondidos em áreas administrativas.

### Aluno

Precisa acessar conteúdo e entrar na aula ao vivo com o menor atrito possível.

Interface recomendada:

- botão `Entrar na aula` quando a aula estiver disponível;
- data e horário visíveis antes da aula;
- aviso simples quando a aula ainda não estiver liberada;
- mensagem clara quando não houver matrícula válida.

### Administrador LMS

Precisa acompanhar operação acadêmica, logs e integrações.

Interface recomendada:

- KPIs poucos e acionáveis;
- tabelas para logs e falhas;
- filtros por curso, turma, status e data;
- detalhes técnicos apenas onde forem úteis para suporte.

## Linguagem

Usar frases curtas, diretas e profissionais.

Preferir:

- `Iniciar aula`
- `Entrar na aula`
- `Reenviar aviso`
- `Ver turma`
- `Aula agendada com sucesso.`
- `A aula ainda não está disponível.`
- `Você não tem permissão para iniciar esta aula.`

Evitar:

- jargões técnicos para professor e aluno;
- mensagens em inglês;
- códigos de erro sem explicação;
- textos longos dentro de botões;
- nomes internos como `roomName`, `webhook`, `payload` fora de telas técnicas.

## Componentes

Usar componentes do Frappe UI quando disponíveis:

- botões para ações principais e secundárias;
- cards para blocos curtos de informação;
- tabelas para logs e listas administrativas;
- badges para status;
- diálogos para confirmação;
- alertas para erro, sucesso ou aviso;
- campos de texto, seletores e seletores de data para formulários.

Não criar componentes customizados quando um componente Frappe UI resolver o fluxo com clareza.

## Botões e ações

Ação primária por tela:

- professor: `Iniciar aula`;
- aluno: `Entrar na aula`;
- administrador: ação relacionada ao contexto, como `Reenviar` ou `Salvar configuração`.

Padrões:

- ações destrutivas ou sensíveis exigem confirmação;
- reenvio em lote deve confirmar quantidade de destinatários;
- ações indisponíveis devem explicar o motivo;
- botões devem usar verbos claros.

## Status

### Aula ao vivo

- `Agendada`: aula criada e ainda não iniciada.
- `Ao vivo`: aula iniciada pelo professor.
- `Encerrada`: aula finalizada ou marcada como concluída.
- `Cancelada`: aula não acontecerá.

### WhatsApp

- `Pendente`: envio aguardando processamento.
- `Enviado`: provedor aceitou a mensagem.
- `Falhou`: envio não foi concluído.
- `Reenviado`: tentativa manual foi executada.

Status devem aparecer como badges ou indicadores visuais simples, sempre com texto em português brasileiro.

## Layouts

### Painel do professor

Conteúdo recomendado:

- próxima aula em destaque;
- próximas aulas em lista curta;
- status de avisos importantes;
- atalhos para curso, turma e materiais;
- falhas de WhatsApp relacionadas às aulas.

Evitar:

- tabelas densas;
- métricas financeiras;
- configurações técnicas;
- excesso de filtros.

Primeira versão no Desk:

- usar uma única área principal com a próxima aula;
- manter título, curso, turma, início, status, status do WhatsApp e link em blocos
  curtos de leitura;
- usar badge textual para o status da aula;
- destacar `Iniciar aula` como ação primária somente quando a aula estiver
  `Agendada`;
- manter `Abrir aula` como ação secundária quando o link já existir;
- mostrar `Nenhuma aula ao vivo encontrada.` quando não houver aula disponível;
- não mostrar `roomName`, payloads, tokens, endpoints ou detalhes técnicos.

### Área do aluno

Conteúdo recomendado:

- cursos em andamento;
- próxima aula ao vivo;
- materiais e aulas disponíveis;
- avisos importantes.

Evitar:

- detalhes de integração;
- mensagens técnicas;
- múltiplos caminhos para a mesma ação principal.

### Painel administrativo

Conteúdo recomendado:

- alunos ativos;
- matrículas por curso ou turma;
- próximas aulas;
- aulas recentes;
- envios de WhatsApp por status;
- falhas recentes de integração.

Fora da interface:

- cobrança recorrente;
- conciliação;
- emissão fiscal;
- contratos financeiros.

## Formulários

Formulários devem pedir apenas o necessário.

Para agendar aula:

- título;
- curso ou turma;
- professor;
- data;
- horário;
- duração prevista.

O sistema deve gerar sala Jitsi no backend. O professor não deve preencher nome técnico de sala.

## Mensagens de erro

Toda mensagem de erro deve:

- estar em português brasileiro;
- explicar o problema em linguagem simples;
- indicar uma ação quando houver recuperação possível;
- não expor segredo, token ou stack trace.

Exemplos:

- `Não foi possível iniciar a aula. Tente novamente ou fale com o suporte.`
- `Não foi possível enviar o aviso pelo WhatsApp. Verifique o log ou tente reenviar.`
- `A aula está cancelada e não pode ser iniciada.`
- `Você não tem permissão para acessar esta turma.`

## Acessibilidade e consistência

- Usar contraste suficiente entre texto e fundo.
- Não depender apenas de cor para comunicar status.
- Manter rótulos visíveis em campos importantes.
- Usar ordem visual previsível.
- Evitar textos pequenos em informações críticas.
- Garantir que botões principais sejam acessíveis por teclado quando aplicável.
