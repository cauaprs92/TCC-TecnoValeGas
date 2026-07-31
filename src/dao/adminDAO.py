from src.dao.conexao import Conexao


class AdminDAO:

    def listar(self) -> list:
        sql = "SELECT idLogin, email, nomeLogin, cargoLogin FROM login ORDER BY idLogin"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar admins: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_id(self, id_login: int):
        sql = "SELECT idLogin, email, nomeLogin, cargoLogin FROM login WHERE idLogin = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_login,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar admin por ID: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_email(self, email: str, excluir_id: int = None):
        sql = "SELECT idLogin FROM login WHERE email = %s"
        params = [email]
        if excluir_id:
            sql += " AND idLogin != %s"
            params.append(excluir_id)
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar admin por email: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def criar(self, email: str, hash_senha: str, nome: str, cargo: str) -> bool:
        sql = "INSERT INTO login (email, senha, nomeLogin, cargoLogin) VALUES (%s, %s, %s, %s)"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (email, hash_senha, nome, cargo))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao criar admin: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def atualizar(self, id_login: int, email: str, nome: str, cargo: str,
                  hash_senha: str = None) -> bool:
        if hash_senha:
            sql = "UPDATE login SET email = %s, nomeLogin = %s, cargoLogin = %s, senha = %s WHERE idLogin = %s"
            params = (email, nome, cargo, hash_senha, id_login)
        else:
            sql = "UPDATE login SET email = %s, nomeLogin = %s, cargoLogin = %s WHERE idLogin = %s"
            params = (email, nome, cargo, id_login)

        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, params)
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar admin: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def deletar(self, id_login: int) -> bool:
        sql = "DELETE FROM login WHERE idLogin = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_login,))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar admin: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_hash_senha(self, id_login: int):
        sql = "SELECT senha FROM login WHERE idLogin = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_login,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"Erro ao buscar hash de senha: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def contar(self) -> int:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return 0
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM login")
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except Exception as e:
            print(f"Erro ao contar admins: {e}")
            return 0
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def contar_por_cargo(self, cargo: str) -> int:
        """Usado para impedir que o último usuário de Administração seja excluído
        ou rebaixado, o que deixaria o sistema sem ninguém capaz de gerenciá-lo."""
        conexao = Conexao.obter_conexao()
        if not conexao:
            return 0
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM login WHERE cargoLogin = %s", (cargo,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except Exception as e:
            print(f"Erro ao contar usuários por cargo: {e}")
            return 0
        finally:
            Conexao.fechar_conexao(conexao, cursor)
