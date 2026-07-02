from datetime import datetime
from functools import wraps
from flask import request
from src.error_response import ErrorResponse


class ObraMiddleware:

    STATUS_VALIDOS = ["À iniciar", "Em andamento", "Concluida", "Cancelada", "Pausada"]
    FORMATO_DATA = "%Y-%m-%d"

    def _validar_data(self, valor, campo):
        if not isinstance(valor, str) or not valor.strip():
            raise ErrorResponse(
                400, "Erro na validação de dados",
                {"campo": campo, "message": f"O campo '{campo}' é obrigatório!"}
            )
        try:
            datetime.strptime(valor.strip(), self.FORMATO_DATA)
        except ValueError:
            raise ErrorResponse(
                400, "Erro na validação de dados",
                {"campo": campo, "message": f"O campo '{campo}' é inválido. Use o formato {self.FORMATO_DATA}!"}
            )

    def validate_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 ObraMiddleware.validate_body()")
            body = request.get_json()

            if not body or 'obra' not in body:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'obra' é obrigatório!"}
                )

            obra = body['obra']

            cod_cliente = obra.get('codCliente')
            try:
                val = int(cod_cliente)
                if val <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "codCliente", "message": "O ID do cliente deve ser um número inteiro positivo!"}
                )

            desc = obra.get('descObra')
            if not isinstance(desc, str) or not desc.strip():
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "descObra", "message": "A descrição da obra é obrigatória!"}
                )

            self._validar_data(obra.get('dataInicio'), 'dataInicio')

            data_fim = obra.get('dataFim')
            if data_fim:
                self._validar_data(data_fim, 'dataFim')

            status = obra.get('statusObra')
            if status not in self.STATUS_VALIDOS:
                opcoes = ", ".join(self.STATUS_VALIDOS)
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "statusObra", "message": f"Status inválido. Use: {opcoes}!"}
                )

            resp = obra.get('respObra')
            if not isinstance(resp, str) or not resp.strip():
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "respObra", "message": "Selecione o field responsável pela obra!"}
                )

            produtos = body.get('produtosUsados', [])
            if not isinstance(produtos, list):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "produtosUsados", "message": "O campo 'produtosUsados' deve ser uma lista!"}
                )

            for i, item in enumerate(produtos):
                if not isinstance(item, dict):
                    raise ErrorResponse(
                        400, "Erro na validação de dados",
                        {"campo": "produtosUsados", "message": f"Item {i} da lista de produtos é inválido!"}
                    )
                if 'idProduto' not in item or 'quantidade' not in item:
                    raise ErrorResponse(
                        400, "Erro na validação de dados",
                        {"campo": "produtosUsados", "message": f"Item {i} deve conter 'idProduto' e 'quantidade'!"}
                    )
                try:
                    id_p = int(item['idProduto'])
                    qtd  = int(item['quantidade'])
                except (ValueError, TypeError):
                    raise ErrorResponse(
                        400, "Erro na validação de dados",
                        {"campo": "produtosUsados", "message": f"Item {i}: 'idProduto' e 'quantidade' devem ser inteiros!"}
                    )
                if id_p <= 0:
                    raise ErrorResponse(
                        400, "Erro na validação de dados",
                        {"campo": "produtosUsados", "message": f"Item {i}: 'idProduto' deve ser positivo!"}
                    )
                if qtd <= 0:
                    raise ErrorResponse(
                        400, "Erro na validação de dados",
                        {"campo": "produtosUsados", "message": f"Item {i}: a quantidade deve ser maior que zero!"}
                    )

            servicos = body.get('servicosVinculados', [])
            if not isinstance(servicos, list):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "servicosVinculados", "message": "O campo 'servicosVinculados' deve ser uma lista!"}
                )
            for i, id_s in enumerate(servicos):
                try:
                    val = int(id_s)
                    if val <= 0:
                        raise ValueError
                except (ValueError, TypeError):
                    raise ErrorResponse(
                        400, "Erro na validação de dados",
                        {"campo": "servicosVinculados", "message": f"servicosVinculados[{i}]: deve ser um inteiro positivo!"}
                    )

            if len(produtos) == 0 and len(servicos) == 0:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "Informe ao menos um produto ou serviço para a obra!"}
                )

            return f(*args, **kwargs)
        return decorated_function

    def validate_update_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 ObraMiddleware.validate_update_body()")
            body = request.get_json()

            if not body or 'obra' not in body:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'obra' é obrigatório!"}
                )

            obra = body['obra']

            cod_cliente = obra.get('codCliente')
            try:
                val = int(cod_cliente)
                if val <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "codCliente", "message": "O ID do cliente deve ser um número inteiro positivo!"}
                )

            desc = obra.get('descObra')
            if not isinstance(desc, str) or not desc.strip():
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "descObra", "message": "A descrição da obra é obrigatória!"}
                )

            self._validar_data(obra.get('dataInicio'), 'dataInicio')

            data_fim = obra.get('dataFim')
            if data_fim:
                self._validar_data(data_fim, 'dataFim')

            status = obra.get('statusObra')
            if status not in self.STATUS_VALIDOS:
                opcoes = ", ".join(self.STATUS_VALIDOS)
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "statusObra", "message": f"Status inválido. Use: {opcoes}!"}
                )

            resp = obra.get('respObra')
            if not isinstance(resp, str) or not resp.strip():
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"campo": "respObra", "message": "Selecione o field responsável pela obra!"}
                )

            # produtosNovos — opcional, mas se vier deve ser válido
            produtos_novos = body.get('produtosNovos')
            if produtos_novos is not None:
                if not isinstance(produtos_novos, list):
                    raise ErrorResponse(
                        400, "Erro na validação de dados",
                        {"campo": "produtosNovos", "message": "O campo 'produtosNovos' deve ser uma lista!"}
                    )
                for i, item in enumerate(produtos_novos):
                    try:
                        id_p = int(item['idProduto'])
                        qtd  = int(item['quantidade'])
                    except (ValueError, TypeError, KeyError):
                        raise ErrorResponse(
                            400, "Erro na validação de dados",
                            {"campo": "produtosNovos", "message": f"produtosNovos[{i}]: 'idProduto' e 'quantidade' devem ser inteiros!"}
                        )
                    if id_p <= 0 or qtd <= 0:
                        raise ErrorResponse(
                            400, "Erro na validação de dados",
                            {"campo": "produtosNovos", "message": f"produtosNovos[{i}]: valores devem ser positivos!"}
                        )

            # servicosNovos — opcional, mas se vier deve ser válido
            servicos_novos = body.get('servicosNovos')
            if servicos_novos is not None:
                if not isinstance(servicos_novos, list):
                    raise ErrorResponse(
                        400, "Erro na validação de dados",
                        {"campo": "servicosNovos", "message": "O campo 'servicosNovos' deve ser uma lista!"}
                    )
                for i, id_s in enumerate(servicos_novos):
                    try:
                        val = int(id_s)
                        if val <= 0:
                            raise ValueError
                    except (ValueError, TypeError):
                        raise ErrorResponse(
                            400, "Erro na validação de dados",
                            {"campo": "servicosNovos", "message": f"servicosNovos[{i}]: deve ser um inteiro positivo!"}
                        )

            return f(*args, **kwargs)
        return decorated_function

    def validate_id_param(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 ObraMiddleware.validate_id_param()")
            if 'idObra' not in kwargs:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O parâmetro 'idObra' é obrigatório!"}
                )
            try:
                val = int(kwargs['idObra'])
                if val <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O parâmetro 'idObra' deve ser um número inteiro positivo!"}
                )
            return f(*args, **kwargs)
        return decorated_function

    def validate_status_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 ObraMiddleware.validate_status_body()")
            body = request.get_json()

            if not body or 'statusObra' not in body:
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": "O campo 'statusObra' é obrigatório!"}
                )

            if body['statusObra'] not in self.STATUS_VALIDOS:
                opcoes = ", ".join(self.STATUS_VALIDOS)
                raise ErrorResponse(
                    400, "Erro na validação de dados",
                    {"message": f"O campo 'statusObra' é inválido. Use: {opcoes}!"}
                )

            return f(*args, **kwargs)
        return decorated_function
