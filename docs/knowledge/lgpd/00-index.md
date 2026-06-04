# LGPD — Base de conhecimento em Markdown

Esta pasta organiza a Lei Geral de Proteção de Dados Pessoais (LGPD) em chunks semânticos para consulta por humanos, Codex e outros agentes de código.

> Observação: estes arquivos não substituem análise jurídica profissional. Eles servem como base técnica e operacional para produto, arquitetura, segurança e documentação.

## Estrutura

```txt
docs/knowledge/lgpd/
├── 00-index.md
├── source-map.md
├── raw-articles/
│   ├── art-001.md
│   ├── art-002.md
│   └── ...
└── topics/
    ├── 01-escopo-fundamentos-definicoes-principios.md
    ├── 02-bases-legais-consentimento-transparencia-legitimo-interesse.md
    └── ...
```

## Como usar com Codex

1. Leia este `00-index.md`.
2. Abra `source-map.md` para localizar os artigos relevantes.
3. Consulte apenas os chunks de `topics/` relacionados à tarefa.
4. Use `raw-articles/` quando precisar conferir o texto do artigo isolado.
5. Ao propor implementação, separe texto legal, interpretação técnica e decisão humana.

## Chunks temáticos

| Arquivo | Tema | Artigos / base | Uso principal |
| ------- | ---- | -------------- | ------------- |
| `topics/01-escopo-fundamentos-definicoes-principios.md` | Escopo, fundamentos, definições e princípios | 1, 2, 3, 4, 5, 6 | escopo, conceitos, glossário e princípios gerais |
| `topics/02-bases-legais-consentimento-transparencia-legitimo-interesse.md` | Bases legais, consentimento, transparência e legítimo interesse | 7, 8, 9, 10 | bases legais, consentimento, transparência e legítimo interesse |
| `topics/03-dados-sensiveis-criancas-adolescentes-termino.md` | Dados sensíveis, anonimização, crianças/adolescentes e término do tratamento | 11, 12, 13, 14, 15, 16 | dados sensíveis, menores, anonimização e retenção |
| `topics/04-direitos-dos-titulares.md` | Direitos dos titulares | 17, 18, 19, 20, 21, 22 | processos de acesso, correção, exportação, eliminação e revisão |
| `topics/05-tratamento-pelo-poder-publico.md` | Tratamento de dados pelo poder público | 23, 24, 25, 26, 27, 28, 29, 30, 31, 32 | parcerias públicas e compartilhamento com órgãos públicos |
| `topics/06-transferencia-internacional.md` | Transferência internacional de dados | 33, 34, 35, 36 | provedores internacionais, Jitsi/JaaS, IA, storage e suboperadores |
| `topics/07-agentes-encarregado-responsabilidade.md` | Controlador, operador, encarregado e responsabilidade | 37, 38, 39, 40, 41, 42, 43, 44, 45 | controlador, operador, DPO/encarregado, responsabilidade e registros |
| `topics/08-seguranca-incidentes-governanca.md` | Segurança, incidentes e governança | 46, 47, 48, 49, 50, 51 | security by design, incident response, governança e logs |
| `topics/09-sancoes-administrativas.md` | Sanções administrativas | 52, 53, 54 | risco regulatório e priorização de controles |
| `topics/10-anpd-conselho-nacional.md` | ANPD e Conselho Nacional de Proteção de Dados | 55, 55-A, 55-B, 55-C, 55-D, 55-E, 55-F, 55-G, 55-H, 55-I, 55-J, 55-K, 55-L, 55-M, 56, 58, 58-A, 58-B | competências da ANPD, guias, normas e procedimentos simplificados |
| `topics/11-disposicoes-finais-vigencia.md` | Disposições finais e vigência | 59, 60, 61, 62, 63, 64, 65 | fechamento normativo e revisão de outras normas |
| `topics/12-implicacoes-para-saas-educacional.md` | Implicações da LGPD para um SaaS educacional | 1-65 | tradução operacional para Melura/Frappe LMS |
| `topics/13-checklist-lgpd-melura.md` | Checklist LGPD para Melura / Frappe LMS | 1-65 | checklist prático de implementação e governança |

## Regra de ouro

O Codex não deve carregar a LGPD inteira para toda tarefa. Ele deve localizar o tema no índice, abrir os chunks relevantes e usar o mapa de fontes para rastrear os artigos usados.

## Próximos chunks recomendados

- `docs/lgpd/00-contexto-produto.md`: mapa de dados real do produto.
- `docs/lgpd/01-inventario-dados.md`: inventário por DocType e integração.
- `docs/lgpd/02-matriz-bases-legais.md`: base legal por fluxo.
- `docs/lgpd/03-processo-direitos-titular.md`: processo operacional de atendimento.
- `docs/lgpd/04-privacy-policy-draft.md`: rascunho de política de privacidade.
