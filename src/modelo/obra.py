import re
from datetime import datetime

class Obra:
    def __init__(self):
        self._idObra = None
        self._codCliente = None
        self._codProduto = None
        self._descObra = None
        self._dataObra = None
        self._statusObra = None
        self._respObra = None
        self._obsObra = None
        self._orientacaoObra = None

    @property
    def idObra(self):
        return self._idObra

    @idObra.setter
    def idObra(self, value):
        try:
            id_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("idObra deve ser um número inteiro.")
        
        if id_val <= 0:
            raise ValueError("idObra deve ser positivo.")
        
        self._idObra = id_val

    @property
    def codCliente(self):
        return self._codCliente

    @codCliente.setter
    def codCliente(self, value):
        try:
            cod_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("codCliente deve ser um número inteiro.")
        
        if cod_val <= 0:
            raise ValueError("codCliente deve ser positivo.")
        
        self._codCliente = cod_val

    @property
    def codProduto(self):
        return self._codProduto

    @codProduto.setter
    def codProduto(self, value):
        try:
            cod_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("codProduto deve ser um número inteiro.")
        
        if cod_val <= 0:
            raise ValueError("codProduto deve ser positivo.")
        
        self._codProduto = cod_val

    @property
    def descObra(self):
        return self._descObra

    @descObra.setter
    def descObra(self, value):
        if not isinstance(value, str):
            raise ValueError("descObra deve ser uma string.")
        
        desc = value.strip()
        
        if len(desc) == 0:
            raise ValueError("descObra não pode ser vazia.")
        
        self._descObra = desc

    @property
    def dataObra(self):
        return self._dataObra

    @dataObra.setter
    def dataObra(self, value):
        if isinstance(value, str):
            try:
                # Assume format YYYY-MM-DD
                datetime.strptime(value, '%Y-%m-%d')
                self._dataObra = value
            except ValueError:
                raise ValueError("dataObra deve estar no formato YYYY-MM-DD.")
        elif isinstance(value, datetime):
            self._dataObra = value.strftime('%Y-%m-%d')
        else:
            raise ValueError("dataObra deve ser uma string no formato YYYY-MM-DD ou um objeto datetime.")

    @property
    def statusObra(self):
        return self._statusObra

    @statusObra.setter
    def statusObra(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("statusObra deve ser uma string ou None.")
        
        self._statusObra = value.strip() if value else None

    @property
    def respObra(self):
        return self._respObra

    @respObra.setter
    def respObra(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("respObra deve ser uma string ou None.")
        
        self._respObra = value.strip() if value else None

    @property
    def obsObra(self):
        return self._obsObra

    @obsObra.setter
    def obsObra(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("obsObra deve ser uma string ou None.")
        
        self._obsObra = value.strip() if value else None

    @property
    def orientacaoObra(self):
        return self._orientacaoObra

    @orientacaoObra.setter
    def orientacaoObra(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("orientacaoObra deve ser uma string ou None.")
        
        self._orientacaoObra = value.strip() if value else None