from datetime import datetime
from functools import wraps
from flask import request
from src.error_response import ErrorResponse

STATUS_VALIDOS = ["À iniciar", "Em andamento", "Concluida", "Cancelada", "Pausada"]
FORMATO_DATA   = "%Y-%m-%d"


def _erro(mensagem: str, campo: str = None):
    detalhe = {"message": mensagem}
    if campo:
        detalhe["campo"] = campo
    raise ErrorResponse(400, "Erro na validação de dados", detalhe)


def _inteiro_positivo(valor) -> bool:
    try:
        return int(valor) > 0
    except (ValueError, TypeError):
        return False


class ObraMiddleware:
    """Valida o formato do corpo das rotas de obra. Regras que dependem do
    banco (cliente existe, equipe tem cargo Obra, estoque) ficam no controller."""

    def _data(self, valor, campo):
        if not isinstance(valor, str) or not valor.strip():
            _erro(f"O campo '{campo}' é obrigatório!", campo)
        try:
            return datetime.strptime(valor.strip(), FORMATO_DATA)
        except ValueError:
            _erro(f"O campo '{campo}' é inválido. Use o formato {FORMATO_DATA}!", campo)

    def _validar_obra(self, body: dict):
        if not body or not isinstance(body.get("obra"), dict):
            _erro("O campo 'obra' é obrigatório!")
        obra = body["obra"]

        if not _inteiro_positivo(obra.get("codCliente")):
            _erro("O ID do cliente deve ser um número inteiro positivo!", "codCliente")

        desc = obra.get("descObra")
        if not isinstance(desc, str) or not desc.strip():
            _erro("A descrição da obra é obrigatória!", "descObra")

        inicio = self._data(obra.get("dataInicio"), "dataInicio")
        if obra.get("dataFim"):
            fim = self._data(obra.get("dataFim"), "dataFim")
            if fim < inicio:
                _erro("A data fim não pode ser anterior à data de início!", "dataFim")

        if obra.get("statusObra") not in STATUS_VALIDOS:
            _erro(f"Status inválido. Use: {', '.join(STATUS_VALIDOS)}!", "statusObra")

        resp = obra.get("respObra")
        if not isinstance(resp, str) or not resp.strip():
            _erro("Selecione o field responsável pela obra!", "respObra")

    def _validar_produtos(self, body: dict, campo: str) -> list:
        produtos = body.get(campo) or []
        if not isinstance(produtos, list):
            _erro(f"O campo '{campo}' deve ser uma lista!", campo)
        for i, item in enumerate(produtos):
            if not isinstance(item, dict) or not (
                _inteiro_positivo(item.get("idProduto")) and _inteiro_positivo(item.get("quantidade"))
            ):
                _erro(f"{campo}[{i}]: 'idProduto' e 'quantidade' devem ser inteiros positivos!", campo)
        return produtos

    def _validar_ids(self, body: dict, campo: str) -> list:
        """Lista opcional de IDs positivos (serviços, equipe)."""
        ids = body.get(campo) or []
        if not isinstance(ids, list):
            _erro(f"O campo '{campo}' deve ser uma lista!", campo)
        for i, valor in enumerate(ids):
            if not _inteiro_positivo(valor):
                _erro(f"{campo}[{i}]: deve ser um inteiro positivo!", campo)
        return ids

    def validate_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            body = request.get_json()
            self._validar_obra(body)
            produtos = self._validar_produtos(body, "produtosUsados")
            servicos = self._validar_ids(body, "servicosVinculados")
            if not produtos and not servicos:
                _erro("Informe ao menos um produto ou serviço para a obra!")
            self._validar_ids(body, "funcionarios")
            return f(*args, **kwargs)
        return decorated_function

    def validate_update_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            body = request.get_json()
            self._validar_obra(body)
            self._validar_produtos(body, "produtosNovos")
            self._validar_ids(body, "servicosNovos")
            # Ausente = a rota não mexe na equipe; o formato só é checado se vier.
            self._validar_ids(body, "funcionarios")
            return f(*args, **kwargs)
        return decorated_function
