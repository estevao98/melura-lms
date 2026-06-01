# Segurança

Este projeto customiza o Frappe LMS para operação acadêmica do curso do professor Bruce. A regra de segurança principal é simples: segredos ficam fora do repositório e operações sensíveis passam pelo backend com validação de permissão.

## Arquivos que não devem ser commitados

Nunca versionar:

- `.env` real de ambiente;
- `site_config.json`;
- `common_site_config.json`;
- tokens;
- senhas;
- API keys;
- dumps de banco;
- backups de sites;
- arquivos com dados reais de alunos;
- payloads completos de integrações contendo dados sensíveis.

O arquivo `.env.example` pode existir no repositório porque deve conter apenas nomes de variáveis e exemplos não sensíveis.

## Segredos e configuração

Valores sensíveis devem ser configurados por:

- variáveis de ambiente;
- `site_config.json` do site;
- mecanismo seguro equivalente aprovado para o ambiente.

Exemplos de valores sensíveis:

- `EVOLUTION_API_KEY`;
- tokens de webhook;
- credenciais de provedores;
- URLs internas protegidas;
- chaves de assinatura;
- senhas de usuários técnicos.

Valores não sensíveis, como domínio público do Jitsi ou prefixo de sala, podem ser documentados, mas ainda devem ser configuráveis por ambiente.

## API keys no frontend

API keys nunca devem ser enviadas para:

- componentes Vue;
- páginas públicas;
- HTML renderizado para aluno ou professor;
- respostas de APIs usadas pelo navegador;
- logs acessíveis por usuários sem permissão técnica.

O frontend pode acionar uma ação, como `Enviar aviso` ou `Reenviar WhatsApp`, mas a chamada ao provedor deve acontecer no backend ou em fluxo n8n protegido.

## Jitsi

As salas Jitsi devem usar `roomName` único e não previsível.

Boas práticas:

- gerar o nome da sala no backend;
- salvar curso, turma, professor, data, link e status;
- validar permissão antes de iniciar aula;
- validar matrícula antes de liberar entrada do aluno;
- evitar expor configurações internas desnecessárias ao navegador;
- não reutilizar nomes previsíveis como turma, curso ou data pura.

## WhatsApp, Evolution API e n8n

O envio deve ocorrer no backend ou por webhook n8n protegido.

Boas práticas:

- guardar token da Evolution API fora do repositório;
- não exibir endpoint sensível para professor ou aluno;
- registrar tentativa de envio com status, data/hora e erro resumido;
- evitar salvar conteúdo sensível desnecessário no log;
- permitir reenvio manual apenas para usuário autorizado;
- preservar histórico da falha original.

## Usuários e permissões

O usuário `Administrator` não deve ser usado como conta operacional do professor.

Contas devem ser separadas por responsabilidade:

- Root Técnico para manutenção e configuração sensível;
- Professor para operação acadêmica;
- Administrador LMS para KPIs, logs e configurações operacionais;
- Integração/Bot para automações.

Ações críticas devem validar permissão no backend:

- iniciar aula;
- cancelar aula;
- gerar ou recriar link;
- enviar WhatsApp;
- reenviar mensagem;
- consultar logs detalhados;
- alterar configurações de integração.

## Onboarding e acesso pedagógico de alunos

O Frappe LMS não deve implementar cobrança, assinatura, captação, blog,
newsletter ou CRM. Esses fluxos pertencem ao SaaS externo definido para a
operação financeira/comercial.

Dentro do Frappe, o acesso pedagógico do aluno é controlado pela camada
customizada `Bruce Student Access`, com os status:

- `Pendente`;
- `Ativo`;
- `Bloqueado`;
- `Expirado`.

Regras de segurança:

- páginas customizadas do aluno devem validar o usuário logado no backend;
- aluno só pode ver aulas vinculadas ao curso ou turma liberados em
  `Bruce Student Access`;
- parâmetros vindos do frontend não podem definir aluno, turma, curso ou
  escopo de acesso;
- `Bruce Live Class` usa permissões scripted para impedir leitura ampla por
  `LMS Student`;
- o link Jitsi só deve ser retornado por APIs que validem status ativo e vínculo
  pedagógico;
- `Pendente`, `Bloqueado` e `Expirado` não liberam aula.

## Materiais educacionais

`Bruce Educational Material` segue a mesma fonte segura de acesso pedagógico:
`Bruce Student Access`.

Regras de segurança:

- materiais para aluno devem estar publicados e com visibilidade `Aluno`;
- `published_at` é preenchido no backend quando o material é publicado;
- páginas e APIs do aluno não recebem aluno, curso ou turma como parâmetros de
  liberação;
- aluno só recebe materiais compatíveis com seu acesso ativo por turma ou curso;
- materiais com visibilidade `Professor` ou `Interno` não são retornados para
  `LMS Student`;
- `Pendente`, `Bloqueado` e `Expirado` não liberam materiais.

Integrações futuras com SaaS financeiro externo devem atualizar apenas o status
pedagógico e referências opacas. Não salvar tokens, dados de cartão, payloads
financeiros completos ou segredos em `Bruce Student Access`.

## Logs

Logs devem ajudar na auditoria operacional sem virar depósito de dados sensíveis.

Registrar:

- origem da ação;
- usuário responsável quando aplicável;
- data/hora;
- status;
- destinatário mínimo necessário;
- erro resumido do provedor;
- referência para aula, curso ou turma.

Evitar registrar:

- API keys;
- tokens;
- senhas;
- headers de autenticação;
- payloads completos com dados pessoais quando um resumo bastar.

## Revisão antes de commit

Antes de commitar, verificar:

- nenhum arquivo sensível foi adicionado;
- `.env` real não aparece no diff;
- `site_config.json` e `common_site_config.json` não aparecem no diff;
- tokens não aparecem em código, documentação ou testes;
- novas APIs validam permissão no backend;
- textos de erro não expõem detalhes internos sensíveis;
- usuário professor não depende de `Administrator`.

## Incidente ou vazamento

Se uma credencial for commitada ou exposta:

1. revogar ou rotacionar a credencial imediatamente;
2. remover o segredo do código e da configuração versionada;
3. revisar logs e acessos relacionados;
4. registrar a decisão de correção;
5. evitar reutilizar a credencial antiga.
