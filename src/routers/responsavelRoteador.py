from flask import Blueprint, request, jsonify
from src.controller.responsavelController import ResponsavelController
from src.middleware.jwtMiddleware         import JwtMiddleware
from src.error_response                   import ErrorResponse

responsavel_bp = Blueprint("responsavel", __name__, url_prefix="/responsavel")
controller     = ResponsavelController()
jwt            = JwtMiddleware()


@responsavel_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


# ─── GET /responsavel ──────────────────────────────────────────────────────────
@responsavel_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    return jsonify({"status": True, "responsaveis": controller.listar()}), 200


# ─── POST /responsavel ─────────────────────────────────────────────────────────
@responsavel_bp.route("", methods=["POST"])
@jwt.validate_token
def criar():
    body = request.get_json() or {}
    nome = (body.get("nomeResponsavel") or "").strip()
    ok, msg = controller.criar(nome)
    if not ok:
        raise ErrorResponse(400, msg, {"message": msg})
    return jsonify({"status": True, "msg": msg}), 201


# ─── PUT /responsavel/<id> ─────────────────────────────────────────────────────
@responsavel_bp.route("/<int:idResponsavel>", methods=["PUT"])
@jwt.validate_token
def atualizar(idResponsavel: int):
    body = request.get_json() or {}
    nome = (body.get("nomeResponsavel") or "").strip()
    ok, msg = controller.atualizar(idResponsavel, nome)
    if not ok:
        raise ErrorResponse(400, msg, {"message": msg})
    return jsonify({"status": True, "msg": msg}), 200


# ─── DELETE /responsavel/<id> ──────────────────────────────────────────────────
@responsavel_bp.route("/<int:idResponsavel>", methods=["DELETE"])
@jwt.validate_token
def deletar(idResponsavel: int):
    ok, msg = controller.deletar(idResponsavel)
    if not ok:
        raise ErrorResponse(400, msg, {"message": msg})
    return jsonify({"status": True, "msg": msg}), 200
