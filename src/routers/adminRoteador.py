from flask import Blueprint, request, jsonify, g
from src.controller.adminController import AdminController
from src.middleware.adminMiddleware  import AdminMiddleware
from src.middleware.jwtMiddleware    import JwtMiddleware
from src.error_response              import ErrorResponse

admin_bp   = Blueprint("admin", __name__, url_prefix="/admin")
controller = AdminController()
middleware = AdminMiddleware()
jwt        = JwtMiddleware()


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
    sucesso, mensagem = controller.criar(
        admin.get("email"),
        admin.get("senha"),
        admin.get("nomeLogin"),
    )
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    return jsonify({"status": True, "msg": mensagem}), 201


# ─── PUT /admin/<idLogin> ─────────────────────────────────────────────────────
@admin_bp.route("/<int:idLogin>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_update_body
def atualizar(idLogin: int):
    logged_id = g.get("admin_id")
    # Bloqueio de edição cruzada: admin só pode editar o próprio perfil
    if logged_id and int(logged_id) != idLogin:
        raise ErrorResponse(403, "Você só pode editar seu próprio perfil.", {"message": "Edição cruzada não permitida."})

    admin = request.get_json()["admin"]
    sucesso, mensagem = controller.atualizar(
        idLogin,
        admin.get("email"),
        admin.get("nomeLogin"),
        admin.get("novaSenha")   or None,
        admin.get("senhaAtual")  or None,
    )
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /admin/<idLogin> ──────────────────────────────────────────────────
@admin_bp.route("/<int:idLogin>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def deletar(idLogin: int):
    logged_id = g.get("admin_id")
    # Admin não pode se auto-deletar
    if logged_id and int(logged_id) == idLogin:
        raise ErrorResponse(403, "Você não pode excluir sua própria conta.", {"message": "Auto-exclusão não permitida."})
    sucesso, mensagem = controller.deletar(idLogin)
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    return jsonify({"status": True, "msg": mensagem}), 200
