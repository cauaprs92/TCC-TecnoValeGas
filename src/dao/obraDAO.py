from src.dao.conexao import Conexao

class ObraDAO:

    def inserir(self, obra: dict) -> bool:
        sql = """
            INSERT INTO obras
              (codCliente, descObra, dataInicio, dataFim,
               statusObra, respObra, obsObra, orientacaoObra)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (
                obra["codCliente"],
                obra["descObra"],
                obra["dataInicio"],
                obra.get("dataFim"),
                obra.get("statusObra"),
                obra.get("respObra"),
                obra.get("obsObra"),
                obra.get("orientacaoObra")
            ))
            conexao.commit()
            print("Obra inserida com sucesso!")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_todas(self) -> list:
        sql = """
            SELECT o.idObra, o.codCliente, o.descObra, o.dataInicio, o.dataFim,
                   o.statusObra, o.respObra, o.obsObra, o.orientacaoObra
            FROM obras o
            ORDER BY o.dataInicio DESC
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar obras: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_id(self, id_obra: int):
        sql = """
            SELECT idObra, codCliente, descObra, dataInicio, dataFim,
                   statusObra, respObra, obsObra, orientacaoObra
            FROM obras WHERE idObra = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_obra,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar obra por ID: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def atualizar(self, id_obra: int, obra: dict) -> bool:
        sql = """
            UPDATE obras SET
              codCliente = %s, descObra = %s, dataInicio = %s, dataFim = %s,
              statusObra = %s, respObra = %s
            WHERE idObra = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (
                obra["codCliente"],
                obra["descObra"],
                obra["dataInicio"],
                obra.get("dataFim"),
                obra["statusObra"],
                obra.get("respObra", ""),
                id_obra
            ))
            conexao.commit()
            print(f"Obra {id_obra} atualizada com sucesso!")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def atualizar_status(self, id_obra: int, novo_status: str) -> bool:
        sql = "UPDATE obras SET statusObra = %s WHERE idObra = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (novo_status, id_obra))
            conexao.commit()
            print(f"Status da obra {id_obra} atualizado para '{novo_status}'")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar status da obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def deletar(self, id_obra: int) -> bool:
        sql = "DELETE FROM obras WHERE idObra = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_obra,))
            conexao.commit()
            print("Obra deletada com sucesso!")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)
