# Base de tradução e linguagem pt-BR

## Objetivo

Esta base define o padrão inicial de idioma para a app `bruce_lms_custom`. Toda nova interface, mensagem de erro, ação, log visível ao usuário e documentação funcional criada nesta app deve usar português brasileiro.

Esta app não deve alterar traduções globais do Frappe LMS, Frappe Framework, Frappe UI ou qualquer outro app de core. Traduções e textos específicos do produto devem ficar dentro de `bruce_lms_custom`.

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

O diretório `bruce_lms_custom/translations` guarda traduções específicas desta app.

O arquivo inicial `bruce_lms_custom/translations/pt-BR.csv` usa o formato padrão de CSV de traduções do Frappe:

```csv
Texto original,Texto traduzido,contexto
```

O terceiro campo pode ficar vazio quando não houver contexto específico.

## Diretrizes de linguagem

- Usar frases curtas e diretas.
- Preferir termos operacionais simples para professor e aluno.
- Evitar jargões técnicos fora de telas administrativas e logs.
- Usar `Aula ao vivo` para experiências Jitsi visíveis ao usuário.
- Usar `Painel` em vez de `Dashboard` nas interfaces.
- Usar `Professor` para o papel operacional de instrutor.
- Usar `Aluno` para usuários matriculados.

## Limites

- Não alterar traduções globais do Frappe LMS.
- Não modificar arquivos em `frappe/`, `lms/`, `frappe-ui/` ou `jitsi-meet/`.
- Não implementar frontend nesta etapa.
- Não criar DocTypes nesta etapa.
