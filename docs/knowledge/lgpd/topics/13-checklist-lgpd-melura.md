# Checklist LGPD para Melura / Frappe LMS

## Fonte

- Documento: `lgpd.md`
- Páginas: não aplicável; fonte em Markdown sem paginação
- Seções/artigos usados como base: LGPD completa, com foco em princípios, bases legais, direitos dos titulares, crianças/adolescentes, agentes de tratamento, segurança, incidentes e governança
- Tema: checklist operacional
- Tipo de conteúdo: checklist interno derivado da lei
- Observação: este checklist ajuda priorização técnica e operacional. Não substitui parecer jurídico.

## Produto e governança

- [ ] Definir se Melura/professor atua como controlador, operador ou ambos em cada fluxo.
- [ ] Criar inventário de dados pessoais por DocType/tabela/integração.
- [ ] Criar matriz de base legal por finalidade.
- [ ] Criar política de privacidade em português brasileiro.
- [ ] Criar canal de privacidade/encarregado quando aplicável.
- [ ] Definir processo de atualização regulatória.

## Dados e minimização

- [ ] Coletar apenas dados necessários para acesso, aula, suporte, progresso e operação.
- [ ] Separar dados pedagógicos do SaaS financeiro externo.
- [ ] Evitar dados sensíveis salvo necessidade justificada.
- [ ] Definir retenção por tipo de dado.
- [ ] Definir anonimização/bloqueio/eliminação quando aplicável.

## Direitos dos titulares

- [ ] Processo para confirmar tratamento.
- [ ] Processo para exportar/acessar dados.
- [ ] Processo para corrigir dados.
- [ ] Processo para eliminar, bloquear ou anonimizar dados.
- [ ] Processo para registrar e responder solicitações.
- [ ] Processo para informar compartilhamentos relevantes.

## Segurança técnica

- [ ] Validar autorização no backend.
- [ ] Garantir que `student_user` venha de `frappe.session.user`.
- [ ] Impedir acesso cruzado entre alunos/turmas/cursos.
- [ ] Bloquear acesso pedagógico para `Pendente`, `Bloqueado` e `Expirado`.
- [ ] Proteger links de aula do Google Meet.
- [ ] Manter secrets fora do Git e fora do frontend.
- [ ] Evitar logs com tokens, senhas, payloads completos ou dados excessivos.
- [ ] Proteger arquivos privados.
- [ ] Fazer backup fora do repositório.
- [ ] Testar restore.

## Integrações

- [ ] Mapear provedores: Google Meet, Evolution API, n8n, hospedagem, e-mail, storage, IA.
- [ ] Registrar país/local de processamento quando relevante.
- [ ] Validar webhooks do SaaS externo com assinatura/segredo.
- [ ] Tornar webhook de acesso idempotente.
- [ ] Não armazenar cartão, transação completa ou payload financeiro no LMS.
- [ ] Registrar apenas referência externa opaca e status pedagógico.

## Menores de idade

- [ ] Definir se o produto atende crianças/adolescentes.
- [ ] Se houver crianças, definir consentimento específico e destacado do responsável.
- [ ] Exibir informações claras e acessíveis sobre dados coletados e uso.
- [ ] Evitar exigir dados além do necessário para participação.

## Incidentes

- [ ] Criar plano de resposta a incidente.
- [ ] Definir quem confirma, contém, comunica e corrige.
- [ ] Definir critérios de comunicação à ANPD e titulares.
- [ ] Criar checklist de rotação de segredos.
- [ ] Registrar incidentes e medidas corretivas.

## Evidências de prestação de contas

- [ ] Guardar histórico de decisões de privacidade.
- [ ] Documentar permissões e auditorias.
- [ ] Documentar medidas técnicas e administrativas.
- [ ] Documentar testes de acesso e bloqueio.
- [ ] Documentar políticas internas e revisões.
