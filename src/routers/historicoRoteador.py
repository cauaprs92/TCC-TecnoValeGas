from flask import Blueprint, jsonify
from src.controller.historicoController import HistoricoController
from src.middleware.jwtMiddleware import JwtMiddleware, CARGO_ADMINISTRACAO

historico_bp = Blueprint("historico", __name__, url_prefix="/historico")
controller   = HistoricoController()
jwt          = JwtMiddleware()


def _serializar(h) -> dict:
    return {
        "idHistorico": h._idHistorico,
        "idAdmin":     h._idAdmin,
        "nomeAdmin":   h._nomeAdmin,
        "acao":        h._acao,
        "entidade":    h._entidade,
        "descricao":   h._descricao,
        "dataHora":    h._dataHora.strftime("%d/%m/%Y %H:%M:%S") if h._dataHora else None,
    }


# ─── GET /historico ───────────────────────────────────────────────────────────
@historico_bp.route("", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO)
def listar():
    registros = controller.listar()
    return jsonify({"status": True, "historico": [_serializar(h) for h in registros]}), 200
