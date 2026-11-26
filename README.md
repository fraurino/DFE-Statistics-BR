# DFE Statistics BR

Observatório independente de estatísticas fiscais públicas. [Fonte oficial](https://www.nfe.fazenda.gov.br/portal/infoEstatisticas.aspx).

Coleta a cada 30 minutos. Diferenças do acumulado são aproximadas e líquidas de cancelamentos; lacunas não são interpoladas. Agregações mostram dias observados, não totais completos garantidos. Emissores são CNPJs ativos nos 30 dias anteriores à apuração.

## Ativação
Settings → Pages → Source: GitHub Actions. Actions → Monitor NF-e → Run workflow. Painel: https://fraurino.github.io/DFE-Statistics-BR/.

Python 3.12, sem dependências externas. Testes: `python -m unittest discover -s tests`. Coleta: `python monitor.py`. Dados em `docs/api/`. Base inicial transcrita do HTML oficial fornecido em 26/11/2026. Outros DF-e dependem de fontes verificadas.
