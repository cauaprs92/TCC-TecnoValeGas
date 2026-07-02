from functools import wraps
from flask import request
from src.error_response import ErrorResponse


class ServicoMiddleware:

    def validate_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 ServicoMiddleware.validate_body()")
            body = request.get_json()

            if not body or 'servico' not in body:
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'servico' é obrigatório!"})

            servico = body['servico']

            nome = servico.get('nomeServico')
            if not isinstance(nome, str) or not nome.strip():
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'nomeServico' é obrigatório!"})
            if len(nome.strip()) < 3:
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'nomeServico' deve ter pelo menos 3 caracteres!"})

            preco = servico.get('precoServico')
            try:
                preco_val = float(preco)
                if preco_val <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'precoServico' deve ser um número maior que zero!"})

            produtos = servico.get('produtos', [])
            if not isinstance(produtos, list):
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'produtos' deve ser uma lista!"})

            for item in produtos:
                if not isinstance(item, dict):
                    raise ErrorResponse(400, "Erro na validação de dados",
                                        {"message": "Cada item em 'produtos' deve ser um objeto!"})
                try:
                    id_p = int(item.get('idProduto'))
                    if id_p <= 0:
                        raise ValueError
                except (ValueError, TypeError):
                    raise ErrorResponse(400, "Erro na validação de dados",
                                        {"message": "O campo 'idProduto' deve ser um inteiro positivo!"})
                try:
                    qtd = int(item.get('quantidade'))
                    if qtd <= 0:
                        raise ValueError
                except (ValueError, TypeError):
                    raise ErrorResponse(400, "Erro na validação de dados",
                                        {"message": "O campo 'quantidade' deve ser um inteiro maior que zero!"})

            return f(*args, **kwargs)
        return decorated_function

    def validate_id_param(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 ServicoMiddleware.validate_id_param()")
            if 'idServico' not in kwargs:
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O parâmetro 'idServico' é obrigatório!"})
            try:
                val = int(kwargs['idServico'])
                if val <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O parâmetro 'idServico' deve ser um número inteiro positivo!"})
            return f(*args, **kwargs)
        return decorated_function
