import jwt
import time
import secrets
from flask import request, jsonify, g
from functools import wraps


class MeuTokenJWT:
    """Classe para gerar e validar tokens JWT"""
    
    def __init__(self):
        self._key = "x9S4q0v+V0IjvHkG20uAxaHx1ijj+q1HWjHKv+ohxp/oK+77qyXkVj/l4QYHHTF3"
        self._alg = "HS256"
        self._iss = "http://localhost"
        self._aud = "http://localhost"
        self._sub = "acesso_sistema"
        self._duracao_token = 3600 * 24 * 60  # 60 dias em segundos
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
            print("Token não fornecido")
            return False

        token = token.replace("Bearer ", "").strip()

        try:
            decoded = jwt.decode(token, self._key, algorithms=[self._alg], audience=self._aud, issuer=self._iss)
            self._payload = decoded
            return True
        except jwt.ExpiredSignatureError:
            print("Token expirado")
        except jwt.InvalidTokenError:
            print("Token inválido")
        return False


CARGO_ADMINISTRACAO = "Administracao"
CARGO_ALMOXARIFADO  = "Almoxarifado"
CARGO_OBRA          = "Obra"


class JwtMiddleware:
    """Middleware Flask para validação de tokens JWT"""

    def validate_token(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 JwtMiddleware.validate_token()")
            authorization = request.headers.get("Authorization", None)
            jwt_instance = MeuTokenJWT()

            if jwt_instance.validar_token(authorization):
                g.jwt_payload = jwt_instance.payload or {}
                g.admin_id    = g.jwt_payload.get("idAdmin")
                # Tokens emitidos antes do cargo existir não trazem o claim.
                # Como todos os usuários da época eram administradores, tratamos
                # a ausência como Administração e ninguém é deslogado à força.
                g.cargo       = g.jwt_payload.get("cargo") or CARGO_ADMINISTRACAO
                return f(*args, **kwargs)
            else:
                return jsonify({"status": False, "msg": "token inválido"}), 401

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