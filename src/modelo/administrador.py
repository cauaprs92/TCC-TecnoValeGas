import re

class administrador:
    def __init__(self):
        
        self._idAdministrador = None
        self._email = None
        self._senha = None
        self._nomeAdministrador = None
    
    @property
    def idAdministrador(self):
        return self._idAdministrador
    
    @idAdministrador.setter
    def idAdministrador(self, value):
        try:
            id_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("idAdministrador deve ser um número inteiro.")
        
        if id_val <= 0:
            raise ValueError("idAdministrador deve ser positivo.")
        
        self._idAdministrador = id_val

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str):
            raise ValueError("email deve ser uma string.")
        
        email = value.strip()
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            raise ValueError("email inválido.")
        
        self._email = email

    @property
    def senha(self):
        return self.__senha

    @senha.setter
    def senha(self, value):
        if not isinstance(value, str):
            raise ValueError("senha deve ser uma string.")
        
        if len(value) < 6:
            raise ValueError("senha deve ter pelo menos 6 caracteres.")
        
        self.__senha = value

    @property
    def ativo(self):
        return self.__ativo

    @ativo.setter
    def ativo(self, value):
        self.__ativo = bool(value)

    