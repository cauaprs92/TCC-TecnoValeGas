from flask import Blueprint, jsonify, request, g
from src.controller.fornecedorController import FornecedorController
from src.controller.historicoController  import HistoricoController
from src.middleware.jwtMiddleware import JwtMiddleware, CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO
from src.error_response import ErrorResponse

fornecedor_bp  = Blueprint("fornecedor", __name__, url_prefix="/fornecedor")
controller     = FornecedorController()
historico_ctrl = HistoricoController()
jwt            = JwtMiddleware()


# ─── GET /fornecedor ───────────────────────────────────────────────────────────
@fornecedor_bp.route("", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def listar():
    return jsonify({"status": True, "fornecedores": controller.listar()}), 200


# ─── PATCH /fornecedor/<idFornecedor>/prazo ───────────────────────────────────
@fornecedor_bp.route("/<int:idFornecedor>/prazo", methods=["PATCH"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def atualizar_prazo(idFornecedor: int):
    prazo = (request.get_json(silent=True) or {}).get("prazoEntregaDias")
    sucesso, mensagem, nome = controller.atualizar_prazo(idFornecedor, prazo)
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Editou", "Fornecedor",
        f"Alterou o prazo de entrega de '{nome}' para {int(prazo)} dias",
    )
    return jsonify({"status": True, "msg": mensagem}), 200
