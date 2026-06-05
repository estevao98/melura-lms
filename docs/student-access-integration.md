# Integração de acesso pedagógico do aluno

Esta integração futura existe para sincronizar o SaaS financeiro externo com o
Frappe LMS. O Frappe não implementa cobrança, assinatura, captação, blog,
newsletter ou CRM.

## Fonte de verdade no Frappe

O DocType customizado Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`) representa a liberação pedagógica.

Status permitidos:

- `Pendente`;
- `Ativo`;
- `Bloqueado`;
- `Expirado`.

Somente `Ativo`, dentro do período configurado, libera aulas, materiais,
questões publicadas e listas de exercícios para o aluno.

## Escopo de acesso

Cada registro deve apontar para:

- `student`: usuário do aluno no Frappe;
- `batch`: turma LMS, quando disponível;
- `course`: curso LMS, quando a liberação for por curso;
- `starts_on` e `expires_on`, quando houver janela de acesso;
- `external_reference`, quando o SaaS precisar guardar uma referência opaca.

Quando `batch` estiver preenchida, a liberação de aulas fica restrita à turma.
Para materiais educacionais, o aluno com acesso por turma vê materiais da
própria turma e materiais gerais do mesmo curso sem turma específica. Quando
somente `course` estiver preenchido, a liberação cobre aulas e materiais daquele
curso.

Para questões ENEM, o aluno com acesso por turma vê questões da própria turma e
questões gerais do mesmo curso sem turma específica. Quando somente `course`
estiver preenchido, a liberação cobre questões publicadas daquele curso.

Para listas de exercícios, a regra é a mesma de materiais e questões: o aluno
com acesso por turma vê listas da própria turma e listas gerais do mesmo curso
sem turma específica. Quando somente `course` estiver preenchido, a liberação
cobre listas publicadas daquele curso. Respostas de aluno são salvas no backend
para o usuário logado, sem aceitar `student_user` vindo do frontend.

## Dados proibidos

Não enviar nem salvar no Frappe:

- API keys;
- tokens;
- dados de cartão;
- payload financeiro completo;
- senha;
- segredo de webhook;
- dados comerciais desnecessários para liberar aula.

## Backend implementado

A integração deve chamar endpoint backend protegido:

```text
melura_lms.services.external_student_status.handle_external_student_status
```

Esse endpoint deve:

- autenticar a origem;
- validar assinatura HMAC antes de processar o payload;
- validar payload mínimo;
- localizar um registro existente de Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`) por referência
  segura;
- atualizar apenas status pedagógico e referência opaca existente;
- rejeitar payload financeiro amplo;
- retornar resposta mínima sem expor segredo;
- nunca depender de parâmetros do frontend do aluno.

Esta fundação não cria registros novos de acesso, não persiste histórico de
eventos externos e não implementa lógica de cobrança, checkout, assinatura,
CRM, blog, newsletter ou captação de leads.

As APIs de aluno, como `/app/minha-aula`, a listagem inicial de questões ENEM e
as listas de exercícios, devem consultar aulas, materiais, questões e listas a
partir do usuário logado e do Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`). O frontend não deve enviar
escopo de curso, turma ou aluno para ampliar acesso.

O acesso também pode continuar sendo mantido manualmente por usuários
administrativos autorizados quando a integração externa não estiver configurada.
