"""Custo, preço de venda e lucro.

A margem é um acréscimo sobre o custo (markup): com custo 100 e margem 30%, o
preço é 100 × 1,30 = 130,00 — o lucro (30,00) é 30% do custo. Por isso a
margem pode passar de 100% (150% = vender por 2,5 vezes o custo). O lucro aqui
considera só material; mão de obra, deslocamento e impostos ainda não entram.

Produto sem margem própria usa MARGEM_PADRAO — como o estoque mínimo, que é
automático até alguém definir um valor manual. O valor é provisório até a
empresa informar a margem real.
"""

MARGEM_PADRAO = 30.0
# Limite da coluna produtos.margemPercentual (DECIMAL(5,2)).
MARGEM_MAXIMA = 1000.0


def margem_efetiva(margem_percentual) -> float:
    """A margem do produto, ou a padrão quando ele não tem uma própria."""
    return float(margem_percentual) if margem_percentual is not None else MARGEM_PADRAO


def preco_venda(custo, margem_percentual):
    """Preço de venda = custo × (1 + margem) — a margem do produto, ou a
    padrão se ele não tiver uma própria. None se faltar o custo."""
    if custo is None:
        return None
    margem = margem_efetiva(margem_percentual) / 100
    if margem < 0:
        return None
    return round(float(custo) * (1 + margem), 2)


def custo_medio(estoque_atual, custo_atual, qtd_entrada, custo_entrada):
    """Custo médio ponderado depois de uma entrada de estoque.

    Sem custo anterior (ou sem estoque para ponderar), vale o custo da entrada.
    """
    if custo_entrada is None or qtd_entrada <= 0:
        return custo_atual
    estoque_atual = max(int(estoque_atual or 0), 0)
    if custo_atual is None or estoque_atual == 0:
        return round(float(custo_entrada), 4)
    total = estoque_atual * float(custo_atual) + qtd_entrada * float(custo_entrada)
    return round(total / (estoque_atual + qtd_entrada), 4)


def lucro(valor, custo) -> dict:
    """Lucro e margem real; None nos dois quando o custo é desconhecido."""
    if valor is None or custo is None:
        return {"lucro": None, "margemReal": None}
    valor, custo = float(valor), float(custo)
    resultado = round(valor - custo, 2)
    return {
        "lucro":      resultado,
        "margemReal": round(resultado / valor * 100, 2) if valor > 0 else None,
    }
