from flask import Blueprint, request, jsonify, g
from src.controller.clienteController   import ClienteController
from src.controller.historicoController import HistoricoController
from src.middleware.clienteMiddleware   import ClienteMiddleware
from src.middleware.jwtMiddleware       import JwtMiddleware
from src.error_response                 import ErrorResponse

cliente_bp     = Blueprint("cliente", __name__, url_prefix="/cliente")
controller     = ClienteController()
historico_ctrl = HistoricoController()
middleware     = ClienteMiddleware()
jwt            = JwtMiddleware()


@cliente_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


def _serializar(c) -> dict:
    return {
        "idCliente":      c._idCliente,
        "nomeCliente":    c._nomeCliente,
        "CNPJCPF":        c._CNPJCPF,
        "contatoCliente": c._contatoCliente,
        "emailCliente":   c._emailCliente,
        "telefone2":      c._telefone2,
        "cep":            c._cep,
        "rua":            c._rua,
        "numero":         c._numero,
        "complemento":    c._complemento,
        "bairro":         c._bairro,
        "cidade":         c._cidade,
        "estado":         c._estado,
    }


# ─── POST /cliente ────────────────────────────────────────────────────────────
@cliente_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def cadastrar():
    cliente = request.get_json()["cliente"]
    nome    = cliente.get("nomeCliente")

    sucesso, mensagem = controller.cadastrar(
        nome,
        cliente.get("CNPJCPF"),
        cliente.get("contatoCliente", ""),
        cliente.get("emailCliente", ""),
        cliente.get("telefone2", ""),
        cliente.get("cep", ""),
        cliente.get("rua"),
        cliente.get("numero"),
        cliente.get("complemento", ""),
        cliente.get("bairro", ""),
        cliente.get("cidade"),
        cliente.get("estado"),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Cadastrou", "Cliente",
        f"Cadastrou o cliente '{nome}'",
    )

    return jsonify({"status": True, "msg": mensagem}), 201


# ─── GET /cliente ─────────────────────────────────────────────────────────────
@cliente_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    clientes = controller.listar()
    return jsonify({"status": True, "clientes": [_serializar(c) for c in clientes]}), 200


# ─── GET /cliente/<idCliente> ─────────────────────────────────────────────────
@cliente_bp.route("/<int:idCliente>", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_por_id(idCliente: int):
    cliente = controller.buscar_por_id(idCliente)

    if not cliente:
        raise ErrorResponse(404, "Cliente não encontrado.", {"message": f"Nenhum cliente com ID {idCliente}."})

    return jsonify({"status": True, "cliente": _serializar(cliente)}), 200


# ─── PUT /cliente/<idCliente> ─────────────────────────────────────────────────
@cliente_bp.route("/<int:idCliente>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_body
def editar(idCliente: int):
    cliente = request.get_json()["cliente"]
    nome    = cliente.get("nomeCliente")

    sucesso, mensagem = controller.editar(
        idCliente,
        nome,
        cliente.get("CNPJCPF"),
        cliente.get("contatoCliente", ""),
        cliente.get("emailCliente", ""),
        cliente.get("telefone2", ""),
        cliente.get("cep", ""),
        cliente.get("rua"),
        cliente.get("numero"),
        cliente.get("complemento", ""),
        cliente.get("bairro", ""),
        cliente.get("cidade"),
        cliente.get("estado"),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Editou", "Cliente",
        f"Editou o cliente '{nome}' (ID: {idCliente})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /cliente/<idCliente> ──────────────────────────────────────────────
@cliente_bp.route("/<int:idCliente>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def deletar(idCliente: int):
    cliente = controller.buscar_por_id(idCliente)
    nome    = cliente._nomeCliente if cliente else str(idCliente)

    sucesso, mensagem = controller.deletar(idCliente)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Deletou", "Cliente",
        f"Deletou o cliente '{nome}' (ID: {idCliente})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200
