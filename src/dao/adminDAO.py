from src.dao.banco import consultar, consultar_um, executar

_COLS = "idLogin, email, nomeLogin, cargoLogin"


class AdminDAO:

    def listar(self) -> list:
        return consultar(f"SELECT {_COLS} FROM login ORDER BY idLogin",
                         erro="Erro ao listar usuários:")

    def buscar_por_id(self, id_login: int):
        return consultar_um(f"SELECT {_COLS} FROM login WHERE idLogin = %s", (id_login,),
                            erro="Erro ao buscar usuário por ID:")

    def buscar_por_email(self, email: str, excluir_id: int = None):
        sql, params = "SELECT idLogin FROM login WHERE email = %s", [email]
        if excluir_id:
            sql += " AND idLogin != %s"
            params.append(excluir_id)
        return consultar_um(sql, params, erro="Erro ao buscar usuário por email:")

    def buscar_credenciais(self, email: str):
        """(idLogin, nomeLogin, hash da senha, cargoLogin) para o login."""
        return consultar_um(
            "SELECT idLogin, nomeLogin, senha, cargoLogin FROM login WHERE email = %s", (email,),
            erro="Erro ao buscar credenciais:")

    def buscar_hash_senha(self, id_login: int):
        row = consultar_um("SELECT senha FROM login WHERE idLogin = %s", (id_login,),
                           erro="Erro ao buscar hash de senha:")
        return row[0] if row else None

    def criar(self, email: str, hash_senha: str, nome: str, cargo: str) -> bool:
        return executar(
            "INSERT INTO login (email, senha, nomeLogin, cargoLogin) VALUES (%s, %s, %s, %s)",
            (email, hash_senha, nome, cargo), erro="Erro ao criar usuário:")

    def atualizar(self, id_login: int, email: str, nome: str, cargo: str,
                  hash_senha: str = None) -> bool:
        if hash_senha:
            sql = "UPDATE login SET email = %s, nomeLogin = %s, cargoLogin = %s, senha = %s WHERE idLogin = %s"
            params = (email, nome, cargo, hash_senha, id_login)
        else:
            sql = "UPDATE login SET email = %s, nomeLogin = %s, cargoLogin = %s WHERE idLogin = %s"
            params = (email, nome, cargo, id_login)
        return executar(sql, params, erro="Erro ao atualizar usuário:")

    def deletar(self, id_login: int) -> bool:
        return executar("DELETE FROM login WHERE idLogin = %s", (id_login,),
                        erro="Erro ao deletar usuário:")

    def contar(self) -> int:
        row = consultar_um("SELECT COUNT(*) FROM login", erro="Erro ao contar usuários:")
        return row[0] if row else 0

    def contar_por_cargo(self, cargo: str) -> int:
        """Usado para impedir que o último usuário de Administração seja excluído
        ou rebaixado, o que deixaria o sistema sem ninguém capaz de gerenciá-lo."""
        row = consultar_um("SELECT COUNT(*) FROM login WHERE cargoLogin = %s", (cargo,),
                           erro="Erro ao contar usuários por cargo:")
        return row[0] if row else 0
