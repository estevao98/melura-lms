# Base de tradução e linguagem pt-BR

## Objetivo

Esta base define o padrão inicial de idioma para a app `melura_lms`. Toda nova interface, mensagem de erro, ação, log visível ao usuário e documentação funcional criada nesta app deve usar português brasileiro.

Esta app não deve alterar traduções globais do Frappe LMS, Frappe Framework, Frappe UI ou qualquer outro app de core. Traduções e textos específicos do produto devem ficar dentro de `melura_lms`.

## Termos oficiais do produto

| Inglês | Português brasileiro |
| --- | --- |
| Course | Curso |
| Lesson | Aula |
| Batch | Turma |
| Assignment | Atividade |
| Live Class | Aula ao vivo |
| Student | Aluno |
| Instructor | Professor |
| Enrollment | Matrícula |
| Dashboard | Painel |

## Regras para novas strings em Python

Novas strings exibidas ao usuário em código Python devem usar a função de tradução do Frappe:

```python
from frappe import _

_("Texto")
```

Exemplo:

```python
from frappe import _

frappe.throw(_("Você não tem permissão para iniciar esta aula."))
```

Não montar frases traduzíveis com concatenação quando isso dificultar a tradução. Prefira placeholders:

```python
_("Aula {0} agendada com sucesso.").format(titulo)
```

## Regras para novas strings em JS/Vue

Novas strings exibidas ao usuário em JavaScript ou Vue devem usar a função global de tradução:

```js
__("Texto")
```

Exemplo:

```js
frappe.msgprint(__("Aula agendada com sucesso."))
```

Em componentes Vue, manter labels, mensagens vazias, erros e ações em português brasileiro e envolver strings novas com `__()` quando forem renderizadas ao usuário.

## Arquivo de tradução da app

O diretório `melura_lms/translations` guarda traduções específicas desta app.

O arquivo inicial `melura_lms/translations/pt-BR.csv` usa o formato padrão de CSV de traduções do Frappe:

```csv
Texto original,Texto traduzido,contexto
```

O terceiro campo pode ficar vazio quando não houver contexto específico.

## Tradução por CSV x dados salvos

O CSV de tradução é aplicado quando o Frappe renderiza uma string por meio do mecanismo de tradução, como `_()` em Python, `__()` em JavaScript ou labels traduzíveis carregados pelo framework. Esse caminho é adequado para textos visíveis de menus, botões, mensagens, estados e títulos que passam pelo tradutor.

Alguns textos do Desk podem estar salvos como dados no banco, especialmente em Workspaces, atalhos, cards, Dashboard Charts, Number Cards e fixtures de outros apps. Nesses casos, adicionar a entrada ao CSV pode não alterar o texto já persistido. Se labels como `Learning`, `Tools`, `New Signups`, `Course Enrollments`, `Certification`, `Course Data`, `Course Stats`, `Review` ou `Evaluation Request` continuarem aparecendo em inglês no Workspace Learning depois de limpar cache e atualizar traduções, uma etapa futura pode exigir override de Workspace/fixtures dentro de `melura_lms`, sem modificar o core do Frappe ou do LMS.

## Interface, não nomes internos

As traduções devem cobrir apenas textos visíveis para o usuário: rótulos, menus, botões, mensagens, estados e textos de ajuda.

Não traduzir nomes internos usados pelo código ou pelo framework, como nomes de DocTypes, fieldnames, rotas, métodos Python, imports, chaves de configuração, IDs, nomes de arquivos ou nomes técnicos exigidos por integrações. Quando um texto em inglês aparecer na interface, adicionar a tradução em `melura_lms/translations/pt-BR.csv` ou envolver a nova string com `_()` em Python e `__()` em JavaScript.

## Diretrizes de linguagem

- Usar frases curtas e diretas.
- Preferir termos operacionais simples para professor e aluno.
- Evitar jargões técnicos fora de telas administrativas e logs.
- Usar `Aula ao vivo` para experiências de Google Meet visíveis ao usuário.
- Usar `Painel` em vez de `Dashboard` nas interfaces.
- Usar `Professor` para o papel operacional de instrutor.
- Usar `Aluno` para usuários matriculados.

## Limites

- Não alterar traduções globais do Frappe LMS.
- Não modificar arquivos em `frappe/`, `lms/` ou `frappe-ui/`.
- Não implementar frontend nesta etapa.
- Não criar DocTypes nesta etapa.
