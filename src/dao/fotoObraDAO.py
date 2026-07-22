from src.dao.conexao import Conexao


class FotoObraDAO:

    def inserir(self, idObra: int, nomeArquivo: str, nomeOriginal: str):
        sql = """
            INSERT INTO obra_fotos (idObra, nomeArquivo, nomeOriginal)
            VALUES (%s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idObra, nomeArquivo, nomeOriginal))
            conexao.commit()
            return cursor.lastrowid
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir foto da obra: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_obra(self, idObra: int) -> list:
        sql = """
            SELECT idFoto, idObra, nomeArquivo, nomeOriginal, dataUpload
            FROM obra_fotos WHERE idObra = %s ORDER BY dataUpload
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idObra,))
            return [
                {
                    "idFoto":       r[0],
                    "idObra":       r[1],
                    "nomeArquivo":  r[2],
                    "nomeOriginal": r[3],
                    "dataUpload":   r[4].strftime("%d/%m/%Y %H:%M") if r[4] else "",
                    "url":          f"/uploads/{r[2]}",
                }
                for r in cursor.fetchall()
            ]
        except Exception as e:
            print(f"Erro ao buscar fotos da obra: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def _buscar_nome_arquivo(self, idFoto: int):
        sql = "SELECT nomeArquivo FROM obra_fotos WHERE idFoto = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idFoto,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"Erro ao buscar nome de arquivo: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def deletar(self, idFoto: int):
        nome = self._buscar_nome_arquivo(idFoto)
        if not nome:
            return None
        sql = "DELETE FROM obra_fotos WHERE idFoto = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idFoto,))
            conexao.commit()
            return nome
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar foto da obra: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)
