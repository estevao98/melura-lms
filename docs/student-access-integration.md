# Integração de acesso pedagógico do aluno

Esta integração futura existe para sincronizar o SaaS financeiro externo com o
Frappe LMS. O Frappe não implementa cobrança, assinatura, captação, blog,
newsletter ou CRM.

## Fonte de verdade no Frappe

O DocType customizado `Bruce Student Access` representa a liberação pedagógica.

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

## Backend esperado

A integração deve chamar endpoint backend protegido. Esse endpoint ainda será
definido, mas deve:

- autenticar a origem;
- validar payload mínimo;
- resolver aluno, curso e turma no backend;
- criar ou atualizar `Bruce Student Access`;
- registrar erro resumido sem expor segredo;
- nunca depender de parâmetros do frontend do aluno.

As APIs de aluno, como `/app/minha-aula`, a listagem inicial de questões ENEM e
as listas de exercícios, devem consultar aulas, materiais, questões e listas a
partir do usuário logado e do `Bruce Student Access`. O frontend não deve enviar
escopo de curso, turma ou aluno para ampliar acesso.

Até essa etapa ser implementada, o acesso pode ser mantido manualmente por
usuários administrativos autorizados.
