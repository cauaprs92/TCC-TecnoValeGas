from flask import Blueprint, request, jsonify, g
from src.controller.adminController     import AdminController
from src.controller.historicoController import HistoricoController
from src.middleware.adminMiddleware     import AdminMiddleware
from src.middleware.jwtMiddleware       import JwtMiddleware
from src.error_response                 import ErrorResponse

admin_bp       = Blueprint("admin", __name__, url_prefix="/admin")
controller     = AdminController()
historico_ctrl = HistoricoController()
middleware     = AdminMiddleware()
jwt            = JwtMiddleware()


@admin_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


# ─── GET /admin ───────────────────────────────────────────────────────────────
@admin_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    admins = controller.listar()
    return jsonify({"status": True, "admins": admins}), 200


# ─── POST /admin ──────────────────────────────────────────────────────────────
@admin_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def criar():
    admin = request.get_json()["admin"]
    nome  = admin.get("nomeLogin")

    sucesso, mensagem = controller.criar(
        admin.get("email"),
        admin.get("senha"),
        nome,
    )
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Cadastrou", "Administrador",
        f"Cadastrou o administrador '{nome}'",
    )

    return jsonify({"status": True, "msg": mensagem}), 201


# ─── PUT /admin/<idLogin> ─────────────────────────────────────────────────────
@admin_bp.route("/<int:idLogin>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_update_body
def atualizar(idLogin: int):
    logged_id = g.get("admin_id")
    if logged_id and int(logged_id) != idLogin:
        raise ErrorResponse(403, "Você só pode editar seu próprio perfil.", {"message": "Edição cruzada não permitida."})

    admin = request.get_json()["admin"]
    nome  = admin.get("nomeLogin")

    sucesso, mensagem = controller.atualizar(
        idLogin,
        admin.get("email"),
        nome,
        admin.get("novaSenha")  or None,
        admin.get("senhaAtual") or None,
    )
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Editou", "Administrador",
        f"Editou o administrador '{nome}' (ID: {idLogin})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /admin/<idLogin> ──────────────────────────────────────────────────
@admin_bp.route("/<int:idLogin>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def deletar(idLogin: int):
    logged_id = g.get("admin_id")
    if logged_id and int(logged_id) == idLogin:
        raise ErrorResponse(403, "Você não pode excluir sua própria conta.", {"message": "Auto-exclusão não permitida."})

    admins = controller.listar()
    alvo   = next((a for a in admins if a["idLogin"] == idLogin), None)
    nome   = alvo["nomeLogin"] if alvo else str(idLogin)

    sucesso, mensagem = controller.deletar(idLogin)
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Deletou", "Administrador",
        f"Deletou o administrador '{nome}' (ID: {idLogin})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200
