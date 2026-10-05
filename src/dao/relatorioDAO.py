from src.dao.banco import consultar
from src.dao.produtoDAO import ProdutoDAO

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
