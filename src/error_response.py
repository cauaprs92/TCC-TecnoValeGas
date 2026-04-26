class ErrorResponse(Exception):
    def __init__(self, httpCode: int, message: str, error: any = None):
        """
        Construtor da classe ErrorResponse

        :param httpCode: Código de status HTTP (ex: 400, 404, 500)
        :param message: Mensagem de erro descritiva
        :param error: Objeto adicional com detalhes do erro (opcional)
        """
        super().__init__(message)
        self.__httpCode = httpCode
        self.__error = error

    @property
    def httpCode(self) -> int:
        """Retorna o código HTTP associado ao erro"""
        return self.__httpCode

    @property
    def error(self):
        """Retorna informações adicionais sobre o erro"""
        return self.__error

    def __str__(self) -> str:
        """Representação textual do erro"""
        return f"[{self.__httpCode}] {self.args[0]} | Detalhes: {self.__error}"