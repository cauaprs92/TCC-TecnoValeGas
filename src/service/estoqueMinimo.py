"""Cálculo automático do estoque mínimo (ponto de pedido).

    mínimo = consumo médio diário × prazo de entrega × (1 + margem de segurança)

O consumo médio vem das saídas de material para obras (descontadas as
devoluções) registradas em movimentacoesEstoque. Quando o produto ainda não
tem histórico suficiente, o cálculo usa, nesta ordem:

    1. histórico   — 30 dias ou mais desde a primeira saída: média real
    2. estimativa  — uso aproximado informado no cadastro do produto
    3. histórico curto — menos de 30 dias de uso, sem estimativa: média dos
                     dias desde a primeira saída (mínimo de 7 dias na conta,
                     para uma única obra grande não inflar o resultado)
    4. sem dados   — mínimo 0 até o produto ser usado ou ganhar estimativa

Um mínimo definido manualmente sempre substitui o calculado.
"""
import math
from datetime import date, datetime

JANELA_DIAS          = 90    # período usado para a média de consumo
HISTORICO_MINIMO     = 30    # dias de uso a partir dos quais a média é confiável
DIAS_MINIMOS_CONTA   = 7     # piso do divisor no histórico curto
MARGEM_SEGURANCA     = 0.20  # 20% acima do consumo esperado no prazo
PRAZO_PADRAO         = 7     # produto sem fornecedor nem prazo próprio

DIAS_POR_PERIODO = {"dia": 1, "semana": 7, "mes": 30}

ORIGENS = {
    "manual":          "Definido manualmente",
    "historico":       "Calculado pelo histórico",
    "estimativa":      "Calculado pela estimativa de uso",
    "historico_curto": "Calculado com pouco histórico",
    "sem_dados":       "Aguardando dados de uso",
}


def _formatar(numero: float) -> str:
    """3,5 | 12 | 0,27 — duas casas só abaixo de 1, para não virar '0/dia'."""
    texto = f"{numero:.2f}" if numero < 1 else f"{numero:.1f}"
    texto = texto.replace(".", ",")
    return texto[:-2] if texto.endswith(",0") else texto


def calcular(consumo_janela, primeira_saida, consumo_estimado=None, periodo_estimativa=None,
             prazo_produto=None, prazo_fornecedor=None, minimo_manual=None, hoje: date = None) -> dict:
    """Devolve o mínimo efetivo e como ele foi obtido.

    consumo_janela: unidades consumidas por obras nos últimos JANELA_DIAS (líquido)
    primeira_saida: data da primeira saída para obra registrada (ou None)
    """
    hoje = hoje or date.today()
    if isinstance(primeira_saida, datetime):
        primeira_saida = primeira_saida.date()

    if prazo_produto:
        prazo, origem_prazo = int(prazo_produto), "produto"
    elif prazo_fornecedor:
        prazo, origem_prazo = int(prazo_fornecedor), "fornecedor"
    else:
        prazo, origem_prazo = PRAZO_PADRAO, "padrao"

    dias_uso = (hoje - primeira_saida).days + 1 if primeira_saida else 0
    consumo = max(float(consumo_janela or 0), 0.0)

    if dias_uso >= HISTORICO_MINIMO:
        origem, consumo_dia = "historico", consumo / min(dias_uso, JANELA_DIAS)
    elif consumo_estimado and periodo_estimativa in DIAS_POR_PERIODO:
        origem, consumo_dia = "estimativa", float(consumo_estimado) / DIAS_POR_PERIODO[periodo_estimativa]
    elif primeira_saida:
        origem, consumo_dia = "historico_curto", consumo / max(dias_uso, DIAS_MINIMOS_CONTA)
    else:
        origem, consumo_dia = "sem_dados", 0.0

    calculado = math.ceil(round(consumo_dia * prazo * (1 + MARGEM_SEGURANCA), 6))
    if origem == "sem_dados":
        explicacao = "Sem uso registrado nem estimativa — mínimo 0 até haver dados."
    else:
        explicacao = (f"{_formatar(consumo_dia)}/dia × {prazo} dias de prazo "
                      f"+ {int(MARGEM_SEGURANCA * 100)}% de margem = {calculado}")

    efetivo = calculado
    if minimo_manual is not None:
        efetivo = int(minimo_manual)
        explicacao = f"Definido manualmente (o cálculo daria {calculado})."

    return {
        "qtdMinima":           efetivo,
        "qtdMinimaCalculada":  calculado,
        "origemMinimo":        "manual" if minimo_manual is not None else origem,
        "origemCalculo":       origem,
        "descricaoOrigem":     ORIGENS["manual" if minimo_manual is not None else origem],
        "consumoDiario":       round(consumo_dia, 2),
        "diasHistorico":       dias_uso,
        "prazoEntregaDias":    prazo,
        "origemPrazo":         origem_prazo,
        "explicacaoMinimo":    explicacao,
    }
