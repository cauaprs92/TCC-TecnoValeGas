from flask import Blueprint, request, jsonify
from src.controller.obraController import ObraController
from src.middleware.obraMiddleware  import ObraMiddleware
from src.middleware.jwtMiddleware   import JwtMiddleware
from src.error_response             import ErrorResponse

obra_bp    = Blueprint("obra", __name__, url_prefix="/obra")
controller = ObraController()
middleware = ObraMiddleware()
jwt        = JwtMiddleware()


@obra_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


# ─── POST /obra ───────────────────────────────────────────────────────────────
@obra_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def cadastrar():
    """Cadastra uma nova obra com os produtos utilizados."""
    body           = request.get_json()
    dados_obra     = body["obra"]
    produtos_usados = body["produtosUsados"]

    sucesso, mensagem = controller.cadastrar(dados_obra, produtos_usados)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 201


# ─── GET /obra ────────────────────────────────────────────────────────────────
@obra_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    """Lista todas as obras."""
    obras = controller.listar()

    resultado = [
        {
            "idObra":      idObra,
            "codCliente":  codCliente,
            "descObra":    descObra,
            "dataObra":    str(dataObra) if dataObra else None,
            "statusObra":  statusObra,
            "respObra":    respObra,
        }
        for idObra, codCliente, descObra, dataObra, statusObra, respObra, *_ in obras
    ]

    return jsonify({"status": True, "obras": resultado}), 200


# ─── GET /obra/<idObra> ───────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_por_id(idObra: int):
    """Busca uma obra pelo ID."""
    obra = controller.buscar_por_id(idObra)

    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    obra = tuple(obra)
    codCliente = obra[1]
    descObra = obra[3]
    dataObra = obra[4]
    statusObra = obra[5]
    respObra = obra[6]

    resultado = {
        "idObra":     idObra,
        "codCliente": codCliente,
        "descObra":   descObra,
        "dataObra":   str(dataObra) if dataObra else None,
        "statusObra": statusObra,
        "respObra":   respObra,
    }

    return jsonify({"status": True, "obra": resultado}), 200


# ─── GET /obra/cliente/<idCliente> ────────────────────────────────────────────
@obra_bp.route("/cliente/<int:idCliente>", methods=["GET"])
@jwt.validate_token
def listar_por_cliente(idCliente: int):
    """Lista todas as obras de um determinado cliente."""
    sucesso, mensagem, obras = controller.listar_por_cliente(idCliente)

    if not sucesso:
        raise ErrorResponse(404, mensagem, {"message": mensagem})

    resultado = [
        {
            "idObra":     idObra,
            "codCliente": codCliente,
            "descObra":   descObra,
            "dataObra":   str(dataObra) if dataObra else None,
            "statusObra": statusObra,
            "respObra":   respObra,
        }
        for idObra, codCliente, descObra, dataObra, statusObra, respObra, *_ in obras
    ]

    return jsonify({"status": True, "msg": mensagem, "obras": resultado}), 200


# ─── GET /obra/<idObra>/produtos ──────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/produtos", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_produtos_da_obra(idObra: int):
    """Lista os produtos utilizados em uma obra."""
    obra = controller.buscar_por_id(idObra)
    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    produtos = controller.buscar_produtos_da_obra(idObra)

    return jsonify({"status": True, "produtos": produtos}), 200


# ─── PATCH /obra/<idObra>/status ─────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/status", methods=["PATCH"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_status_body
def atualizar_status(idObra: int):
    """Atualiza apenas o status de uma obra."""
    body       = request.get_json()
    novo_status = body["statusObra"]

    sucesso, mensagem = controller.atualizar_status(idObra, novo_status)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /obra/<idObra> ────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def deletar(idObra: int):
    """Remove uma obra pelo ID."""
    sucesso, mensagem = controller.deletar(idObra)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 200