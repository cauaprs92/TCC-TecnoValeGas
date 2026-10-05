from flask import Blueprint, jsonify
from src.controller.fornecedorController import FornecedorController
from src.middleware.jwtMiddleware import JwtMiddleware, CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO

fornecedor_bp = Blueprint("fornecedor", __name__, url_prefix="/fornecedor")
controller    = FornecedorController()
jwt           = JwtMiddleware()


# ─── GET /fornecedor ───────────────────────────────────────────────────────────
@fornecedor_bp.route("", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def listar():
    return jsonify({"status": True, "fornecedores": controller.listar()}), 200
