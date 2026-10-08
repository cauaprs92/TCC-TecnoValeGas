"""Custo, preço de venda e lucro.

A margem é sobre a venda, não markup: com custo 100 e margem 30%, o preço é
100 ÷ 0,70 = 142,86 — dos 142,86 cobrados, 30% (42,86) é lucro. O lucro aqui
considera só material; mão de obra, deslocamento e impostos ainda não entram.
"""


def preco_venda(custo, margem_percentual):
    """Preço de venda pela margem sobre a venda, ou None se faltar custo ou margem."""
    if custo is None or margem_percentual is None:
        return None
    margem = float(margem_percentual) / 100
    if not 0 <= margem < 1:
        return None
    return round(float(custo) / (1 - margem), 2)


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
