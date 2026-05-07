from functools import wraps
from flask import request
from src.error_response import ErrorResponse


class ProdutoMiddleware:

    QTD_MAXIMA = 9999

    def validate_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 ProdutoMiddleware.validate_body()")
            body = request.get_json()

            if not body or 'produto' not in body:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'produto' é obrigatório!"}
                )

            produto = body['produto']

            # nomeProduto
            nome = produto.get('nomeProduto')
            if not isinstance(nome, str) or not nome.strip():
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'nomeProduto' é obrigatório!"}
                )
            if len(nome.strip()) < 3:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'nomeProduto' deve ter pelo menos 3 caracteres!"}
                )

            # qtdProduto
            qtd = produto.get('qtdProduto')
            try:
                qtd_val = int(qtd)
            except (ValueError, TypeError):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'qtdProduto' deve ser um número inteiro!"}
                )
            if qtd_val < 0:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'qtdProduto' não pode ser negativo!"}
                )
            if qtd_val > self.QTD_MAXIMA:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": f"O campo 'qtdProduto' não pode ultrapassar {self.QTD_MAXIMA} unidades!"}
                )

            # descProduto (opcional)
            desc = produto.get('descProduto')
            if desc is not None and not isinstance(desc, str):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'descProduto' deve ser texto!"}
                )

            return f(*args, **kwargs)
        return decorated_function

    def validate_id_param(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 ProdutoMiddleware.validate_id_param()")
            if 'idProduto' not in kwargs:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O parâmetro 'idProduto' é obrigatório!"}
                )
            try:
                val = int(kwargs['idProduto'])
                if val <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O parâmetro 'idProduto' deve ser um número inteiro positivo!"}
                )
            return f(*args, **kwargs)
        return decorated_function

    def validate_uso_em_obra_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 ProdutoMiddleware.validate_uso_em_obra_body()")
            body = request.get_json()

            if not body:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O corpo da requisição é obrigatório!"}
                )

            # idProduto
            id_produto = body.get('idProduto')
            try:
                id_val = int(id_produto)
                if id_val <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'idProduto' deve ser um número inteiro positivo!"}
                )

            # quantidade
            quantidade = body.get('quantidade')
            try:
                qtd_val = int(quantidade)
            except (ValueError, TypeError):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'quantidade' deve ser um número inteiro!"}
                )
            if qtd_val <= 0:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'quantidade' deve ser maior que zero!"}
                )
            if qtd_val > self.QTD_MAXIMA:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": f"O campo 'quantidade' não pode ultrapassar {self.QTD_MAXIMA} unidades!"}
                )

            return f(*args, **kwargs)
        return decorated_function