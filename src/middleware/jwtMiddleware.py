import os
import jwt
import time
import secrets
from flask import request, jsonify, g
from functools import wraps
from src.dao.adminDAO import AdminDAO

_RAIZ_PROJETO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ARQUIVO_CHAVE = os.path.join(_RAIZ_PROJETO, ".jwt_secret")


def _carregar_chave() -> str:
    """Chave de assinatura dos tokens. Vem de JWT_SECRET ou, na falta dela, de
    um arquivo gerado no primeiro uso (fora do git) — nunca do código."""
    chave = os.environ.get("JWT_SECRET")
    if chave:
        return chave
    if os.path.exists(_ARQUIVO_CHAVE):
        with open(_ARQUIVO_CHAVE, encoding="utf-8") as f:
            return f.read().strip()
    chave = secrets.token_hex(32)
    with open(_ARQUIVO_CHAVE, "w", encoding="utf-8") as f:
        f.write(chave)
    return chave


class MeuTokenJWT:
    """Classe para gerar e validar tokens JWT"""

    _key = _carregar_chave()

    def __init__(self):
        self._alg = "HS256"
        self._iss = "http://localhost"
        self._aud = "http://localhost"
        self._sub = "acesso_sistema"
        self._duracao_token = 3600 * 12  # 12 horas
        self._payload = None

    @property
    def payload(self):
        return self._payload

    def gerar_token(self, claims: dict) -> str:
        payload = {
            "iss": self._iss,
            "aud": self._aud,
            "sub": self._sub,
            "iat": int(time.time()),
            "exp": int(time.time()) + self._duracao_token,
            "nbf": int(time.time()),
            "jti": secrets.token_hex(16),
            **claims
        }
        token = jwt.encode(payload, self._key, algorithm=self._alg)
        return token

    def validar_token(self, token: str) -> bool:
        if not token:
            return False

        token = token.replace("Bearer ", "").strip()

        try:
            decoded = jwt.decode(token, self._key, algorithms=[self._alg], audience=self._aud, issuer=self._iss)
            self._payload = decoded
            return True
        except jwt.InvalidTokenError:
            return False


CARGO_ADMINISTRACAO = "Administracao"
CARGO_ALMOXARIFADO  = "Almoxarifado"
CARGO_OBRA          = "Obra"


class JwtMiddleware:
    """Middleware Flask para validação de tokens JWT"""

    def __init__(self):
        self.daoAdmin = AdminDAO()

    def validate_token(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            jwt_instance = MeuTokenJWT()
            if not jwt_instance.validar_token(request.headers.get("Authorization")):
                return jsonify({"status": False, "msg": "token inválido"}), 401

            payload = jwt_instance.payload or {}
            # Cargo e nome vêm do banco, não do token: um usuário rebaixado ou
            # excluído perde o acesso na hora, sem esperar o token expirar.
            usuario = self.daoAdmin.buscar_por_id(payload.get("idAdmin"))
            if not usuario:
                return jsonify({"status": False, "msg": "usuário não encontrado"}), 401

            g.jwt_payload = {**payload, "nomeLogin": usuario[2]}
            g.admin_id    = usuario[0]
            g.cargo       = usuario[3]
            return f(*args, **kwargs)

        return decorated_function

    def require_cargo(self, *cargos_permitidos):
        """Restringe a rota aos cargos informados. Deve vir depois de
        @jwt.validate_token, que é quem preenche g.cargo."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cargo = g.get("cargo")
                if cargo not in cargos_permitidos:
                    return jsonify({
                        "status": False,
                        "msg":    "Você não tem permissão para acessar este recurso.",
                        "error":  {"message": f"Cargo '{cargo}' sem acesso a esta rota."},
                    }), 403
                return f(*args, **kwargs)
            return decorated_function
        return decorator
