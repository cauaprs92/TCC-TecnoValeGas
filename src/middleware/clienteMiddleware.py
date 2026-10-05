from functools import wraps
from flask import request
from src.error_response import ErrorResponse

class ClienteMiddleware:
    def validate_body(self, f):
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            body = request.get_json()

            if not body or 'cliente' not in body:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'cliente' é obrigatório!"}
                )

            cliente = body['cliente']
            if 'nomeCliente' not in cliente:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'nomeCliente' é obrigatório!"}
                )

            return f(*args, **kwargs)
        return decorated_function

    def validate_id_param(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'idCliente' not in kwargs:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O parâmetro 'idCliente' é obrigatório!"}
                )
            return f(*args, **kwargs)
        return decorated_function