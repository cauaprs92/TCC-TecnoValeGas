import bcrypt
from src.dao.conexao import Conexao

class LoginController:

    def autenticar(self, email: str, senha: str) -> tuple:
        if not email.strip() or not senha.strip():
            return False, "Email e senha sao obrigatorios."

        conexao = Conexao.obter_conexao()
        if not conexao:
            return False, "Erro ao conectar ao banco de dados."

        cursor = conexao.cursor()
        try:
            cursor.execute(
                "SELECT idLogin, nomeLogin, senha FROM login WHERE email = %s",
                (email.strip(),)
            )
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Email ou senha incorretos."

            id_login, nome_login, hash_salvo = resultado
            senha_bytes = senha.strip().encode("utf-8")
            hash_bytes  = hash_salvo.encode("utf-8") if isinstance(hash_salvo, str) else hash_salvo

            if not bcrypt.checkpw(senha_bytes, hash_bytes):
                return False, "Email ou senha incorretos."

            return True, (id_login, nome_login)
        except Exception as e:
            return False, f"Erro ao autenticar: {e}"
        finally:
            Conexao.fechar_conexao(conexao, cursor)