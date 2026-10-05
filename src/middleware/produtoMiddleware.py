from functools import wraps
from flask import request
from src.error_response import ErrorResponse


class ProdutoMiddleware:

    def validate_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            body = request.get_json()

            if not body or 'produto' not in body:
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'produto' é obrigatório!"})

            produto = body['produto']

            nome = produto.get('nomeProduto')
            if not isinstance(nome, str) or not nome.strip():
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'nomeProduto' é obrigatório!"})
            if len(nome.strip()) < 3:
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'nomeProduto' deve ter pelo menos 3 caracteres!"})

            qtd = produto.get('qtdProduto')
            try:
                qtd_val = int(qtd)
            except (ValueError, TypeError):
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'qtdProduto' deve ser um número inteiro!"})
            if qtd_val < 0:
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'qtdProduto' não pode ser negativo!"})

            for campo in ('qtdMaxima', 'qtdMinimaManual'):
                val = produto.get(campo)
                if val is not None and val != "":
                    try:
                        int(val)
                    except (ValueError, TypeError):
                        raise ErrorResponse(400, "Erro na validação de dados",
                                            {"message": f"O campo '{campo}' deve ser um número inteiro!"})

            desc = produto.get('descProduto')
            if desc is not None and not isinstance(desc, str):
                raise ErrorResponse(400, "Erro na validação de dados",
                                    {"message": "O campo 'descProduto' deve ser texto!"})

            return f(*args, **kwargs)
        return decorated_function
