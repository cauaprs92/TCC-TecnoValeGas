from src.dao.obraDAO import ObraDAO
from src.modelo.obra import Obra 
from src.error_response import ErrorResponse

class ObraService:
    def __init__(self, obra_dao_dependency: ObraDAO):
        self.obra_dao = obra_dao_dependency
   
    def createObra(self, obra: Obra) -> Obra:
        try:
            return self.obra_dao.create(obra)
        except Exception as e:
            raise ErrorResponse(f"Erro ao criar obra: {str(e)}")
        
    def find_all(self) -> list[Obra]:
        try:
            return self.obra_dao.find_all()
        except Exception as e:
            raise ErrorResponse(f"Erro ao buscar obras: {str(e)}")
        
    def find_by_id(self, id) -> Obra | None:
        try:
            return self.obra_dao.find_by_id(id)
        except Exception as e:
            raise ErrorResponse(f"Erro ao buscar obra por ID: {str(e)}")
        
    def update(self, obra: Obra) -> Obra:
        try:
            return self.obra_dao.update(obra)
        except Exception as e:
            raise ErrorResponse(f"Erro ao atualizar obra: {str(e)}")
        
    def delete(self, id) -> bool:
        try:
            return self.obra_dao.delete(id)
        except Exception as e:
            raise ErrorResponse(f"Erro ao deletar obra: {str(e)}")