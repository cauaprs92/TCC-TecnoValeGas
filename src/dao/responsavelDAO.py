from src.dao.conexao import Conexao


class ResponsavelDAO:

    def listar(self) -> list:
        sql = "SELECT idResponsavel, nomeResponsavel FROM responsavel ORDER BY nomeResponsavel"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar responsáveis: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_id(self, id_responsavel: int):
        sql = "SELECT idResponsavel, nomeResponsavel FROM responsavel WHERE idResponsavel = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_responsavel,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar responsável por ID: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_nome(self, nome: str, excluir_id: int = None):
        sql = "SELECT idResponsavel FROM responsavel WHERE LOWER(nomeResponsavel) = LOWER(%s)"
        params = [nome]
        if excluir_id:
            sql += " AND idResponsavel != %s"
            params.append(excluir_id)
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar responsável por nome: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def criar(self, nome: str) -> bool:
        sql = "INSERT INTO responsavel (nomeResponsavel) VALUES (%s)"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (nome,))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao criar responsável: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def atualizar(self, id_responsavel: int, nome: str) -> bool:
        sql = "UPDATE responsavel SET nomeResponsavel = %s WHERE idResponsavel = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (nome, id_responsavel))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar responsável: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def deletar(self, id_responsavel: int) -> bool:
        sql = "DELETE FROM responsavel WHERE idResponsavel = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_responsavel,))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar responsável: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)
