from flask import Blueprint, request, jsonify, g
from src.controller.servicoController   import ServicoController
from src.controller.historicoController import HistoricoController
from src.middleware.servicoMiddleware   import ServicoMiddleware
from src.middleware.jwtMiddleware       import JwtMiddleware
from src.error_response                 import ErrorResponse

servico_bp     = Blueprint("servico", __name__, url_prefix="/servico")
controller     = ServicoController()
historico_ctrl = HistoricoController()
middleware     = ServicoMiddleware()
jwt            = JwtMiddleware()


@servico_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


def _serializar(s) -> dict:
    return {
        "idServico":    s._idServico,
        "nomeServico":  s._nomeServico,
        "precoServico": float(s._precoServico) if s._precoServico is not None else None,
        "produtos":     s._produtos,
    }


# ─── POST /servico ────────────────────────────────────────────────────────────
@servico_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def cadastrar():
    servico = request.get_json()["servico"]
    nome    = servico.get("nomeServico")

    sucesso, mensagem, idServico = controller.cadastrar(
        nome,
        servico.get("precoServico"),
        servico.get("produtos", []),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Cadastrou", "Serviço",
        f"Cadastrou o serviço '{nome}'",
    )

    return jsonify({"status": True, "msg": mensagem, "idServico": idServico}), 201


# ─── GET /servico ─────────────────────────────────────────────────────────────
@servico_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    servicos = controller.listar()
    return jsonify({"status": True, "servicos": [_serializar(s) for s in servicos]}), 200


# ─── GET /servico/<idServico> ─────────────────────────────────────────────────
@servico_bp.route("/<int:idServico>", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_por_id(idServico: int):
    servico = controller.buscar_por_id(idServico)

    if not servico:
        raise ErrorResponse(404, "Serviço não encontrado.", {"message": f"Nenhum serviço com ID {idServico}."})

    return jsonify({"status": True, "servico": _serializar(servico)}), 200


# ─── PUT /servico/<idServico> ─────────────────────────────────────────────────
@servico_bp.route("/<int:idServico>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_body
def editar(idServico: int):
    servico = request.get_json()["servico"]
    nome    = servico.get("nomeServico")

    sucesso, mensagem = controller.editar(
        idServico,
        nome,
        servico.get("precoServico"),
        servico.get("produtos", []),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Editou", "Serviço",
        f"Editou o serviço '{nome}' (ID: {idServico})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /servico/<idServico> ──────────────────────────────────────────────
@servico_bp.route("/<int:idServico>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def deletar(idServico: int):
    servico = controller.buscar_por_id(idServico)
    nome    = servico._nomeServico if servico else str(idServico)

    sucesso, mensagem = controller.deletar(idServico)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Deletou", "Serviço",
        f"Deletou o serviço '{nome}' (ID: {idServico})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── GET /servico/<idServico>/produtos ────────────────────────────────────────
@servico_bp.route("/<int:idServico>/produtos", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_produtos(idServico: int):
    servico = controller.buscar_por_id(idServico)

    if not servico:
        raise ErrorResponse(404, "Serviço não encontrado.", {"message": f"Nenhum serviço com ID {idServico}."})

    return jsonify({"status": True, "produtos": servico._produtos}), 200
