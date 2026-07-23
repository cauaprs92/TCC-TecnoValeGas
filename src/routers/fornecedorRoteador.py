from flask import Blueprint, jsonify
from src.controller.fornecedorController import FornecedorController
from src.middleware.jwtMiddleware import JwtMiddleware
from src.error_response import ErrorResponse

fornecedor_bp = Blueprint("fornecedor", __name__, url_prefix="/fornecedor")
controller    = FornecedorController()
jwt           = JwtMiddleware()


@fornecedor_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


# ─── GET /fornecedor ───────────────────────────────────────────────────────────
@fornecedor_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    return jsonify({"status": True, "fornecedores": controller.listar()}), 200
