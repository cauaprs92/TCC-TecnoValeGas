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


# ─── GET /relatorio/lucro-servicos ───────────────────────────────────────────
# Margem de cada serviço com o custo atual da receita (só material)
@relatorio_bp.route("/lucro-servicos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO)
def lucro_servicos():
    return jsonify({"status": True, "dados": dao.lucro_servicos()}), 200


# ─── GET /relatorio/lucro-produtos ───────────────────────────────────────────
# Preço de venda atual e lucro realizado nas vendas avulsas em obras concluídas
@relatorio_bp.route("/lucro-produtos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO)
def lucro_produtos():
    return jsonify({"status": True, "dados": dao.lucro_produtos()}), 200
