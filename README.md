# DFE Statistics BR

> Observatório independente de estatísticas nacionais de documentos fiscais eletrônicos.

**[Acessar o painel público de indicadores fiscais](https://fraurino.github.io/DFE-Statistics-BR/)**

## Sobre o projeto

O DFE Statistics BR nasceu com o propósito de transformar informações públicas sobre documentos fiscais eletrônicos em indicadores históricos acessíveis, organizados e úteis para análise da atividade fiscal brasileira.

O projeto acompanha as apurações divulgadas pelo Portal Nacional da NF-e, preservando o histórico dos valores publicados e permitindo observar sua evolução ao longo do tempo. A iniciativa busca promover transparência, facilitar pesquisas e ampliar o acesso a dados fiscais agregados.

## Objetivos

- Acompanhar a evolução do volume nacional de NF-e autorizadas.
- Preservar o histórico das apurações oficiais.
- Apresentar indicadores diários, semanais, mensais e anuais.
- Acompanhar a quantidade de estabelecimentos emissores ativos.
- Facilitar análises de tendências, sazonalidade e evolução da digitalização fiscal, respeitando as limitações da fonte.
- Disponibilizar dados abertos para estudos, aplicações e integrações com sistemas ERP, contábeis e fiscais.

## Painel analítico

O [dashboard público](https://fraurino.github.io/DFE-Statistics-BR/) apresenta indicadores nacionais, gráficos históricos, demonstrativos por período e exportação CSV. As datas e quantidades são exibidas no padrão brasileiro.

| Indicador | Significado |
| --- | --- |
| NF-e autorizadas | Quantidade acumulada publicada pela fonte oficial |
| Emissores ativos | CNPJs de 14 dígitos que emitiram NF-e nos 30 dias anteriores à apuração |
| Variação diária | Diferença entre acumulados de dias consecutivos |
| Variação semanal | Soma das variações diárias disponíveis na semana |
| Variação mensal | Soma das variações diárias disponíveis no mês |
| Variação anual | Soma das variações diárias disponíveis no ano |

## Fonte e periodicidade

A fonte inicial é o [Portal Nacional da Nota Fiscal Eletrônica — Estatísticas](https://www.nfe.fazenda.gov.br/portal/infoEstatisticas.aspx).

As consultas são programadas a cada 30 minutos. Isso não significa que a fonte disponibilize novos números a cada consulta: o acumulado de NF-e é apurado diariamente e o indicador de emissores a cada dez dias, conforme a metodologia divulgada pelo portal.

O painel informa as datas de apuração e a situação da última consulta, preservando os últimos dados válidos em caso de indisponibilidade.

## Metodologia de cálculo

A variação líquida diária é calculada pela diferença entre o acumulado publicado no dia e o acumulado publicado no dia anterior.

**Variação diária = acumulado atual − acumulado anterior**

Os indicadores semanais, mensais e anuais somam as variações diárias disponíveis nos respectivos períodos. As semanas começam na segunda-feira; meses e anos seguem o calendário civil.

### Limitações e interpretação

- Os valores oficiais são publicados de forma arredondada.
- O acumulado exclui documentos cancelados e denegados; portanto, sua diferença representa uma estimativa de variação líquida, não a quantidade exata de novas autorizações.
- Dias sem apuração consecutiva não são interpolados nem tratados como emissão zero.
- Os períodos agregados podem ser parciais e devem ser interpretados considerando a quantidade de dias observados.
- O histórico inicial registra NF-e em 26/11/2026 e emissores em 22/11/2026. Não representa uma série diária completa desde o início da NF-e.
- O volume de documentos não equivale diretamente a faturamento, arrecadação tributária ou crescimento econômico.

## Dados abertos

Os dados podem ser consultados gratuitamente em formatos adequados à análise e integração.

| Recurso | Formato |
| --- | --- |
| [Última apuração](https://fraurino.github.io/DFE-Statistics-BR/api/latest.json) | JSON |
| [Histórico de apurações](https://fraurino.github.io/DFE-Statistics-BR/api/history.json) | JSON |
| [Estatísticas diárias](https://fraurino.github.io/DFE-Statistics-BR/api/daily.json) | JSON |
| [Estatísticas semanais](https://fraurino.github.io/DFE-Statistics-BR/api/weekly.json) | JSON |
| [Estatísticas mensais](https://fraurino.github.io/DFE-Statistics-BR/api/monthly.json) | JSON |
| [Estatísticas anuais](https://fraurino.github.io/DFE-Statistics-BR/api/yearly.json) | JSON |
| [Histórico diário para planilhas](https://fraurino.github.io/DFE-Statistics-BR/api/daily.csv) | CSV |
| [Situação da última consulta](https://fraurino.github.io/DFE-Statistics-BR/api/status.json) | JSON |

## Público-alvo

Desenvolvedores de sistemas fiscais e ERP, profissionais de contabilidade, pesquisadores, analistas de dados, estudantes, empresas e cidadãos interessados na evolução dos documentos fiscais eletrônicos no Brasil.

## Abrangência e evolução

O escopo atual é a NF-e (modelo 55) em âmbito nacional. A inclusão de NFC-e, CT-e, MDF-e e outros documentos fiscais eletrônicos é uma possibilidade de evolução, condicionada à disponibilidade e validação de fontes públicas confiáveis.

## Transparência e independência

O DFE Statistics BR é uma iniciativa independente, sem vínculo institucional com a Receita Federal, ENCAT ou Secretarias de Fazenda. O projeto trabalha com estatísticas públicas agregadas, não com documentos fiscais individuais.

As informações possuem finalidade informativa e analítica e não substituem os dados oficiais para fins fiscais, contábeis ou legais.

**Fonte oficial:** [Portal Nacional da NF-e](https://www.nfe.fazenda.gov.br/portal/infoEstatisticas.aspx).
