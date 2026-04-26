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
                "SELECT nomeLogin FROM login WHERE email = %s AND senha = %s",
                (email.strip(), senha.strip())
            )
            resultado = cursor.fetchone()
            if resultado:
                return True, resultado[0]
            return False, "Email ou senha incorretos."
        except Exception as e:
            return False, f"Erro ao autenticar: {e}"
        finally:
            Conexao.fechar_conexao(conexao, cursor)