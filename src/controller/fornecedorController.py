from src.dao.fornecedorDAO import FornecedorDAO


class FornecedorController:

    def __init__(self):
        self.dao = FornecedorDAO()

    def listar(self) -> list:
        return [
            {"idFornecedor": r[0], "nomeFornecedor": r[1], "prazoEntregaDias": r[2], "qtdProdutos": r[3]}
            for r in self.dao.listar()
        ]

    def atualizar_prazo(self, id_fornecedor: int, prazo) -> tuple:
        """O prazo de entrega entra no cálculo do estoque mínimo de todos os
        produtos do fornecedor que não têm prazo próprio."""
        fornecedor = self.dao.buscar_por_id(id_fornecedor)
        if not fornecedor:
            return False, "Fornecedor não encontrado.", None
        try:
            prazo = int(prazo)
        except (ValueError, TypeError):
            return False, "Prazo de entrega deve ser um número inteiro de dias.", None
        if prazo <= 0 or prazo > 365:
            return False, "Prazo de entrega deve estar entre 1 e 365 dias.", None
        if not self.dao.atualizar_prazo(id_fornecedor, prazo):
            return False, "Erro ao atualizar o prazo do fornecedor.", None
        return True, "Prazo de entrega atualizado!", fornecedor[1]

    def obter_ou_criar_id(self, nome: str):
        """Resolve o nome de um fornecedor para seu ID, criando-o se ainda não existir.
        Retorna None se nenhum nome for informado (fornecedor é opcional)."""
        if not nome or not nome.strip():
            return None
        return self.dao.obter_ou_criar(nome.strip())
