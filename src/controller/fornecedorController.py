from src.dao.fornecedorDAO import FornecedorDAO


class FornecedorController:

    def __init__(self):
        self.dao = FornecedorDAO()

    def listar(self) -> list:
        rows = self.dao.listar()
        return [{"idFornecedor": r[0], "nomeFornecedor": r[1]} for r in rows]

    def obter_ou_criar_id(self, nome: str):
        """Resolve o nome de um fornecedor para seu ID, criando-o se ainda não existir.
        Retorna None se nenhum nome for informado (fornecedor é opcional)."""
        if not nome or not nome.strip():
            return None
        return self.dao.obter_ou_criar(nome.strip())
