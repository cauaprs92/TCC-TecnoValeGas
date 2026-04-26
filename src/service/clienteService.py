from src.dao.clienteDAO import ClienteDAO
from src.modelo.cliente import Cliente
from src.error_response import ErrorResponse

class ClienteService:
    def __init__(self, cliente_dao_dependency: ClienteDAO):
        self.cliente_dao = cliente_dao_dependency
   
    def createCliente(self, cliente: Cliente) -> Cliente:
        try:
            return self.cliente_dao.create(cliente)
        except Exception as e:
            raise ErrorResponse(f"Erro ao criar cliente: {str(e)}")
        
    def find_all(self) -> list[Cliente]:
        try:
            return self.cliente_dao.find_all()
        except Exception as e:
            raise ErrorResponse(f"Erro ao buscar clientes: {str(e)}")
        
    def find_by_id(self, id) -> Cliente | None:
        try:
            return self.cliente_dao.find_by_id(id)
        except Exception as e:
            raise ErrorResponse(f"Erro ao buscar cliente por ID: {str(e)}")
        
    def update(self, cliente: Cliente) -> Cliente:
        try:
            return self.cliente_dao.update(cliente)
        except Exception as e:
            raise ErrorResponse(f"Erro ao atualizar cliente: {str(e)}")
        
    def delete(self, id) -> bool:
        try:
            return self.cliente_dao.delete(id)
        except Exception as e:
            raise ErrorResponse(f"Erro ao deletar cliente: {str(e)}")