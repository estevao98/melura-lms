# Implicações da LGPD para um SaaS educacional

## Fonte

- Documento: `lgpd.md`
- Páginas: não aplicável; fonte em Markdown sem paginação
- Seções/artigos usados como base: Art. 1º ao Art. 65, com foco em arts. 5º, 6º, 7º, 8º, 9º, 10, 14, 15, 16, 18, 19, 37, 41, 46, 48, 49 e 50
- Tema: tradução operacional da LGPD para produto SaaS educacional
- Tipo de conteúdo: síntese interna derivada da lei
- Observação: esta seção interpreta implicações técnicas e de produto. Não substitui análise jurídica profissional.

## Resumo curto

Para Zuno, a LGPD deve ser traduzida em regras de produto, arquitetura e operação. O ponto central não é apenas ter uma política de privacidade, mas conseguir demonstrar finalidade, minimização, segurança, transparência, atendimento aos direitos dos titulares e governança.

## Dados pessoais prováveis no produto

- Nome, e-mail, telefone e identificadores de usuário.
- Dados de acesso: curso, turma, status, datas, permissões e histórico.
- Dados pedagógicos: progresso, respostas, notas, participação, presença e atividade.
- Dados de comunicação: logs de WhatsApp, tentativas de envio, status e erros.
- Dados técnicos: IP, logs de autenticação, eventos de segurança e auditoria.
- Dados de responsável legal, se houver alunos crianças/adolescentes.
- Referências externas opacas vindas de SaaS financeiro, sem trazer payload financeiro completo.

## Regras de arquitetura recomendadas

- Decisões de autorização devem acontecer no backend.
- `frappe.session.user` deve ser a fonte do usuário autenticado.
- O frontend não deve decidir `student_user`, curso, turma ou escopo de acesso.
- Toda listagem de dados de aluno deve ser filtrada por usuário autenticado e acesso permitido.
- Logs devem ajudar suporte e auditoria sem armazenar segredos ou payloads completos.
- Dados financeiros devem permanecer no SaaS externo.
- Integrações com WhatsApp, Jitsi, IA ou SaaS financeiro devem ter escopo mínimo e controle de segredo.

## Funcionalidades que provavelmente serão necessárias

- Inventário de dados pessoais.
- Matriz de bases legais por fluxo.
- Política de privacidade.
- Processo de atendimento a titular.
- Processo de correção de dados.
- Processo de exportação de dados.
- Processo de eliminação, bloqueio ou anonimização.
- Registro de operações de tratamento.
- Plano de resposta a incidente.
- Canal de privacidade/encarregado quando aplicável.
- Mapa de suboperadores/provedores externos.
- Retenção de dados por tipo: conta, progresso, logs, respostas, comunicações e backups.

## Riscos prioritários para Zuno

- Aluno acessar dados, progresso ou respostas de outro aluno.
- Aluno bloqueado/expirado acessar conteúdo.
- Link de aula ao vivo vazar sem validação de acesso.
- Logs de WhatsApp armazenarem dados excessivos ou tokens.
- API retornar campos demais ao frontend.
- SaaS financeiro externo ativar acesso sem webhook verificado.
- Backup ou dump ser commitado por engano.
- Dados de menores de idade serem coletados sem regra clara.

## Controles mínimos antes de produção

- Permission audit completo.
- Segurança de secrets e `site_config.json`.
- Política de logs.
- Backup fora do Git.
- Restore testado.
- Política de privacidade.
- Registro de operações.
- Definição de controlador/operador.
- Rotina de incident response.
- Processo para direitos dos titulares.
- Fluxo para menores/responsável legal se houver esse público.

## Pendências ou decisões humanas

- Definir papéis jurídicos: Zuno, Professor Bruce, SaaS financeiro e provedores.
- Definir se o produto atenderá menores de idade e como coletará autorização de responsáveis.
- Definir canal público de privacidade.
- Definir quais dados podem ser anonimizados e quais precisam ser retidos.
- Definir se haverá IA externa e quais dados ela poderá processar.
