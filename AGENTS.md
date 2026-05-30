# AGENTS.md — bruce_lms_custom

## Objetivo

Customizar o Frappe Learning/LMS para um curso online de Ciências Humanas/ENEM, com aulas ao vivo via Jitsi, envio de links por WhatsApp e interface em português brasileiro.

## Regra principal

Não modificar diretamente o core do Frappe, Frappe LMS ou Frappe UI sem justificar. Preferir extensões, DocTypes, hooks, páginas e componentes dentro da app bruce_lms_custom.

## Segurança

- Nunca commitar .env, site_config.json, common_site_config.json, tokens, senhas ou API keys.
- Não expor API key no frontend.
- Usar variáveis de ambiente ou site config.
- Não usar Administrator como usuário operacional do professor.

## UI

- Usar Frappe UI sempre que possível.
- Toda interface deve estar em português brasileiro.
- Manter fluxo simples para professor não técnico.

## Jitsi

- Gerar roomName único e não previsível.
- Salvar link, turma, curso, professor, data e status.
- Permitir iniciar aula e entrar na aula pelo LMS.
- Usar Jitsi IFrame API.

## WhatsApp

- Envio deve acontecer no backend ou via n8n.
- Registrar log de envio.
- Permitir reenvio manual em caso de falha.

## Git

- Fazer commits pequenos.
- Trabalhar em branches feature/*.
- Ao final de cada tarefa, listar arquivos alterados e motivo.
