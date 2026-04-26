from src.dao.produtoDAO import ProdutoDAO
from src.modelo.produto import Produto
from src.error_response import ErrorResponse

class ProdutoService:
    def __init__(self, produto_dao_dependency: ProdutoDAO):
        self.produto_dao = produto_dao_dependency
    
    def createProduto(self, produto: Produto) -> Produto:
        try:
            return self.produto_dao.create(produto)
        except Exception as e:
            raise ErrorResponse(f"Erro ao criar produto: {str(e)}")
        
    def find_all(self) -> list[Produto]:
        try:
            return self.produto_dao.find_all()
        except Exception as e:
            raise ErrorResponse(f"Erro ao buscar produtos: {str(e)}")

    def find_by_id(self, id) -> Produto | None:
        try:
            return self.produto_dao.find_by_id(id)
        except Exception as e:
            raise ErrorResponse(f"Erro ao buscar produto por ID: {str(e)}")

    def update(self, produto: Produto) -> Produto:
        try:
            return self.produto_dao.update(produto)
        except Exception as e:
            raise ErrorResponse(f"Erro ao atualizar produto: {str(e)}")

    def delete(self, id) -> bool:
        try:
            return self.produto_dao.delete(id)
        except Exception as e:
            raise ErrorResponse(f"Erro ao deletar produto: {str(e)}")