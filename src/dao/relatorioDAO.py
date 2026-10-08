from src.dao.banco import consultar
from src.dao.produtoDAO import ProdutoDAO
from src.service import precificacao

# Consumo = produtos avulsos + receita dos serviços (vw_consumo_obra).
# Obra cancelada já devolveu o material ao estoque, então não conta.


class RelatorioDAO:

    def produtos_consumidos(self) -> list:
        """Total consumido por produto, com estoque atual e mínimo (calculado)."""
        minimos = {p._idProduto: p._qtdMinima for p in ProdutoDAO().buscar_todos()}
        linhas = consultar("""
            SELECT p.idProduto, p.nomeProduto,
                   COALESCE(SUM(c.quantidade), 0) AS totalConsumido,
                   p.qtdProduto
            FROM produtos p
            LEFT JOIN (
                SELECT v.idProduto, v.quantidade
                FROM vw_consumo_obra v
                JOIN obras o ON o.idObra = v.idObra
                WHERE o.statusObra <> 'Cancelada'
            ) c ON c.idProduto = p.idProduto
            GROUP BY p.idProduto, p.nomeProduto, p.qtdProduto
            ORDER BY totalConsumido DESC
        """, erro="Erro no relatório de produtos consumidos:")
        return [
            {"idProduto": r[0], "nomeProduto": r[1], "totalConsumido": int(r[2]),
             "estoqueAtual": r[3], "qtdMinima": minimos.get(r[0], 0)}
            for r in linhas
        ]

    def consumo_por_produto_e_obra(self) -> list:
        """Para o gráfico: cada produto com o total consumido e a quebra por obra."""
        linhas = consultar("""
            SELECT p.idProduto, p.nomeProduto, o.idObra, o.descObra,
                   COALESCE(c.nomeCliente, CONCAT('Cliente #', o.codCliente)),
                   SUM(v.quantidade)
            FROM vw_consumo_obra v
            JOIN produtos p      ON p.idProduto = v.idProduto
            JOIN obras o         ON o.idObra    = v.idObra
            LEFT JOIN clientes c ON c.idCliente = o.codCliente
            WHERE o.statusObra <> 'Cancelada'
            GROUP BY p.idProduto, p.nomeProduto, o.idObra, o.descObra, c.nomeCliente, o.codCliente
            ORDER BY p.idProduto, o.idObra
        """, erro="Erro no relatório do gráfico de produtos:")

        produtos = {}
        for id_produto, nome_produto, id_obra, desc_obra, nome_cliente, qtd in linhas:
            p = produtos.setdefault(id_produto, {
                "idProduto": id_produto, "nomeProduto": nome_produto, "totalConsumido": 0, "obras": []
            })
            p["totalConsumido"] += int(qtd)
            p["obras"].append({"idObra": id_obra, "descObra": desc_obra,
                               "nomeCliente": nome_cliente, "qtd": int(qtd)})
        return sorted(produtos.values(), key=lambda x: x["totalConsumido"], reverse=True)

    # ─── Lucro (só material) ──────────────────────────────────────────────────

    def lucro_servicos(self) -> list:
        """Margem de cada serviço com o custo ATUAL da receita — é a margem que
        ele daria se fosse vendido hoje. Serviço com produto sem custo fica com
        custo/lucro None, para não parecer mais lucrativo do que é."""
        linhas = consultar("""
            SELECT s.idServico, s.nomeServico, s.precoServico,
                   SUM(sp.quantidade * p.custoUnitario),
                   COUNT(sp.idProduto),
                   COUNT(p.custoUnitario)
            FROM servicos s
            LEFT JOIN servicoProdutos sp ON sp.idServico = s.idServico
            LEFT JOIN produtos p         ON p.idProduto  = sp.idProduto
            GROUP BY s.idServico, s.nomeServico, s.precoServico
            ORDER BY s.nomeServico
        """, erro="Erro no relatório de lucro dos serviços:")
        resultado = []
        for id_servico, nome, preco, custo, qtd_itens, qtd_com_custo in linhas:
            sem_custo = qtd_itens - qtd_com_custo
            custo = None if sem_custo else float(custo or 0)
            resultado.append({
                "idServico": id_servico, "nomeServico": nome, "precoServico": float(preco),
                "custoMaterial": custo, "produtosSemCusto": sem_custo,
                **precificacao.lucro(preco, custo),
            })
        return resultado

    def lucro_produtos(self) -> list:
        """Por produto: preço atual (custo + margem) e o que ele rendeu vendido
        avulso em obras concluídas, com o custo e o preço congelados nelas."""
        linhas = consultar("""
            SELECT p.idProduto, p.nomeProduto, p.custoUnitario, p.margemPercentual,
                   COALESCE(SUM(po.qtdProdutosObra), 0),
                   SUM(po.qtdProdutosObra * COALESCE(po.precoVenda, 0)),
                   SUM(po.qtdProdutosObra * po.custoUnitario),
                   COUNT(po.idProdutosObra) - COUNT(po.custoUnitario)
            FROM produtos p
            LEFT JOIN (
                SELECT po.*
                FROM produtosObras po
                JOIN obras o ON o.idObra = po.idObra
                WHERE o.statusObra = 'Concluida'
            ) po ON po.idProduto = p.idProduto
            GROUP BY p.idProduto, p.nomeProduto, p.custoUnitario, p.margemPercentual
            ORDER BY p.nomeProduto
        """, erro="Erro no relatório de lucro dos produtos:")
        resultado = []
        for id_produto, nome, custo, margem, qtd, receita, custo_total, sem_custo in linhas:
            receita = float(receita or 0)
            custo_total = None if sem_custo else float(custo_total or 0)
            resultado.append({
                "idProduto": id_produto, "nomeProduto": nome,
                "custoUnitario":    float(custo)  if custo  is not None else None,
                "margemPercentual": float(margem) if margem is not None else None,
                "margemEfetiva":    precificacao.margem_efetiva(margem),
                "precoVenda":       precificacao.preco_venda(custo, margem),
                "qtdVendida": int(qtd), "receita": receita, "custoTotal": custo_total,
                **(precificacao.lucro(receita, custo_total) if qtd else {"lucro": None, "margemReal": None}),
            })
        return resultado
