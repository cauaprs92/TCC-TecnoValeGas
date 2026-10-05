from src.dao.banco import consultar, consultar_um, inserir


class FornecedorDAO:

    def listar(self) -> list:
        return consultar("SELECT idFornecedor, nomeFornecedor FROM fornecedores ORDER BY nomeFornecedor",
                         erro="Erro ao listar fornecedores:")

    def obter_ou_criar(self, nome: str):
        """Retorna o idFornecedor existente para o nome informado ou cria um novo registro."""
        existente = consultar_um(
            "SELECT idFornecedor FROM fornecedores WHERE LOWER(nomeFornecedor) = LOWER(%s)", (nome,),
            erro="Erro ao buscar fornecedor por nome:")
        if existente:
            return existente[0]
        return inserir("INSERT INTO fornecedores (nomeFornecedor) VALUES (%s)", (nome,),
                       erro="Erro ao criar fornecedor:")
