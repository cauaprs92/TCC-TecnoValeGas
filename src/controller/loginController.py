import bcrypt
from src.dao.adminDAO import AdminDAO


class LoginController:

    def __init__(self):
        self.dao = AdminDAO()

    def autenticar(self, email: str, senha: str) -> tuple:
        if not email.strip() or not senha.strip():
            return False, "Email e senha sao obrigatorios."

        resultado = self.dao.buscar_credenciais(email.strip())
        if not resultado:
            return False, "Email ou senha incorretos."

        id_login, nome_login, hash_salvo, cargo_login = resultado
        hash_bytes = hash_salvo.encode("utf-8") if isinstance(hash_salvo, str) else hash_salvo
        if not bcrypt.checkpw(senha.encode("utf-8"), hash_bytes):
            return False, "Email ou senha incorretos."

        return True, (id_login, nome_login, cargo_login)
