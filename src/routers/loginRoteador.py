from flask import Blueprint, request, jsonify
from src.controller.loginController  import LoginController
from src.middleware.loginMiddleware   import LoginMiddleware
from src.middleware.jwtMiddleware     import MeuTokenJWT
from src.error_response               import ErrorResponse

login_bp   = Blueprint("login", __name__, url_prefix="/login")
controller = LoginController()
middleware = LoginMiddleware()


@login_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


# ─── POST /login ──────────────────────────────────────────────────────────────
@login_bp.route("", methods=["POST"])
@middleware.validate_body
def autenticar():
    """Autentica o usuário e retorna um token JWT."""
    body  = request.get_json()
    email = body.get("email").strip()
    senha = body.get("senha").strip()

    sucesso, resultado = controller.autenticar(email, senha)

    if not sucesso:
        raise ErrorResponse(401, resultado, {"message": resultado})

    # resultado é (idLogin, nomeLogin) quando sucesso=True
    id_login, nome_login = resultado
    jwt_instance = MeuTokenJWT()
    token = jwt_instance.gerar_token({
        "nomeLogin": nome_login,
        "email":     email,
        "idAdmin":   id_login,
    })

    return jsonify({
        "status":    True,
        "msg":       "Login realizado com sucesso!",
        "nomeLogin": nome_login,
        "idAdmin":   id_login,
        "token":     token,
    }), 200