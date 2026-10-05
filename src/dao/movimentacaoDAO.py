def registrar_movimentacao(cursor, id_produto: int, tipo: str, origem: str,
                           quantidade: int, id_obra: int = None):
    """Grava uma entrada/saída de estoque na transação de quem chama.

    Todo ponto que muda qtdProduto chama isto — é o histórico datado que
    alimenta o consumo médio do cálculo do estoque mínimo."""
    if quantidade <= 0:
        return
    cursor.execute("""
        INSERT INTO movimentacoesEstoque (idProduto, idObra, tipo, origem, quantidade)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_produto, id_obra, tipo, origem, quantidade))
