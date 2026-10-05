from src.dao.banco import consultar, consultar_um, executar, inserir


class FornecedorDAO:

    def listar(self) -> list:
        """(id, nome, prazo de entrega, quantidade de produtos do fornecedor)."""
        return consultar("""
            SELECT f.idFornecedor, f.nomeFornecedor, f.prazoEntregaDias, COUNT(p.idProduto)
            FROM fornecedores f
            LEFT JOIN produtos p ON p.idFornecedor = f.idFornecedor
            GROUP BY f.idFornecedor, f.nomeFornecedor, f.prazoEntregaDias
            ORDER BY f.nomeFornecedor
        """, erro="Erro ao listar fornecedores:")

    def buscar_por_id(self, id_fornecedor: int):
        return consultar_um("SELECT idFornecedor, nomeFornecedor FROM fornecedores WHERE idFornecedor = %s",
                            (id_fornecedor,), erro="Erro ao buscar fornecedor:")

    def atualizar_prazo(self, id_fornecedor: int, prazo: int) -> bool:
        return executar("UPDATE fornecedores SET prazoEntregaDias = %s WHERE idFornecedor = %s",
                        (prazo, id_fornecedor), erro="Erro ao atualizar prazo do fornecedor:")

    def obter_ou_criar(self, nome: str):
        """Retorna o idFornecedor existente para o nome informado ou cria um novo registro."""
        existente = consultar_um(
            "SELECT idFornecedor FROM fornecedores WHERE LOWER(nomeFornecedor) = LOWER(%s)", (nome,),
            erro="Erro ao buscar fornecedor por nome:")
        if existente:
            return existente[0]
        return inserir("INSERT INTO fornecedores (nomeFornecedor) VALUES (%s)", (nome,),
                       erro="Erro ao criar fornecedor:")
