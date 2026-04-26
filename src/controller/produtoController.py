from src.dao.produtoDAO import ProdutoDAO
from src.modelo.produto import Produto

class ProdutoController:

    QTD_MAXIMA  = 9999
    QTD_MINIMA  = 50
    QTD_ALERTA  = 5

    def __init__(self):
        self.dao = ProdutoDAO()

    def _validar_quantidade(self, qtdProduto) -> tuple:
        try:
            qtd = int(qtdProduto)
        except ValueError:
            return False, "Quantidade deve ser um numero inteiro.", None

        if qtd < 0:
            return False, "Quantidade nao pode ser negativa.", None

        if qtd > self.QTD_MAXIMA:
            return False, f"Quantidade nao pode passar de {self.QTD_MAXIMA} unidades.", None

        return True, "", qtd

    def _verificar_alerta_estoque(self, nomeProduto: str, qtd: int) -> str:
        if qtd <= self.QTD_ALERTA:
            return f"ATENCAO: Estoque de '{nomeProduto}' esta muito baixo ({qtd} unidades). Repor em breve!"
        if qtd < self.QTD_MINIMA:
            return f"AVISO: Estoque de '{nomeProduto}' esta abaixo do minimo ({qtd}/{self.QTD_MINIMA} unidades)."
        return ""

    def cadastrar(self, idProduto, nomeProduto, qtdProduto, descProduto) -> tuple:
        if not nomeProduto.strip():
            return False, "Nome do produto nao pode ser vazio.", None

        if len(nomeProduto.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres.", None

        valido, mensagem, qtd = self._validar_quantidade(qtdProduto)
        if not valido:
            return False, mensagem, None

        produtoExistente = self.dao.buscar_por_id(int(idProduto))
        if produtoExistente:
            return False, f"Ja existe um produto com o ID {idProduto}.", None

        dadoProduto = Produto()
        dadoProduto._idProduto   = int(idProduto)
        dadoProduto._nomeProduto = nomeProduto.strip()
        dadoProduto._qtdProduto  = qtd
        dadoProduto._descProduto = descProduto.strip()

        sucesso = self.dao.inserir(dadoProduto)
        if sucesso:
            aviso = self._verificar_alerta_estoque(nomeProduto.strip(), qtd)
            return True, "Produto cadastrado com sucesso!", aviso
        return False, "Erro ao cadastrar produto.", None

    def listar(self) -> list:
        return self.dao.buscar_todos()

    def buscar_por_id(self, idProduto: int):
        return self.dao.buscar_por_id(idProduto)

    def editar(self, idProduto, nomeProduto, qtdProduto, descProduto) -> tuple:
        if not nomeProduto.strip():
            return False, "Nome do produto nao pode ser vazio.", None

        if len(nomeProduto.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres.", None

        valido, mensagem, qtd = self._validar_quantidade(qtdProduto)
        if not valido:
            return False, mensagem, None

        dadoProduto = Produto()
        dadoProduto._idProduto   = int(idProduto)
        dadoProduto._nomeProduto = nomeProduto.strip()
        dadoProduto._qtdProduto  = qtd
        dadoProduto._descProduto = descProduto.strip()

        sucesso = self.dao.atualizar(dadoProduto)
        if sucesso:
            aviso = self._verificar_alerta_estoque(nomeProduto.strip(), qtd)
            return True, "Produto atualizado com sucesso!", aviso
        return False, "Erro ao atualizar produto.", None

    def deletar(self, idProduto: int) -> tuple:
        produtoExistente = self.dao.buscar_por_id(idProduto)
        if not produtoExistente:
            return False, "Produto nao encontrado.", None

        sucesso = self.dao.deletar(idProduto)
        if sucesso:
            return True, "Produto deletado com sucesso!", None
        return False, "Erro ao deletar produto. Verifique se ele nao esta vinculado a uma obra.", None

    def verificar_estoque(self, idProduto: int, quantidadeNecessaria: int) -> tuple:
        dadoProduto = self.dao.buscar_por_id(idProduto)
        if not dadoProduto:
            return False, f"Produto ID {idProduto} nao encontrado."

        if dadoProduto._qtdProduto <= 0:
            return False, f"Produto '{dadoProduto._nomeProduto}' sem estoque."

        if dadoProduto._qtdProduto < quantidadeNecessaria:
            return False, f"Estoque insuficiente para '{dadoProduto._nomeProduto}'. Disponivel: {dadoProduto._qtdProduto}."

        estoqueAposUso = dadoProduto._qtdProduto - quantidadeNecessaria
        aviso = self._verificar_alerta_estoque(dadoProduto._nomeProduto, estoqueAposUso)
        return True, aviso if aviso else "Estoque disponivel."