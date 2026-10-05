from src.dao.produtoDAO import ProdutoDAO
from src.controller.fornecedorController import FornecedorController
from src.modelo.produto import Produto


class ProdutoController:

    def __init__(self):
        self.dao = ProdutoDAO()
        self.fornecedor_ctrl = FornecedorController()

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

    def _opcional_positivo(self, valor, rotulo: str, decimal: bool = False) -> tuple:
        """Campo opcional: vazio vira None; se vier, precisa ser número > 0."""
        if valor is None or valor == "":
            return True, "", None
        try:
            numero = float(valor) if decimal else int(valor)
        except (ValueError, TypeError):
            return False, f"{rotulo} deve ser um número.", None
        if numero <= 0:
            return False, f"{rotulo} deve ser maior que zero.", None
        return True, "", numero

    def _montar(self, dados: dict) -> tuple:
        """Valida o corpo do cadastro/edição e monta o Produto.
        Retorna (sucesso, mensagem, produto)."""
        nome = (dados.get("nomeProduto") or "").strip()
        if not nome:
            return False, "Nome do produto não pode ser vazio.", None
        if len(nome) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres.", None

        qtd_maxima = int(dados.get("qtdMaxima") or 9999)
        valido, mensagem, qtd = self._validar_quantidade(dados.get("qtdProduto"), qtd_maxima)
        if not valido:
            return False, mensagem, None

        # Ajustes opcionais do estoque mínimo automático
        minimo_manual = dados.get("qtdMinimaManual")
        if minimo_manual is not None and minimo_manual != "":
            try:
                minimo_manual = int(minimo_manual)
            except (ValueError, TypeError):
                return False, "Mínimo manual deve ser um número inteiro.", None
            if minimo_manual < 0:
                return False, "Mínimo manual não pode ser negativo.", None
            if qtd_maxima > 0 and minimo_manual > qtd_maxima:
                return False, "Mínimo manual não pode ser maior que a quantidade máxima.", None
        else:
            minimo_manual = None

        valido, mensagem, prazo = self._opcional_positivo(dados.get("prazoEntregaDias"), "Prazo de entrega")
        if not valido:
            return False, mensagem, None
        valido, mensagem, consumo = self._opcional_positivo(dados.get("consumoEstimado"), "Uso aproximado", decimal=True)
        if not valido:
            return False, mensagem, None
        periodo = dados.get("periodoEstimativa") or None
        if consumo is not None and periodo not in ("dia", "semana", "mes"):
            return False, "Informe se o uso aproximado é por dia, semana ou mês.", None
        if consumo is None:
            periodo = None

        produto = Produto()
        produto._nomeProduto       = nome
        produto._qtdProduto        = qtd
        produto._descProduto       = (dados.get("descProduto") or "").strip()
        produto._qtdMaxima         = qtd_maxima
        produto._idFornecedor      = self.fornecedor_ctrl.obter_ou_criar_id(dados.get("fornecedor"))
        produto._qtdMinimaManual   = minimo_manual
        produto._prazoEntregaDias  = prazo
        produto._consumoEstimado   = consumo
        produto._periodoEstimativa = periodo
        return True, "", produto

    def _aviso_pos_gravacao(self, id_produto: int) -> str:
        """Alerta de estoque com o mínimo efetivo, que só existe depois do cálculo."""
        salvo = self.dao.buscar_por_id(id_produto)
        if not salvo:
            return ""
        return self._verificar_alerta_estoque(salvo._nomeProduto, salvo._qtdProduto, salvo._qtdMinima)

    def cadastrar(self, dados: dict) -> tuple:
        valido, mensagem, produto = self._montar(dados)
        if not valido:
            return False, mensagem, None, None
        if not self.dao.inserir(produto):
            return False, "Erro ao cadastrar produto.", None, None
        return True, "Produto cadastrado com sucesso!", self._aviso_pos_gravacao(produto._idProduto), produto._idProduto

    def listar(self) -> list:
        return self.dao.buscar_todos()

    def buscar_por_id(self, idProduto: int):
        return self.dao.buscar_por_id(idProduto)

    def editar(self, idProduto: int, dados: dict) -> tuple:
        valido, mensagem, produto = self._montar(dados)
        if not valido:
            return False, mensagem, None
        produto._idProduto = int(idProduto)
        if not self.dao.atualizar(produto):
            return False, "Erro ao atualizar produto.", None
        return True, "Produto atualizado com sucesso!", self._aviso_pos_gravacao(produto._idProduto)

    def deletar(self, idProduto: int) -> tuple:
        if not self.dao.buscar_por_id(idProduto):
            return False, "Produto não encontrado.", None

        sucesso = self.dao.deletar(idProduto)
        if sucesso:
            return True, "Produto deletado com sucesso!", None
        return False, "Erro ao deletar produto. Verifique se ele não está vinculado a uma obra ou serviço.", None

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
