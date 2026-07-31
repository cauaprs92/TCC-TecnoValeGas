from flask import Blueprint, request, jsonify, g
from src.controller.adminController     import AdminController
from src.controller.historicoController import HistoricoController
from src.middleware.adminMiddleware     import AdminMiddleware
from src.middleware.jwtMiddleware       import JwtMiddleware, CARGO_ADMINISTRACAO
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
@jwt.require_cargo(CARGO_ADMINISTRACAO)
def listar():
    admins = controller.listar()
    return jsonify({"status": True, "admins": admins}), 200


# ─── POST /admin ──────────────────────────────────────────────────────────────
@admin_bp.route("", methods=["POST"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO)
@middleware.validate_body
def criar():
    admin = request.get_json()["admin"]
    nome  = admin.get("nomeLogin")
    cargo = admin.get("cargo")

    sucesso, mensagem = controller.criar(
        admin.get("email"),
        admin.get("senha"),
        nome,
        cargo,
    )
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Cadastrou", "Usuário",
        f"Cadastrou o usuário '{nome}' com o cargo {cargo}",
    )

    return jsonify({"status": True, "msg": mensagem}), 201


# ─── PUT /admin/<idLogin> ─────────────────────────────────────────────────────
@admin_bp.route("/<int:idLogin>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_update_body
def atualizar(idLogin: int):
    logged_id   = g.get("admin_id")
    proprio     = bool(logged_id) and int(logged_id) == idLogin
    e_admin     = g.get("cargo") == AdminController.CARGO_ADMIN

    # Administração gerencia qualquer usuário; os demais cargos só o próprio perfil.
    if not proprio and not e_admin:
        raise ErrorResponse(403, "Você só pode editar seu próprio perfil.", {"message": "Edição cruzada não permitida."})

    admin = request.get_json()["admin"]
    nome  = admin.get("nomeLogin")
    cargo = admin.get("cargo")

    # Só Administração troca cargo. Quem edita o próprio perfil sem esse cargo
    # mantém o que já está gravado, mesmo que mande outra coisa no corpo.
    if not e_admin:
        atual = controller.dao.buscar_por_id(idLogin)
        cargo = atual[3] if atual else cargo

    # A senha atual confirma a identidade de quem mexe no próprio perfil.
    # Administração editando outra pessoa não tem como saber a senha dela.
    senha_atual = (admin.get("senhaAtual") or None) if proprio else None

    sucesso, mensagem = controller.atualizar(
        idLogin,
        admin.get("email"),
        nome,
        cargo,
        admin.get("novaSenha") or None,
        senha_atual,
    )
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Editou", "Usuário",
        f"Editou o usuário '{nome}' (ID: {idLogin}) — cargo {cargo}",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /admin/<idLogin> ──────────────────────────────────────────────────
@admin_bp.route("/<int:idLogin>", methods=["DELETE"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO)
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
        "Deletou", "Usuário",
        f"Deletou o usuário '{nome}' (ID: {idLogin})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200
