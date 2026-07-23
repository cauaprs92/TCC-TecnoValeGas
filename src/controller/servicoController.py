from src.dao.servicoDAO import ServicoDAO
from src.modelo.servico import Servico


class ServicoController:

    def __init__(self):
        self.dao = ServicoDAO()

    def _validar_campos(self, nomeServico, precoServico) -> tuple:
        if not nomeServico or not str(nomeServico).strip():
            return False, "Nome do serviço não pode ser vazio."
        if len(str(nomeServico).strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres."
        try:
            preco = float(precoServico)
        except (ValueError, TypeError):
            return False, "Preço deve ser um número válido."
        if preco <= 0:
            return False, "Preço deve ser maior que zero."
        return True, ""

    def _validar_produtos(self, produtos: list) -> tuple:
        if not isinstance(produtos, list):
            return False, "A lista de produtos deve ser um array."
        for item in produtos:
            if not isinstance(item, dict):
                return False, "Cada item de produto deve ser um objeto."
            try:
                id_p = int(item.get("idProduto"))
                if id_p <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return False, "idProduto deve ser um inteiro positivo."
            try:
                qtd = int(item.get("quantidade"))
                if qtd <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return False, "quantidade deve ser um inteiro maior que zero."
        return True, ""

    def cadastrar(self, nomeServico, precoServico, produtos: list = None, fornecedorServico: str = None) -> tuple:
        valido, msg = self._validar_campos(nomeServico, precoServico)
        if not valido:
            return False, msg, None

        produtos = produtos or []
        valido, msg = self._validar_produtos(produtos)
        if not valido:
            return False, msg, None

        servico = Servico()
        servico._nomeServico       = str(nomeServico).strip()
        servico._precoServico      = float(precoServico)
        servico._produtos          = [
            {"idProduto": int(p["idProduto"]), "quantidade": int(p["quantidade"])}
            for p in produtos
        ]
        servico._fornecedorServico = (fornecedorServico or '').strip() or 'Tecnovale Gás'

        sucesso = self.dao.inserir(servico)
        if sucesso:
            return True, "Serviço cadastrado com sucesso!", servico._idServico
        return False, "Erro ao cadastrar serviço.", None

    def listar(self) -> list:
        return self.dao.buscar_todos()

    def buscar_por_id(self, idServico: int):
        return self.dao.buscar_por_id(idServico)

    def editar(self, idServico, nomeServico, precoServico, produtos: list = None, fornecedorServico: str = None) -> tuple:
        valido, msg = self._validar_campos(nomeServico, precoServico)
        if not valido:
            return False, msg

        produtos = produtos or []
        valido, msg = self._validar_produtos(produtos)
        if not valido:
            return False, msg

        servico = Servico()
        servico._idServico         = int(idServico)
        servico._nomeServico       = str(nomeServico).strip()
        servico._precoServico      = float(precoServico)
        servico._produtos          = [
            {"idProduto": int(p["idProduto"]), "quantidade": int(p["quantidade"])}
            for p in produtos
        ]
        servico._fornecedorServico = (fornecedorServico or '').strip() or 'Tecnovale Gás'

        sucesso = self.dao.atualizar(servico)
        if sucesso:
            return True, "Serviço atualizado com sucesso!"
        return False, "Erro ao atualizar serviço."

    def deletar(self, idServico: int) -> tuple:
        if not self.dao.buscar_por_id(idServico):
            return False, "Serviço não encontrado."
        sucesso = self.dao.deletar(idServico)
        if sucesso:
            return True, "Serviço deletado com sucesso!"
        return False, "Erro ao deletar serviço. Verifique se ele não está vinculado a uma obra."
