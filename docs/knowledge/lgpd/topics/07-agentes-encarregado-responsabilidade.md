# Controlador, operador, encarregado e responsabilidade

## Fonte

- Documento: `lgpd.md`
- Páginas: não aplicável; fonte em Markdown sem paginação
- Seções/artigos: Art. 37, Art. 38, Art. 39, Art. 40, Art. 41, Art. 42, Art. 43, Art. 44, Art. 45
- Tema: Controlador, operador, encarregado e responsabilidade
- Tipo de conteúdo: Lei / referência jurídica
- Observação: este chunk é uma organização técnica da LGPD para consulta interna. Não substitui análise jurídica profissional.

## Resumo curto

Este chunk cobre registro de operações de tratamento, relatório de impacto, instruções entre controlador e operador, encarregado, responsabilidade e reparação de danos. É essencial para decidir papéis entre Melura, professor/curso, SaaS financeiro externo, provedores e eventuais clientes.

## Conteúdo extraído

```text
Art. 37. O controlador e o operador devem manter registro das operações de tratamento de dados pessoais que realizarem, especialmente quando baseado no legítimo interesse.

Art. 38. A autoridade nacional poderá determinar ao controlador que elabore relatório de impacto à proteção de dados pessoais, inclusive de dados sensíveis, referente a suas operações de tratamento de dados, nos termos de regulamento, observados os segredos comercial e industrial.

Parágrafo único. Observado o disposto no caput deste artigo, o relatório deverá conter, no mínimo, a descrição dos tipos de dados coletados, a metodologia utilizada para a coleta e para a garantia da segurança das informações e a análise do controlador com relação a medidas, salvaguardas e mecanismos de mitigação de risco adotados.

Art. 39. O operador deverá realizar o tratamento segundo as instruções fornecidas pelo controlador, que verificará a observância das próprias instruções e das normas sobre a matéria.

Art. 40. A autoridade nacional poderá dispor sobre padrões de interoperabilidade para fins de portabilidade, livre acesso aos dados e segurança, assim como sobre o tempo de guarda dos registros, tendo em vista especialmente a necessidade e a transparência.

Seção II
Do Encarregado pelo Tratamento de Dados Pessoais

Art. 41. O controlador deverá indicar encarregado pelo tratamento de dados pessoais.

§ 1º A identidade e as informações de contato do encarregado deverão ser divulgadas publicamente, de forma clara e objetiva, preferencialmente no sítio eletrônico do controlador.

§ 2º As atividades do encarregado consistem em:

I - aceitar reclamações e comunicações dos titulares, prestar esclarecimentos e adotar providências;

II - receber comunicações da autoridade nacional e adotar providências;

III - orientar os funcionários e os contratados da entidade a respeito das práticas a serem tomadas em relação à proteção de dados pessoais; e

IV - executar as demais atribuições determinadas pelo controlador ou estabelecidas em normas complementares.

§ 3º A autoridade nacional poderá estabelecer normas complementares sobre a definição e as atribuições do encarregado, inclusive hipóteses de dispensa da necessidade de sua indicação, conforme a natureza e o porte da entidade ou o volume de operações de tratamento de dados.

§ 4º (VETADO).    (Incluído pela Lei nº 13.853, de 2019)     Vigência

Seção III
Da Responsabilidade e do Ressarcimento de Danos

Art. 42. O controlador ou o operador que, em razão do exercício de atividade de tratamento de dados pessoais, causar a outrem dano patrimonial, moral, individual ou coletivo, em violação à legislação de proteção de dados pessoais, é obrigado a repará-lo.

§ 1º A fim de assegurar a efetiva indenização ao titular dos dados:

I - o operador responde solidariamente pelos danos causados pelo tratamento quando descumprir as obrigações da legislação de proteção de dados ou quando não tiver seguido as instruções lícitas do controlador, hipótese em que o operador equipara-se ao controlador, salvo nos casos de exclusão previstos no art. 43 desta Lei;

II - os controladores que estiverem diretamente envolvidos no tratamento do qual decorreram danos ao titular dos dados respondem solidariamente, salvo nos casos de exclusão previstos no art. 43 desta Lei.

§ 2º O juiz, no processo civil, poderá inverter o ônus da prova a favor do titular dos dados quando, a seu juízo, for verossímil a alegação, houver hipossuficiência para fins de produção de prova ou quando a produção de prova pelo titular resultar-lhe excessivamente onerosa.

§ 3º As ações de reparação por danos coletivos que tenham por objeto a responsabilização nos termos do caput deste artigo podem ser exercidas coletivamente em juízo, observado o disposto na legislação pertinente.

§ 4º Aquele que reparar o dano ao titular tem direito de regresso contra os demais responsáveis, na medida de sua participação no evento danoso.

Art. 43. Os agentes de tratamento só não serão responsabilizados quando provarem:

I - que não realizaram o tratamento de dados pessoais que lhes é atribuído;

II - que, embora tenham realizado o tratamento de dados pessoais que lhes é atribuído, não houve violação à legislação de proteção de dados; ou

III - que o dano é decorrente de culpa exclusiva do titular dos dados ou de terceiro.

Art. 44. O tratamento de dados pessoais será irregular quando deixar de observar a legislação ou quando não fornecer a segurança que o titular dele pode esperar, consideradas as circunstâncias relevantes, entre as quais:

I - o modo pelo qual é realizado;

II - o resultado e os riscos que razoavelmente dele se esperam;

III - as técnicas de tratamento de dados pessoais disponíveis à época em que foi realizado.

Parágrafo único. Responde pelos danos decorrentes da violação da segurança dos dados o controlador ou o operador que, ao deixar de adotar as medidas de segurança previstas no art. 46 desta Lei, der causa ao dano.

Art. 45. As hipóteses de violação do direito do titular no âmbito das relações de consumo permanecem sujeitas às regras de responsabilidade previstas na legislação pertinente.

CAPÍTULO VII
DA SEGURANÇA E DAS BOAS PRÁTICAS

Seção I
Da Segurança e do Sigilo de Dados
```

## Pontos importantes para o SaaS

- Controlador e operador devem manter registro das operações de tratamento, especialmente quando baseado em legítimo interesse.
- A autoridade nacional pode determinar relatório de impacto.
- O operador deve tratar dados conforme instruções do controlador.
- O controlador deve indicar encarregado, salvo hipóteses futuras de dispensa/regulamentação.
- Controlador e operador podem ser responsabilizados por danos decorrentes de tratamento irregular.
- Tratamento irregular inclui deixar de observar a legislação ou não fornecer segurança esperada pelo titular.

## Implicações técnicas

- Definir se o curso/professor é controlador e se Melura atua como operador em cenários futuros.
- Manter registro das operações de tratamento dentro do produto e dos processos externos.
- Criar contato público de privacidade/encarregado quando necessário.
- Criar contratos/instruções para operadores: hospedagem, WhatsApp, Jitsi/JaaS, e-mail, IA, analytics, backup.
- Criar procedimento de relatório de impacto para tratamentos de maior risco.

## Pendências ou decisões humanas

- Definir papéis jurídicos de Melura, Professor Bruce e SaaS financeiro externo.
- Definir encarregado/canal oficial.
- Criar registro de operações de tratamento simplificado.
