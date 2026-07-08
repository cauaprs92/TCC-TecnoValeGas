from src.dao.conexao import Conexao

_COLS_SELECT = """
    idObra, codCliente, descObra, dataInicio, dataFim,
    statusObra, respObra, obsObra, orientacaoObra,
    tipoObra, fieldObra, unidadeObra, emailContato, celular1, celular2
"""

class ObraDAO:

    def inserir(self, obra: dict) -> bool:
        sql = """
            INSERT INTO obras
              (codCliente, descObra, dataInicio, dataFim, statusObra, respObra,
               obsObra, orientacaoObra, tipoObra, fieldObra, unidadeObra,
               emailContato, celular1, celular2)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
                obra.get("orientacaoObra"),
                obra.get("tipoObra"),
                obra.get("fieldObra"),
                obra.get("unidadeObra"),
                obra.get("emailContato"),
                obra.get("celular1"),
                obra.get("celular2"),
            ))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_todas(self) -> list:
        sql = f"SELECT {_COLS_SELECT} FROM obras ORDER BY dataInicio DESC"
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
        sql = f"SELECT {_COLS_SELECT} FROM obras WHERE idObra = %s"
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
              codCliente=%s, descObra=%s, dataInicio=%s, dataFim=%s,
              statusObra=%s, respObra=%s, obsObra=%s, orientacaoObra=%s,
              tipoObra=%s, fieldObra=%s, unidadeObra=%s,
              emailContato=%s, celular1=%s, celular2=%s
            WHERE idObra=%s
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
                obra.get("obsObra"),
                obra.get("orientacaoObra"),
                obra.get("tipoObra"),
                obra.get("fieldObra"),
                obra.get("unidadeObra"),
                obra.get("emailContato"),
                obra.get("celular1"),
                obra.get("celular2"),
                id_obra,
            ))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_cliente(self, id_cliente: int) -> list:
        sql = f"SELECT {_COLS_SELECT} FROM obras WHERE codCliente=%s ORDER BY dataInicio DESC"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_cliente,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar obras do cliente {id_cliente}: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def atualizar_status(self, id_obra: int, novo_status: str) -> bool:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT statusObra FROM obras WHERE idObra=%s", (id_obra,))
            row = cursor.fetchone()
            status_atual = row[0] if row else None

            if novo_status == "Concluida":
                cursor.execute("""
                    SELECT SUM(s.precoServico) AS total
                    FROM obraServicos os
                    JOIN servicos s ON os.idServico = s.idServico
                    WHERE os.idObra = %s
                """, (id_obra,))
                total = cursor.fetchone()[0]
                valor_obra = float(total) if total is not None else 0.00

                cursor.execute(
                    "UPDATE obras SET statusObra=%s, valorObra=%s WHERE idObra=%s",
                    (novo_status, valor_obra, id_obra)
                )
            elif status_atual == "Concluida":
                cursor.execute(
                    "UPDATE obras SET statusObra=%s, valorObra=NULL WHERE idObra=%s",
                    (novo_status, id_obra)
                )
            else:
                cursor.execute(
                    "UPDATE obras SET statusObra=%s WHERE idObra=%s",
                    (novo_status, id_obra)
                )

            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar status da obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def deletar(self, id_obra: int) -> bool:
        sql = "DELETE FROM obras WHERE idObra=%s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_obra,))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)
