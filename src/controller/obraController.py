from src.dao.obraDAO          import ObraDAO
from src.dao.produtosObrasDAO import ProdutosObrasDAO
from src.dao.clienteDAO       import ClienteDAO
from src.controller.produtoController import ProdutoController

class ObraController:

    STATUS_VALIDOS = ["Em andamento", "Concluida", "Cancelada", "Pausada"]

    def __init__(self):
        self.dao          = ObraDAO()
        self.daoProdObras = ProdutosObrasDAO()
        self.daoCliente   = ClienteDAO()
        self.ctrlProduto  = ProdutoController()

    def _validar_status(self, status: str) -> tuple:
        if status not in self.STATUS_VALIDOS:
            opcoes = ", ".join(self.STATUS_VALIDOS)
            return False, f"Status invalido. Use: {opcoes}."
        return True, ""

    def cadastrar(self, dadosObra: dict, produtosUsados: list) -> tuple:
        clienteExistente = self.daoCliente.buscar_por_id(dadosObra["codCliente"])
        if not clienteExistente:
            return False, "Cliente nao encontrado. Cadastre o cliente antes de criar a obra."

        if not dadosObra.get("descObra", "").strip():
            return False, "Descricao da obra nao pode ser vazia."

        if not dadosObra.get("dataInicio", "").strip():
            return False, "Data de inicio da obra nao pode ser vazia."

        if not dadosObra.get("respObra", "").strip():
            return False, "Responsavel pela obra e obrigatorio."

        valido, mensagem = self._validar_status(dadosObra.get("statusObra", ""))
        if not valido:
            return False, mensagem

        if not produtosUsados:
            return False, "Informe pelo menos um produto para a obra."

        avisos = []
        for item in produtosUsados:
            estoque_ok, mensagem = self.ctrlProduto.verificar_estoque(
                item["idProduto"], item["quantidade"]
            )
            if not estoque_ok:
                return False, mensagem
            if "ATENCAO" in mensagem or "AVISO" in mensagem:
                avisos.append(mensagem)

        sucesso = self.daoProdObras.cadastrar_obra_com_produtos(dadosObra, produtosUsados)
        if sucesso:
            if avisos:
                return True, "Obra cadastrada com sucesso!\n" + "\n".join(avisos)
            return True, "Obra cadastrada com sucesso!"
        return False, "Erro ao cadastrar obra."

    def atualizar(self, idObra: int, dadosObra: dict, produtosNovos: list = None) -> tuple:
        obraExistente = self.dao.buscar_por_id(idObra)
        if not obraExistente:
            return False, "Obra nao encontrada."

        clienteExistente = self.daoCliente.buscar_por_id(dadosObra["codCliente"])
        if not clienteExistente:
            return False, "Cliente nao encontrado."

        if not dadosObra.get("descObra", "").strip():
            return False, "Descricao da obra nao pode ser vazia."

        valido, mensagem = self._validar_status(dadosObra.get("statusObra", ""))
        if not valido:
            return False, mensagem

        sucesso = self.dao.atualizar(idObra, dadosObra)
        if not sucesso:
            return False, "Erro ao atualizar obra."

        if produtosNovos:
            avisos = []
            for item in produtosNovos:
                estoque_ok, msg = self.ctrlProduto.verificar_estoque(item["idProduto"], item["quantidade"])
                if not estoque_ok:
                    return False, msg
                if "ATENCAO" in msg or "AVISO" in msg:
                    avisos.append(msg)

            ok = self.daoProdObras.adicionar_produtos_obra(idObra, produtosNovos)
            if not ok:
                return False, "Erro ao adicionar produtos à obra."
            if avisos:
                return True, "Obra atualizada!\n" + "\n".join(avisos)

        return True, "Obra atualizada com sucesso!"

    def listar(self) -> list:
        return self.dao.buscar_todas()

    def buscar_por_id(self, idObra: int):
        return self.dao.buscar_por_id(idObra)

    def listar_por_cliente(self, idCliente: int) -> tuple:
        clienteExistente = self.daoCliente.buscar_por_id(idCliente)
        if not clienteExistente:
            return False, "Cliente nao encontrado.", []

        obras = self.dao.buscar_por_cliente(idCliente)
        return True, f"Obras do cliente {clienteExistente._nomeCliente}", obras

    def atualizar_status(self, idObra: int, novoStatus: str) -> tuple:
        valido, mensagem = self._validar_status(novoStatus)
        if not valido:
            return False, mensagem

        obraExistente = self.dao.buscar_por_id(idObra)
        if not obraExistente:
            return False, "Obra nao encontrada."

        statusAtual = obraExistente[5]
        novoStatus  = novoStatus.strip()

        if statusAtual == novoStatus:
            return True, "Status já estava definido como esse valor."

        if novoStatus == "Cancelada" and statusAtual != "Cancelada":
            if not self.daoProdObras.restaurar_estoque_obra(idObra):
                return False, "Erro ao restaurar estoque ao cancelar obra."

        elif statusAtual == "Cancelada" and novoStatus != "Cancelada":
            ok, msg = self.daoProdObras.baixar_estoque_obra(idObra)
            if not ok:
                return False, f"Não foi possível reativar a obra: {msg}"

        sucesso = self.dao.atualizar_status(idObra, novoStatus)
        if sucesso:
            return True, "Status atualizado com sucesso!"
        return False, "Erro ao atualizar status."

    def deletar(self, idObra: int) -> tuple:
        obraExistente = self.dao.buscar_por_id(idObra)
        if not obraExistente:
            return False, "Obra nao encontrada."

        sucesso = self.daoProdObras.deletar_obra_com_reposicao(idObra)
        if sucesso:
            return True, "Obra deletada com sucesso!"
        return False, "Erro ao deletar obra."

    def buscar_produtos_da_obra(self, idObra: int) -> list:
        return self.daoProdObras.buscar_produtos_da_obra(idObra)

    def atualizar_produto_obra(self, idObra: int, idProduto: int, nova_qtd: int) -> tuple:
        if not self.dao.buscar_por_id(idObra):
            return False, "Obra não encontrada."
        if nova_qtd < 1:
            return False, "Quantidade deve ser maior que zero."
        return self.daoProdObras.atualizar_quantidade_produto_obra(idObra, idProduto, nova_qtd)
