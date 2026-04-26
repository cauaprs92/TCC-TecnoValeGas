from flask import Blueprint, request, jsonify
from src.controller.clienteController import ClienteController
from src.middleware.clienteMiddleware  import ClienteMiddleware
from src.middleware.jwtMiddleware      import JwtMiddleware
from src.error_response                import ErrorResponse

cliente_bp  = Blueprint("cliente", __name__, url_prefix="/cliente")
controller  = ClienteController()
middleware  = ClienteMiddleware()
jwt         = JwtMiddleware()


@cliente_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


# ─── POST /cliente ────────────────────────────────────────────────────────────
@cliente_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def cadastrar():
    """Cadastra um novo cliente."""
    body    = request.get_json()
    cliente = body["cliente"]

    sucesso, mensagem = controller.cadastrar(
        cliente.get("idCliente"),
        cliente.get("nomeCliente"),
        cliente.get("CNPJCPF"),
        cliente.get("enderecoCliente"),
        cliente.get("contatoCliente"),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 201


# ─── GET /cliente ─────────────────────────────────────────────────────────────
@cliente_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    """Lista todos os clientes."""
    clientes = controller.listar()

    resultado = [
        {
            "idCliente":       c._idCliente,
            "nomeCliente":     c._nomeCliente,
            "CNPJCPF":         c._CNPJCPF,
            "enderecoCliente": c._enderecoCliente,
            "contatoCliente":  c._contatoCliente,
        }
        for c in clientes
    ]

    return jsonify({"status": True, "clientes": resultado}), 200


# ─── GET /cliente/<idCliente> ─────────────────────────────────────────────────
@cliente_bp.route("/<int:idCliente>", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_por_id(idCliente: int):
    """Busca um cliente pelo ID."""
    cliente = controller.buscar_por_id(idCliente)

    if not cliente:
        raise ErrorResponse(404, "Cliente não encontrado.", {"message": f"Nenhum cliente com ID {idCliente}."})

    resultado = {
        "idCliente":       cliente._idCliente,
        "nomeCliente":     cliente._nomeCliente,
        "CNPJCPF":         cliente._CNPJCPF,
        "enderecoCliente": cliente._enderecoCliente,
        "contatoCliente":  cliente._contatoCliente,
    }

    return jsonify({"status": True, "cliente": resultado}), 200


# ─── PUT /cliente/<idCliente> ─────────────────────────────────────────────────
@cliente_bp.route("/<int:idCliente>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_body
def editar(idCliente: int):
    """Atualiza os dados de um cliente existente."""
    body    = request.get_json()
    cliente = body["cliente"]

    sucesso, mensagem = controller.editar(
        idCliente,
        cliente.get("nomeCliente"),
        cliente.get("CNPJCPF"),
        cliente.get("enderecoCliente"),
        cliente.get("contatoCliente"),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /cliente/<idCliente> ──────────────────────────────────────────────
@cliente_bp.route("/<int:idCliente>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def deletar(idCliente: int):
    """Remove um cliente pelo ID."""
    sucesso, mensagem = controller.deletar(idCliente)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 200