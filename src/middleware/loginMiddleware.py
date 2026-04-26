import re
from functools import wraps
from flask import request
from src.error_response import ErrorResponse


class LoginMiddleware:

    EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    SENHA_MIN = 6

    def validate_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 LoginMiddleware.validate_body()")
            body = request.get_json()

            if not body:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O corpo da requisição é obrigatório!"}
                )

            email = body.get('email')
            senha = body.get('senha')

            if not email or not isinstance(email, str) or not email.strip():
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'email' é obrigatório!"}
                )

            if not self.EMAIL_REGEX.match(email.strip()):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'email' é inválido!"}
                )

            if not senha or not isinstance(senha, str) or not senha.strip():
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'senha' é obrigatório!"}
                )

            if len(senha) < self.SENHA_MIN:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": f"O campo 'senha' deve ter pelo menos {self.SENHA_MIN} caracteres!"}
                )

            return f(*args, **kwargs)
        return decorated_function