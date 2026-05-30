# Arquitetura do bruce_lms_custom

## Visão geral

O `bruce_lms_custom` customiza o Frappe LMS para um curso online de Ciências Humanas/ENEM do professor Bruce. A arquitetura parte de um Frappe LMS limpo, sem alterações diretas em `frappe/`, `lms/`, `frappe-ui/` ou `jitsi-meet/`, e concentra regras, telas, integrações e documentação dentro desta app customizada.

O produto final deve oferecer uma experiência simples em português brasileiro para:

- alunos acessarem conteúdos, aulas ao vivo e links importantes;
- professor iniciar aulas, acompanhar turmas e reenviar comunicações sem depender de operação técnica;
- administração visualizar KPIs básicos do LMS sem transformar o LMS em uma secretaria financeira completa.

## Princípios

- Manter o Frappe LMS como base limpa e atualizável.
- Implementar extensões por app customizada, usando hooks, permissões, páginas, componentes e DocTypes próprios quando necessário.
- Usar Frappe UI sempre que possível nas interfaces.
- Não expor credenciais, tokens ou API keys no frontend.
- Manter todos os textos da interface final em português brasileiro.
- Separar responsabilidades acadêmicas, comunicação e indicadores básicos do LMS das rotinas financeiras completas.

## Componentes principais

### Frappe Framework

Responsável por autenticação, permissões, ORM, DocTypes, jobs em background, APIs internas, scheduler, logs e configuração por site.

Configurações sensíveis devem ficar em variáveis de ambiente ou `site_config.json`, nunca em código versionado.

### Frappe LMS

Permanece como a base de cursos, aulas, matrículas, progresso e experiência de aprendizagem. O projeto deve preferir configurações, extensões e pontos de integração do LMS antes de qualquer alteração em core.

### bruce_lms_custom

Camada de customização do projeto. Deve conter:

- DocTypes customizados para aulas ao vivo, logs de envio e configurações operacionais;
- hooks para conectar eventos do LMS às rotinas customizadas;
- páginas e componentes específicos do professor e da administração;
- APIs backend para Jitsi, WhatsApp e KPIs;
- documentação funcional e técnica do projeto.

### Jitsi

Usado para aulas ao vivo. O LMS deve permitir criar, iniciar e acessar aulas com Jitsi IFrame API.

Requisitos arquiteturais:

- gerar `roomName` único e não previsível;
- armazenar link, turma, curso, professor, data/hora e status;
- permitir que o professor inicie a aula pelo painel;
- permitir que o aluno entre na aula pelo LMS quando autorizado;
- manter qualquer configuração sensível do Jitsi fora do frontend.

### WhatsApp via Evolution API ou n8n

O envio de mensagens deve acontecer no backend ou por fluxo n8n. O frontend pode solicitar ações, mas não deve conhecer tokens nem endpoints sensíveis.

Requisitos arquiteturais:

- registrar log de cada tentativa de envio;
- guardar status, destinatário, payload mínimo necessário, erro retornado e data/hora;
- permitir reenvio manual em caso de falha;
- permitir integração direta com Evolution API ou indireta via webhook n8n, conforme configuração do site.

## Limites do LMS

O LMS deve cuidar de curso, turma, aula, acesso, comunicação acadêmica e indicadores básicos. Ele não deve se tornar uma secretaria financeira completa.

Fora do escopo do LMS:

- gestão completa de mensalidades;
- conciliação bancária;
- cobrança recorrente;
- inadimplência detalhada;
- emissão fiscal;
- contratos, descontos e renegociação financeira;
- relatórios contábeis.

Dentro do escopo do LMS:

- total de alunos ativos;
- matrículas por curso ou turma;
- presença ou acesso em aulas ao vivo;
- engajamento básico em conteúdos;
- envios de WhatsApp por status;
- próximas aulas;
- erros operacionais relevantes para suporte.

## Modelo conceitual de dados

DocTypes customizados previstos, sujeitos a refinamento durante implementação:

- `Bruce Live Class`: representa uma aula ao vivo vinculada a curso, turma, professor, data/hora, sala Jitsi, link e status.
- `Bruce WhatsApp Message Log`: registra tentativas de envio, destinatário, origem, status, erro e possibilidade de reenvio.
- `Bruce Integration Settings`: armazena chaves de configuração não sensíveis e referências para valores sensíveis em site config ou variáveis de ambiente.
- `Bruce Admin KPI Snapshot`: opcional para consolidar métricas administrativas básicas quando consultas em tempo real ficarem caras.

Sempre que possível, relacionar os DocTypes customizados aos DocTypes nativos do LMS em vez de duplicar dados.

## Papéis e permissões

Papéis previstos:

- `Professor Bruce`: opera aulas, acessa turmas, inicia Jitsi e acompanha indicadores simples de sua rotina.
- `Aluno`: acessa cursos, aulas, links ao vivo e avisos.
- `Administrador LMS`: acompanha KPIs básicos, configura integrações e consulta logs operacionais.

O usuário `Administrator` não deve ser usado como usuário operacional do professor.

## Fluxos de integração

### Aula ao vivo

1. Professor ou administrador agenda aula no LMS customizado.
2. Backend gera `roomName` seguro e registra a aula.
3. Sistema cria ou monta o link Jitsi conforme configuração.
4. Alunos visualizam a aula no LMS quando ela estiver disponível.
5. Professor inicia a aula pelo painel.
6. Status e metadados operacionais são atualizados.

### Envio de WhatsApp

1. Evento acadêmico gera necessidade de comunicação, como aula agendada ou link disponível.
2. Backend cria solicitação de envio.
3. Integração chama n8n ou Evolution API.
4. Resultado é registrado em log.
5. Falhas ficam disponíveis para reenvio manual.

### KPIs administrativos básicos

1. Backend consulta dados do LMS e DocTypes customizados.
2. Métricas são agregadas para painel administrativo.
3. A interface mostra apenas indicadores operacionais do LMS.
4. Demandas financeiras completas são encaminhadas para sistema/processo externo.

## Segurança e configuração

- Não versionar `.env`, `site_config.json`, `common_site_config.json`, tokens, senhas ou API keys.
- Não enviar API keys para componentes Vue ou páginas públicas.
- Preferir APIs backend com checagem de permissão.
- Registrar logs suficientes para auditoria operacional sem armazenar dados sensíveis desnecessários.
- Validar permissões em toda ação de iniciar aula, gerar link, enviar WhatsApp e reenviar mensagem.

## Estratégia de evolução

O projeto deve evoluir em camadas pequenas:

1. documentação e decisões de arquitetura;
2. modelos de dados customizados;
3. integração Jitsi mínima;
4. logs e envio WhatsApp;
5. painel do professor;
6. KPIs administrativos básicos;
7. refinamento de UX, permissões, testes e observabilidade.
