from functools import wraps
from flask import request
from src.error_response import ErrorResponse


class AdminMiddleware:

    def validate_body(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            body = request.get_json()
            if not body or "admin" not in body:
                raise ErrorResponse(400, "Corpo inválido.", {"message": "Campo 'admin' é obrigatório."})
            admin = body["admin"]
            if not admin.get("email", "").strip():
                raise ErrorResponse(400, "Validação falhou.", {"message": "Campo 'email' é obrigatório."})
            if not admin.get("nomeLogin", "").strip():
                raise ErrorResponse(400, "Validação falhou.", {"message": "Campo 'nomeLogin' é obrigatório."})
            if not admin.get("senha", "").strip():
                raise ErrorResponse(400, "Validação falhou.", {"message": "Campo 'senha' é obrigatório."})
            return f(*args, **kwargs)
        return decorated

    def validate_update_body(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            body = request.get_json()
            if not body or "admin" not in body:
                raise ErrorResponse(400, "Corpo inválido.", {"message": "Campo 'admin' é obrigatório."})
            admin = body["admin"]
            if not admin.get("email", "").strip():
                raise ErrorResponse(400, "Validação falhou.", {"message": "Campo 'email' é obrigatório."})
            if not admin.get("nomeLogin", "").strip():
                raise ErrorResponse(400, "Validação falhou.", {"message": "Campo 'nomeLogin' é obrigatório."})
            return f(*args, **kwargs)
        return decorated

    def validate_id_param(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            id_login = kwargs.get("idLogin")
            if id_login is None or id_login <= 0:
                raise ErrorResponse(400, "ID inválido.", {"message": "O ID deve ser um inteiro positivo."})
            return f(*args, **kwargs)
        return decorated
