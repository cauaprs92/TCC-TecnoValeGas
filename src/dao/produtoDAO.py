from src.dao.banco import consultar, consultar_um, executar, executar_transacao, inserir
from src.modelo.produto import Produto

_CAMPOS = ["nomeProduto", "qtdProduto", "descProduto", "qtdMinima", "qtdMaxima", "idFornecedor"]
_SELECT = """
    SELECT p.idProduto, p.nomeProduto, p.qtdProduto, p.descProduto, p.qtdMinima, p.qtdMaxima,
           p.idFornecedor, f.nomeFornecedor
    FROM produtos p
    LEFT JOIN fornecedores f ON f.idFornecedor = p.idFornecedor
"""


def _valores(produto: Produto) -> list:
    return [getattr(produto, f"_{c}") for c in _CAMPOS]


class ProdutoDAO:

    def inserir(self, produto: Produto) -> bool:
        id_gerado = inserir(
            f"INSERT INTO produtos ({', '.join(_CAMPOS)}) VALUES ({', '.join(['%s'] * len(_CAMPOS))})",
            _valores(produto), erro="Erro ao inserir produto:")
        if id_gerado is None:
            return False
        produto._idProduto = id_gerado
        return True

    def buscar_todos(self) -> list:
        return [self._linha_para_produto(l) for l in consultar(_SELECT, erro="Erro ao buscar produtos:")]

    def buscar_por_id(self, id_produto: int):
        linha = consultar_um(f"{_SELECT} WHERE p.idProduto = %s", (id_produto,),
                             erro="Erro ao buscar produto por ID:")
        return self._linha_para_produto(linha) if linha else None

    def atualizar(self, produto: Produto) -> bool:
        sets = ", ".join(f"{c} = %s" for c in _CAMPOS)
        return executar(f"UPDATE produtos SET {sets} WHERE idProduto = %s",
                        _valores(produto) + [produto._idProduto], erro="Erro ao atualizar produto:")

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
        (p._idProduto, p._nomeProduto, p._qtdProduto, p._descProduto,
         qtd_minima, qtd_maxima, p._idFornecedor, p._nomeFornecedor) = linha
        p._qtdMinima = qtd_minima if qtd_minima is not None else 0
        p._qtdMaxima = qtd_maxima if qtd_maxima is not None else 9999
        return p
