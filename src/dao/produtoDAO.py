from src.dao.banco import consultar, consultar_um, executar_transacao
from src.dao.movimentacaoDAO import registrar_movimentacao
from src.modelo.produto import Produto
from src.service import estoqueMinimo

_CAMPOS = [
    "nomeProduto", "qtdProduto", "descProduto", "qtdMaxima", "idFornecedor",
    "qtdMinimaManual", "prazoEntregaDias", "consumoEstimado", "periodoEstimativa",
]

# Consumo líquido das obras na janela (saídas menos devoluções) e a data da
# primeira saída — as duas entradas do cálculo do estoque mínimo.
_SELECT = f"""
    SELECT p.idProduto, p.nomeProduto, p.qtdProduto, p.descProduto, p.qtdMaxima,
           p.idFornecedor, p.qtdMinimaManual, p.prazoEntregaDias, p.consumoEstimado,
           p.periodoEstimativa, f.nomeFornecedor, f.prazoEntregaDias,
           COALESCE(m.consumoJanela, 0), m.primeiraSaida
    FROM produtos p
    LEFT JOIN fornecedores f ON f.idFornecedor = p.idFornecedor
    LEFT JOIN (
        SELECT idProduto,
               SUM(CASE WHEN dataMov >= CURDATE() - INTERVAL {estoqueMinimo.JANELA_DIAS} DAY
                        THEN IF(tipo = 'saida', quantidade, -quantidade) ELSE 0 END) AS consumoJanela,
               MIN(CASE WHEN tipo = 'saida' THEN dataMov END) AS primeiraSaida
        FROM movimentacoesEstoque
        WHERE origem = 'obra'
        GROUP BY idProduto
    ) m ON m.idProduto = p.idProduto
"""


def _valores(produto: Produto) -> list:
    return [getattr(produto, f"_{c}") for c in _CAMPOS]


class ProdutoDAO:

    def inserir(self, produto: Produto) -> bool:
        def operacao(cursor):
            cursor.execute(
                f"INSERT INTO produtos ({', '.join(_CAMPOS)}) VALUES ({', '.join(['%s'] * len(_CAMPOS))})",
                _valores(produto)
            )
            produto._idProduto = cursor.lastrowid
            registrar_movimentacao(cursor, produto._idProduto, "entrada", "ajuste", produto._qtdProduto)
        sucesso, _ = executar_transacao(operacao, "Erro ao inserir produto:")
        return sucesso

    def buscar_todos(self) -> list:
        return [self._linha_para_produto(l) for l in consultar(_SELECT, erro="Erro ao buscar produtos:")]

    def buscar_por_id(self, id_produto: int):
        linha = consultar_um(f"{_SELECT} WHERE p.idProduto = %s", (id_produto,),
                             erro="Erro ao buscar produto por ID:")
        return self._linha_para_produto(linha) if linha else None

    def atualizar(self, produto: Produto) -> bool:
        """A quantidade digitada na edição é um ajuste manual: a diferença para o
        estoque atual fica registrada como entrada ou saída de 'ajuste'."""
        def operacao(cursor):
            cursor.execute("SELECT qtdProduto FROM produtos WHERE idProduto = %s FOR UPDATE",
                           (produto._idProduto,))
            row = cursor.fetchone()
            sets = ", ".join(f"{c} = %s" for c in _CAMPOS)
            cursor.execute(f"UPDATE produtos SET {sets} WHERE idProduto = %s",
                           _valores(produto) + [produto._idProduto])
            diferenca = produto._qtdProduto - (row[0] if row else 0)
            tipo = "entrada" if diferenca > 0 else "saida"
            registrar_movimentacao(cursor, produto._idProduto, tipo, "ajuste", abs(diferenca))
        sucesso, _ = executar_transacao(operacao, "Erro ao atualizar produto:")
        return sucesso

    def deletar(self, idProduto: int) -> bool:
        # O item da nota fiscal só aponta para o produto; a nota continua íntegra
        # sem esse vínculo (guarda nomeProdutoNota e statusItem próprios), então
        # desfaz a referência antes de excluir — senão a FK bloqueia o DELETE.
        def operacao(cursor):
            cursor.execute("UPDATE notaFiscalItens SET idProduto = NULL WHERE idProduto = %s", (idProduto,))
            cursor.execute("DELETE FROM produtos WHERE idProduto = %s", (idProduto,))
        sucesso, _ = executar_transacao(operacao, "Erro ao deletar produto:")
        return sucesso

    def _linha_para_produto(self, linha) -> Produto:
        p = Produto()
        (p._idProduto, p._nomeProduto, p._qtdProduto, p._descProduto, qtd_maxima,
         p._idFornecedor, p._qtdMinimaManual, p._prazoEntregaDias, consumo_estimado,
         p._periodoEstimativa, p._nomeFornecedor, prazo_fornecedor,
         consumo_janela, primeira_saida) = linha
        p._qtdMaxima       = qtd_maxima if qtd_maxima is not None else 9999
        p._consumoEstimado = float(consumo_estimado) if consumo_estimado is not None else None

        p._estoqueMinimo = estoqueMinimo.calcular(
            consumo_janela, primeira_saida,
            consumo_estimado=p._consumoEstimado, periodo_estimativa=p._periodoEstimativa,
            prazo_produto=p._prazoEntregaDias, prazo_fornecedor=prazo_fornecedor,
            minimo_manual=p._qtdMinimaManual,
        )
        p._qtdMinima = p._estoqueMinimo["qtdMinima"]
        return p
