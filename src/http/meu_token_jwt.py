# -*- coding: utf-8 -*-
import jwt
import secrets
import time


"""
Classe responsável por gerar e validar tokens JWT (JSON Web Token) para autenticação.

Implementa:
- Geração de token com claims personalizados;
- Validação de token, incluindo verificação de expiração;
- Configuração de cabeçalhos e payload do JWT.

Os atributos principais são privados e podem ser acessados/modificados via getters/setters.
"""
class MeuTokenJWT:
    def __init__(self):
        """
        Construtor da classe MeuTokenJWT
        Inicializa valores padrão como chave secreta, algoritmo, tipo e duração do token.
        """
        self.__key = "x9S4q0v+V0IjvHkG20uAxaHx1ijj+q1HWjHKv+ohxp/oK+77qyXkVj/l4QYHHTF3"
        self.__alg = "HS256"
        self.__type = "JWT"
        self.__iss = "http://localhost"
        self.__aud = "http://localhost"
        self.__sub = "acesso_sistema"
        self.__duracaoToken = 3600 * 24 * 60  # 60 dias em segundos
        self.__payload = None

    def gerarToken(self, claims: dict) -> str:
        """
        Gera um token JWT assinado com os claims fornecidos.

        :param claims: dict com informações do usuário {email, role, name, idFuncionario}
        :return: string (JWT)
        """
        headers = {
            "alg": self.__alg,
            "typ": self.__type,
        }

        agora = int(time.time())
        payload = {
            "iss": self.__iss,
            "aud": self.__aud,
            "sub": self.__sub,
            "iat": agora,
            "exp": agora + self.__duracaoToken,
            "nbf": agora,
            "jti": secrets.token_hex(16),

            "email": claims.get("email"),
            "role": claims.get("role"),
            "name": claims.get("name"),
            "idFuncionario": claims.get("idFuncionario"),
        }

        return jwt.encode(payload, self.__key, algorithm=self.__alg, headers=headers)

    def validarToken(self, stringToken: str) -> bool:
        """
        Valida um token JWT.

        :param stringToken: Token JWT a ser validado (pode incluir prefixo "Bearer ")
        :return: True se válido, False caso contrário
        """
        if not stringToken or stringToken.strip() == "":
            print("❌ Token não fornecido ou em branco")
            return False

        token = stringToken.replace("Bearer ", "").strip()

        try:
            decoded = jwt.decode(
                token,
                self.__key,
                algorithms=[self.__alg],
                audience=self.__aud,
                issuer=self.__iss
            )
            self.__payload = decoded
            return True
        except jwt.ExpiredSignatureError:
            print("❌ Token expirado")
            return False
        except jwt.InvalidTokenError as err:
            print("❌ Token inválido:", err)
            return False

    # Getters e Setters
    @property
    def key(self): return self.__key
    @key.setter
    def key(self, value): self.__key = value

    @property
    def alg(self): return self.__alg
    @alg.setter
    def alg(self, value): self.__alg = value

    @property
    def type(self): return self.__type
    @type.setter
    def type(self, value): self.__type = value

    @property
    def iss(self): return self.__iss
    @iss.setter
    def iss(self, value): self.__iss = value

    @property
    def aud(self): return self.__aud
    @aud.setter
    def aud(self, value): self.__aud = value

    @property
    def sub(self): return self.__sub
    @sub.setter
    def sub(self, value): self.__sub = value

    @property
    def duracaoToken(self): return self.__duracaoToken
    @duracaoToken.setter
    def duracaoToken(self, value): self.__duracaoToken = value

    @property
    def payload(self): return self.__payload
    @payload.setter
    def payload(self, value): self.__payload = value