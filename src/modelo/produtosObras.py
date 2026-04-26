class produtosObra:
    def __init__(self):
        self._idProdutosObra = None
        self._qtdProdutosObra = None
        self._idProduto = None  # FK referenciando produtos

    @property
    def idProdutosObra(self):
        return self._idProdutosObra

    @idProdutosObra.setter
    def idProdutosObra(self, value):
        try:
            id_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("idProdutosObra deve ser um número inteiro.")

        if id_val <= 0:
            raise ValueError("idProdutosObra deve ser positivo.")

        self._idProdutosObra = id_val

    @property
    def qtdProdutosObra(self):
        return self._qtdProdutosObra

    @qtdProdutosObra.setter
    def qtdProdutosObra(self, value):
        try:
            qtd_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("qtdProdutosObra deve ser um número inteiro.")

        if qtd_val <= 0:
            raise ValueError("qtdProdutosObra deve ser maior que 0.")

        self._qtdProdutosObra = qtd_val

    @property
    def idProduto(self):
        return self._idProduto

    @idProduto.setter
    def idProduto(self, value):
        try:
            id_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("idProduto deve ser um número inteiro.")

        if id_val <= 0:
            raise ValueError("idProduto deve ser positivo.")

        self._idProduto = id_val