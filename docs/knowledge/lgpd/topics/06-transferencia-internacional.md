# Transferência internacional de dados

## Fonte

- Documento: `lgpd.md`
- Páginas: não aplicável; fonte em Markdown sem paginação
- Seções/artigos: Art. 33, Art. 34, Art. 35, Art. 36
- Tema: Transferência internacional de dados
- Tipo de conteúdo: Lei / referência jurídica
- Observação: este chunk é uma organização técnica da LGPD para consulta interna. Não substitui análise jurídica profissional.

## Resumo curto

Este chunk aborda quando a transferência internacional de dados pessoais é permitida e quais garantias podem ser exigidas. Para um SaaS educacional, isto se conecta ao uso de provedores externos, hospedagem, analytics, e-mail, WhatsApp, Jitsi, IA, storage ou qualquer serviço fora do Brasil.

## Conteúdo extraído

```text
Art. 33. A transferência internacional de dados pessoais somente é permitida nos seguintes casos:

I - para países ou organismos internacionais que proporcionem grau de proteção de dados pessoais adequado ao previsto nesta Lei;

II - quando o controlador oferecer e comprovar garantias de cumprimento dos princípios, dos direitos do titular e do regime de proteção de dados previstos nesta Lei, na forma de:

a) cláusulas contratuais específicas para determinada transferência;

b) cláusulas-padrão contratuais;

c) normas corporativas globais;

d) selos, certificados e códigos de conduta regularmente emitidos;

III - quando a transferência for necessária para a cooperação jurídica internacional entre órgãos públicos de inteligência, de investigação e de persecução, de acordo com os instrumentos de direito internacional;

IV - quando a transferência for necessária para a proteção da vida ou da incolumidade física do titular ou de terceiro;

V - quando a autoridade nacional autorizar a transferência;

VI - quando a transferência resultar em compromisso assumido em acordo de cooperação internacional;

VII - quando a transferência for necessária para a execução de política pública ou atribuição legal do serviço público, sendo dada publicidade nos termos do inciso I do caput do art. 23 desta Lei;

VIII - quando o titular tiver fornecido o seu consentimento específico e em destaque para a transferência, com informação prévia sobre o caráter internacional da operação, distinguindo claramente esta de outras finalidades; ou

IX - quando necessário para atender as hipóteses previstas nos incisos II, V e VI do art. 7º desta Lei.

Parágrafo único. Para os fins do inciso I deste artigo, as pessoas jurídicas de direito público referidas no parágrafo único do art. 1º da Lei nº 12.527, de 18 de novembro de 2011 (Lei de Acesso à Informação) , no âmbito de suas competências legais, e responsáveis, no âmbito de suas atividades, poderão requerer à autoridade nacional a avaliação do nível de proteção a dados pessoais conferido por país ou organismo internacional.

Art. 34. O nível de proteção de dados do país estrangeiro ou do organismo internacional mencionado no inciso I do caput do art. 33 desta Lei será avaliado pela autoridade nacional, que levará em consideração:

I - as normas gerais e setoriais da legislação em vigor no país de destino ou no organismo internacional;

II - a natureza dos dados;

III - a observância dos princípios gerais de proteção de dados pessoais e direitos dos titulares previstos nesta Lei;

IV - a adoção de medidas de segurança previstas em regulamento;

V - a existência de garantias judiciais e institucionais para o respeito aos direitos de proteção de dados pessoais; e

VI - outras circunstâncias específicas relativas à transferência.

Art. 35. A definição do conteúdo de cláusulas-padrão contratuais, bem como a verificação de cláusulas contratuais específicas para uma determinada transferência, normas corporativas globais ou selos, certificados e códigos de conduta, a que se refere o inciso II do caput do art. 33 desta Lei, será realizada pela autoridade nacional.

§ 1º Para a verificação do disposto no caput deste artigo, deverão ser considerados os requisitos, as condições e as garantias mínimas para a transferência que observem os direitos, as garantias e os princípios desta Lei.

§ 2º Na análise de cláusulas contratuais, de documentos ou de normas corporativas globais submetidas à aprovação da autoridade nacional, poderão ser requeridas informações suplementares ou realizadas diligências de verificação quanto às operações de tratamento, quando necessário.

§ 3º A autoridade nacional poderá designar organismos de certificação para a realização do previsto no caput deste artigo, que permanecerão sob sua fiscalização nos termos definidos em regulamento.

§ 4º Os atos realizados por organismo de certificação poderão ser revistos pela autoridade nacional e, caso em desconformidade com esta Lei, submetidos a revisão ou anulados.

§ 5º As garantias suficientes de observância dos princípios gerais de proteção e dos direitos do titular referidas no caput deste artigo serão também analisadas de acordo com as medidas técnicas e organizacionais adotadas pelo operador, de acordo com o previsto nos §§ 1º e 2º do art. 46 desta Lei.

Art. 36. As alterações nas garantias apresentadas como suficientes de observância dos princípios gerais de proteção e dos direitos do titular referidas no inciso II do art. 33 desta Lei deverão ser comunicadas à autoridade nacional.

CAPÍTULO VI
DOS AGENTES DE TRATAMENTO DE DADOS PESSOAIS

Seção I
Do Controlador e do Operador
```

## Pontos importantes para o SaaS

- Transferência internacional só é permitida em hipóteses específicas.
- País ou organismo internacional deve ter grau adequado de proteção ou o controlador deve oferecer garantias.
- Garantias podem envolver cláusulas contratuais específicas, cláusulas-padrão, normas corporativas globais, selos, certificados ou códigos de conduta.
- Consentimento para transferência internacional, quando usado, deve ser específico e destacado.
- Mudanças nas garantias devem ser comunicadas à autoridade nacional quando aplicável.

## Implicações técnicas

- Mapear todos os provedores que podem receber dados fora do Brasil.
- Verificar onde ficam servidores de Jitsi/JaaS, WhatsApp/Evolution, e-mail, IA, logs, backups e hospedagem.
- Documentar transferência internacional na política de privacidade.
- Preferir contratos e provedores com garantias claras de proteção de dados.
- Evitar enviar dados excessivos a provedores externos.

## Pendências ou decisões humanas

- Listar suboperadores e países envolvidos.
- Definir cláusulas contratuais/termos para provedores críticos.
- Definir se IA externa será usada e quais dados poderá receber.
