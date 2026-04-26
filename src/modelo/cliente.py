class Cliente:
    def __init__(self):
        self._idCliente = None
        self._nomeCliente = None
        self._CNPJCPF = None
        self._enderecoCliente = None
        self._contatoCliente = None 

    @property
    def idCliente (self):
        return self._idCliente
    @idCliente.setter
    def idCliente(self, valor):   
        try:
            parsed = int(valor)
        except (ValueError, TypeError):
            raise ValueError("idCliente deve ser um número inteiro.")

        if parsed <= 0:
            raise ValueError("idCliente deve ser um número inteiro positivo.")

        self._idCliente = parsed

    @property
    def nomeCliente(self):
        """
        Getter para nome
        :return: str - Nome do Cliente 
        """
        return self.__nomeCliente
    @nomeCliente.setter
    def nome(self, value):
        if not isinstance(value, str):
            raise ValueError("nomeCliente deve ser uma string.")

        nomeCliente = value.strip()

        if len(nomeCliente) < 3:
            raise ValueError("nomeCliente deve ter pelo menos 3 caracteres.")
        self.__nomeCliente = nomeCliente
