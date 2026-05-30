# Roadmap do bruce_lms_custom

## Objetivo do produto

Entregar uma customização limpa do Frappe LMS para o curso de Ciências Humanas/ENEM do professor Bruce, com aulas ao vivo via Jitsi, comunicação por WhatsApp via Evolution API/n8n, painel simples para o professor e KPIs administrativos básicos.

O roadmap não inclui implementação de uma secretaria financeira completa dentro do LMS.

## Fase 0: Alinhamento e documentação

Status: iniciado

Entregas:

- documentar arquitetura como Frappe LMS limpo + app customizada;
- registrar limites entre LMS, comunicação e financeiro;
- descrever fluxos principais de professor, aluno e administração;
- manter decisões em português brasileiro.

Critérios de aceite:

- `ARCHITECTURE.md` descreve componentes, limites e integrações;
- `ROADMAP.md` orienta a sequência de implementação;
- `docs/ux-flows.md` descreve os fluxos de uso principais.

## Fase 1: Fundação da app customizada

Entregas:

- revisar hooks existentes da app;
- definir papéis operacionais sem usar `Administrator` como professor;
- criar DocTypes customizados mínimos para aula ao vivo, logs de WhatsApp e configurações;
- preparar permissões para professor, aluno e administrador LMS.

Critérios de aceite:

- dados customizados ficam dentro de `bruce_lms_custom`;
- não há alteração direta em `frappe/`, `lms/`, `frappe-ui/` ou `jitsi-meet/`;
- permissões impedem alunos de acessar operações administrativas.

## Fase 2: Aulas ao vivo com Jitsi

Entregas:

- gerar `roomName` único e não previsível no backend;
- salvar aula ao vivo com curso, turma, professor, data/hora, link e status;
- criar ação para professor iniciar aula;
- criar ação para aluno entrar na aula pelo LMS;
- integrar Jitsi IFrame API na experiência de aula.

Critérios de aceite:

- professor consegue iniciar uma aula sem operação técnica;
- aluno acessa a aula correta a partir do LMS;
- link e status ficam registrados;
- nenhuma credencial sensível aparece no frontend.

## Fase 3: WhatsApp via Evolution API ou n8n

Entregas:

- definir configuração de provedor: Evolution API direta ou webhook n8n;
- enviar mensagens pelo backend ou por fluxo n8n;
- registrar logs de envio;
- permitir reenvio manual de mensagens com falha;
- criar mensagens em português brasileiro para avisos de aula.

Critérios de aceite:

- envios não expõem tokens no frontend;
- cada tentativa fica auditável;
- falhas mostram motivo e opção de reenvio para usuário autorizado;
- fluxo suporta troca entre Evolution API e n8n por configuração.

## Fase 4: Painel simples do professor

Entregas:

- listar próximas aulas;
- exibir status de aula ao vivo;
- permitir iniciar aula;
- permitir consultar turma e links principais;
- destacar falhas relevantes de comunicação relacionadas às aulas.

Critérios de aceite:

- interface em português brasileiro;
- fluxo é claro para professor não técnico;
- ações críticas exigem permissão;
- tela usa Frappe UI sempre que possível.

## Fase 5: Painel administrativo básico de KPIs

Entregas:

- exibir alunos ativos;
- exibir matrículas por curso ou turma;
- exibir próximas aulas e aulas realizadas;
- exibir status de envios WhatsApp;
- exibir falhas operacionais recentes;
- opcionalmente consolidar snapshots se consultas em tempo real ficarem custosas.

Critérios de aceite:

- painel cobre somente indicadores básicos do LMS;
- não há módulo de secretaria financeira completa;
- indicadores ajudam operação acadêmica e suporte;
- dados respeitam permissões.

## Fase 6: Qualidade, segurança e operação

Entregas:

- testes focados em geração de sala Jitsi, permissões e logs de WhatsApp;
- checklist de segurança para configurações sensíveis;
- validação de textos em português brasileiro;
- documentação de configuração por ambiente;
- revisão de erros e logs operacionais.

Critérios de aceite:

- fluxos críticos têm cobertura mínima;
- segredos seguem fora do repositório;
- usuário operacional do professor não é `Administrator`;
- documentação orienta instalação e manutenção.

## Itens fora do escopo inicial

- secretaria financeira completa;
- cobrança recorrente;
- conciliação bancária;
- emissão fiscal;
- aplicativo mobile nativo;
- customizações diretas no core do Frappe, Frappe LMS, Frappe UI ou Jitsi Meet;
- automações avançadas de marketing.

## Marcos sugeridos

- M1: documentação e escopo fechados.
- M2: modelos e permissões customizadas.
- M3: aula ao vivo funcional com Jitsi.
- M4: WhatsApp com log e reenvio.
- M5: painel do professor.
- M6: KPIs administrativos básicos.
- M7: revisão de segurança, testes e documentação operacional.
