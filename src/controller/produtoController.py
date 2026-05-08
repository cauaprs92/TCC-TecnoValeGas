from src.dao.produtoDAO import ProdutoDAO
from src.modelo.produto import Produto


class ProdutoController:

    def __init__(self):
        self.dao = ProdutoDAO()

    def _validar_quantidade(self, qtdProduto, qtd_maxima: int = 9999) -> tuple:
        try:
            qtd = int(qtdProduto)
        except (ValueError, TypeError):
            return False, "Quantidade deve ser um número inteiro.", None

        if qtd < 0:
            return False, "Quantidade não pode ser negativa.", None

        if qtd_maxima > 0 and qtd > qtd_maxima:
            return False, f"Quantidade não pode passar de {qtd_maxima} unidades (máximo configurado).", None

        return True, "", qtd

    def _verificar_alerta_estoque(self, nomeProduto: str, qtd: int, qtd_minima: int = 0) -> str:
        if qtd <= 0:
            return f"ATENCAO: Produto '{nomeProduto}' está sem estoque!"
        if qtd_minima > 0 and qtd < qtd_minima:
            return f"AVISO: Estoque de '{nomeProduto}' está abaixo do mínimo ({qtd}/{qtd_minima} unidades)."
        return ""

    def cadastrar(self, nomeProduto, qtdProduto, descProduto,
                  qtdMinima: int = 0, qtdMaxima: int = 9999) -> tuple:
        if not nomeProduto or not nomeProduto.strip():
            return False, "Nome do produto não pode ser vazio.", None

        if len(nomeProduto.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres.", None

        valido, mensagem, qtd = self._validar_quantidade(qtdProduto, qtdMaxima)
        if not valido:
            return False, mensagem, None

        if qtdMinima < 0:
            return False, "Quantidade mínima não pode ser negativa.", None
        if qtdMaxima > 0 and qtdMinima > qtdMaxima:
            return False, "Quantidade mínima não pode ser maior que a máxima.", None

        idProduto = self.dao.proximo_id()

        dadoProduto = Produto()
        dadoProduto._idProduto   = idProduto
        dadoProduto._nomeProduto = nomeProduto.strip()
        dadoProduto._qtdProduto  = qtd
        dadoProduto._descProduto = descProduto.strip() if descProduto else ""
        dadoProduto._qtdMinima   = qtdMinima
        dadoProduto._qtdMaxima   = qtdMaxima

        sucesso = self.dao.inserir(dadoProduto)
        if sucesso:
            aviso = self._verificar_alerta_estoque(nomeProduto.strip(), qtd, qtdMinima)
            return True, "Produto cadastrado com sucesso!", aviso
        return False, "Erro ao cadastrar produto.", None

    def listar(self) -> list:
        return self.dao.buscar_todos()

    def buscar_por_id(self, idProduto: int):
        return self.dao.buscar_por_id(idProduto)

    def editar(self, idProduto, nomeProduto, qtdProduto, descProduto,
               qtdMinima: int = 0, qtdMaxima: int = 9999) -> tuple:
        if not nomeProduto or not nomeProduto.strip():
            return False, "Nome do produto não pode ser vazio.", None

        if len(nomeProduto.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres.", None

        valido, mensagem, qtd = self._validar_quantidade(qtdProduto, qtdMaxima)
        if not valido:
            return False, mensagem, None

        if qtdMinima < 0:
            return False, "Quantidade mínima não pode ser negativa.", None
        if qtdMaxima > 0 and qtdMinima > qtdMaxima:
            return False, "Quantidade mínima não pode ser maior que a máxima.", None

        dadoProduto = Produto()
        dadoProduto._idProduto   = int(idProduto)
        dadoProduto._nomeProduto = nomeProduto.strip()
        dadoProduto._qtdProduto  = qtd
        dadoProduto._descProduto = descProduto.strip() if descProduto else ""
        dadoProduto._qtdMinima   = qtdMinima
        dadoProduto._qtdMaxima   = qtdMaxima

        sucesso = self.dao.atualizar(dadoProduto)
        if sucesso:
            aviso = self._verificar_alerta_estoque(nomeProduto.strip(), qtd, qtdMinima)
            return True, "Produto atualizado com sucesso!", aviso
        return False, "Erro ao atualizar produto.", None

    def deletar(self, idProduto: int) -> tuple:
        if not self.dao.buscar_por_id(idProduto):
            return False, "Produto não encontrado.", None

        sucesso = self.dao.deletar(idProduto)
        if sucesso:
            return True, "Produto deletado com sucesso!", None
        return False, "Erro ao deletar produto. Verifique se ele não está vinculado a uma obra.", None

    def verificar_estoque(self, idProduto: int, quantidadeNecessaria: int) -> tuple:
        dadoProduto = self.dao.buscar_por_id(idProduto)
        if not dadoProduto:
            return False, f"Produto ID {idProduto} não encontrado."

        if dadoProduto._qtdProduto <= 0:
            return False, f"Produto '{dadoProduto._nomeProduto}' sem estoque."

        if dadoProduto._qtdProduto < quantidadeNecessaria:
            return False, (f"Estoque insuficiente para '{dadoProduto._nomeProduto}'. "
                           f"Disponível: {dadoProduto._qtdProduto}.")

        estoqueAposUso = dadoProduto._qtdProduto - quantidadeNecessaria
        aviso = self._verificar_alerta_estoque(
            dadoProduto._nomeProduto, estoqueAposUso, dadoProduto._qtdMinima
        )
        return True, aviso if aviso else "Estoque disponível."
