from flask import Blueprint, jsonify
from src.middleware.jwtMiddleware import JwtMiddleware, CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO
from src.dao.relatorioDAO         import RelatorioDAO

relatorio_bp = Blueprint("relatorio", __name__, url_prefix="/relatorio")
jwt          = JwtMiddleware()
dao          = RelatorioDAO()


# ─── GET /relatorio/produtos-consumidos ───────────────────────────────────────
# Retorna total consumido por produto (para exportação)
@relatorio_bp.route("/produtos-consumidos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def produtos_consumidos():
    return jsonify({"status": True, "dados": dao.produtos_consumidos()}), 200


# ─── GET /relatorio/grafico-produtos ─────────────────────────────────────────
@relatorio_bp.route("/grafico-produtos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def grafico_produtos():
    return jsonify({"status": True, "dados": dao.consumo_por_produto_e_obra()}), 200
