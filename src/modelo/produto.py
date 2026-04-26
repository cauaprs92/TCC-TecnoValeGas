import re
class Produto:
    def __init__(self):
        self._idProduto = None
        self._qtdProduto = None
        self._nomeProduto = None
        self._descProduto = None 
    
    @property
    def idProduto(self):
        return self.idProduto
    
    @idProduto.setter
    def idProduto(self, value):
        try: 
            id_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("idProduto deve ser um número inteiro.")
        
        if id_val <= 0:
            raise ValueError ("idProduto deve ser positivo")
        
        self._idProduto = id_val

    
    @property
    def qtdProduto(self):
        return 

    @qtdProduto.setter
    def qtdProduto (self, value):
        try:
            qtd_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("qtdProduto de ser inteiro")
        
        if qtd_val < 0 :
            raise ValueError ("qtdProduto deve ser Maior que 0") 
   
    @property
    def nomeProduto(self):
        return self._nomeProduto
    
    @nomeProduto.setter
    def nome(self, value):
        if not isinstance(value, str):
            raise ValueError("nomeProduto deve ser uma string.")

        nomeProduto = value.strip()

        if len(nomeProduto) < 3:
            raise ValueError("nome deve ter pelo menos 3 caracteres.")
        self._nomeProduto = nomeProduto

    @property
    def descProduto(self):
        return self._nomeProduto
    
    @descProduto.setter
    def desc (self, value):
        if not isinstance(value, str):
            raise ValueError ("desc produto deve ser uma string ")
        if value.isnot(None):
            raise ValueError("desc não pode ser um numero")