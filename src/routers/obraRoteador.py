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


def _serializar(o):
    return {
        "idObra":         o[0],
        "codCliente":     o[1],
        "descObra":       o[2],
        "dataInicio":     str(o[3]) if o[3] else None,
        "dataFim":        str(o[4]) if o[4] else None,
        "statusObra":     o[5],
        "respObra":       o[6],
        "obsObra":        o[7],
        "orientacaoObra": o[8],
        "tipoObra":       o[9]  if len(o) > 9  else None,
        "fieldObra":      o[10] if len(o) > 10 else None,
        "unidadeObra":    o[11] if len(o) > 11 else None,
        "emailContato":   o[12] if len(o) > 12 else None,
        "celular1":       o[13] if len(o) > 13 else None,
        "celular2":       o[14] if len(o) > 14 else None,
    }


# ─── POST /obra ───────────────────────────────────────────────────────────────
@obra_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def cadastrar():
    body            = request.get_json()
    dados_obra      = body["obra"]
    produtos_usados = body["produtosUsados"]

    sucesso, mensagem = controller.cadastrar(dados_obra, produtos_usados)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 201


# ─── GET /obra ────────────────────────────────────────────────────────────────
@obra_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    obras = controller.listar()
    return jsonify({"status": True, "obras": [_serializar(o) for o in obras]}), 200


# ─── GET /obra/<idObra> ───────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_por_id(idObra: int):
    obra = controller.buscar_por_id(idObra)

    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    return jsonify({"status": True, "obra": _serializar(obra)}), 200


# ─── GET /obra/cliente/<idCliente> ────────────────────────────────────────────
@obra_bp.route("/cliente/<int:idCliente>", methods=["GET"])
@jwt.validate_token
def listar_por_cliente(idCliente: int):
    sucesso, mensagem, obras = controller.listar_por_cliente(idCliente)

    if not sucesso:
        raise ErrorResponse(404, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem, "obras": [_serializar(o) for o in obras]}), 200


# ─── GET /obra/<idObra>/produtos ──────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/produtos", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_produtos_da_obra(idObra: int):
    obra = controller.buscar_por_id(idObra)
    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    produtos = controller.buscar_produtos_da_obra(idObra)
    return jsonify({"status": True, "produtos": produtos}), 200


# ─── PUT /obra/<idObra> ───────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_update_body
def atualizar(idObra: int):
    body          = request.get_json()
    dados_obra    = body["obra"]
    produtos_novos = body.get("produtosNovos") or []

    sucesso, mensagem = controller.atualizar(idObra, dados_obra, produtos_novos)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── PATCH /obra/<idObra>/produto/<idProduto> ────────────────────────────────
# Atualiza a quantidade de um produto vinculado a uma obra
@obra_bp.route("/<int:idObra>/produto/<int:idProduto>", methods=["PATCH"])
@jwt.validate_token
@middleware.validate_id_param
def atualizar_produto_obra(idObra: int, idProduto: int):
    body      = request.get_json() or {}
    nova_qtd  = body.get("quantidade")
    if nova_qtd is None or int(nova_qtd) < 1:
        raise ErrorResponse(400, "Quantidade inválida.", {"message": "Informe uma quantidade >= 1."})
    sucesso, mensagem = controller.atualizar_produto_obra(idObra, idProduto, int(nova_qtd))
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    return jsonify({"status": True, "msg": mensagem}), 200


# ─── PATCH /obra/<idObra>/status ─────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/status", methods=["PATCH"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_status_body
def atualizar_status(idObra: int):
    body        = request.get_json()
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
    sucesso, mensagem = controller.deletar(idObra)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 200
