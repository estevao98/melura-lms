# bruce_lms_custom

Customizações do Frappe LMS para o curso online de Ciências Humanas/ENEM do professor Bruce.

O objetivo desta app é manter o Frappe LMS limpo e atualizável, concentrando as regras específicas do curso, integrações e telas operacionais dentro de `bruce_lms_custom`.

## Escopo do projeto

O projeto deve apoiar:

- aulas ao vivo via Jitsi;
- envio de avisos e links por WhatsApp via backend, Evolution API ou n8n;
- painel simples para o professor;
- experiência do aluno em português brasileiro;
- KPIs administrativos básicos do LMS;
- logs operacionais para suporte e reenvio de mensagens com falha.

O projeto não deve virar uma secretaria financeira completa. Cobrança recorrente, conciliação bancária, emissão fiscal, contratos financeiros e inadimplência detalhada ficam fora do escopo inicial.

## Regra principal

Não modificar diretamente o core do Frappe, Frappe LMS, Frappe UI ou Jitsi Meet sem justificativa técnica explícita.

Diretórios que devem permanecer limpos:

- `frappe/`
- `lms/`
- `frappe-ui/`
- `jitsi-meet/`

Customizações devem ser feitas dentro desta app usando hooks, DocTypes próprios, permissões, páginas, componentes, APIs backend e configurações por site.

## Estrutura esperada

- `bruce_lms_custom/`: código da app customizada.
- `bruce_lms_custom/hooks.py`: pontos de integração com o Frappe.
- `bruce_lms_custom/config/`: configurações de módulo e navegação.
- `bruce_lms_custom/public/`: assets públicos da app.
- `bruce_lms_custom/templates/`: templates web quando necessários.
- `docs/`: documentação funcional, técnica, UX, segurança e testes.
- `ARCHITECTURE.md`: visão arquitetural e limites do projeto.
- `ROADMAP.md`: fases de evolução.
- `AGENTS.md`: regras operacionais para agentes e contribuidores.
- `.env.example`: exemplo de variáveis esperadas para integrações locais.

## Como rodar localmente

Pré-requisitos:

- bench do Frappe instalado;
- ambiente Frappe/Frappe LMS funcional;
- site local criado no bench;
- app `lms` instalada no site antes ou junto desta customização.

Exemplo de instalação em um bench local:

```bash
cd /caminho/para/frappe-bench
bench get-app URL_DO_REPOSITORIO --branch develop
bench --site nome-do-site install-app bruce_lms_custom
bench --site nome-do-site migrate
bench start
```

Em um ambiente onde a app já está dentro de `apps/bruce_lms_custom`, normalmente basta instalar no site e migrar:

```bash
cd /caminho/para/frappe-bench
bench --site nome-do-site install-app bruce_lms_custom
bench --site nome-do-site migrate
bench start
```

Configurações sensíveis devem ser definidas por variável de ambiente ou `site_config.json`, nunca em arquivos versionados. Use `.env.example` apenas como referência de nomes.

## Configuração de integrações

Jitsi:

- `JITSI_DOMAIN`
- `JITSI_ROOM_PREFIX`

WhatsApp/Evolution API:

- `EVOLUTION_API_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE_NAME`
- `WHATSAPP_DEFAULT_COUNTRY_CODE`

Tokens, senhas e API keys não devem ser expostos no frontend. Chamadas para Jitsi, WhatsApp, n8n ou Evolution API devem passar por backend com validação de permissão.

## Papéis principais

- Root Técnico: manutenção técnica e configuração sensível.
- Professor: inicia aulas, acompanha turmas e consulta avisos operacionais.
- Aluno: acessa cursos, conteúdos e aulas ao vivo.
- Administrador LMS: acompanha KPIs básicos, logs e configurações operacionais.
- Integração/Bot: usuário técnico para automações e integrações.

O usuário `Administrator` não deve ser usado como usuário operacional do professor.

## Documentação relacionada

- `ARCHITECTURE.md`: arquitetura e limites.
- `ROADMAP.md`: fases de implementação.
- `docs/ux-flows.md`: fluxos de professor, aluno e administração.
- `docs/design-system.md`: padrões simples de UI.
- `docs/roles-permissions.md`: papéis e permissões.
- `docs/testing-checklist.md`: validações manuais e futuras automações.
- `SECURITY.md`: práticas de segurança e gestão de segredos.

## Desenvolvimento

Antes de qualquer mudança:

1. confirme que a alteração pertence à app `bruce_lms_custom`;
2. evite mudanças diretas em core;
3. mantenha textos de interface em português brasileiro;
4. valide permissões em ações críticas;
5. não versione segredos.

O projeto usa `pre-commit` para formatação e lint quando houver implementação de código:

```bash
cd apps/bruce_lms_custom
pre-commit install
```

Ferramentas configuradas:

- ruff
- eslint
- prettier
- pyupgrade

## Licença

MIT.
