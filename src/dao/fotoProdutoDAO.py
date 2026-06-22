from src.dao.conexao import Conexao


class FotoProdutoDAO:

    def inserir(self, idProduto: int, tipoFoto: str, nomeArquivo: str, nomeOriginal: str):
        sql = """
            INSERT INTO produto_fotos (idProduto, tipoFoto, nomeArquivo, nomeOriginal)
            VALUES (%s, %s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idProduto, tipoFoto, nomeArquivo, nomeOriginal))
            conexao.commit()
            return cursor.lastrowid
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir foto: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_produto(self, idProduto: int) -> list:
        sql = """
            SELECT idFoto, idProduto, tipoFoto, nomeArquivo, nomeOriginal, dataUpload
            FROM produto_fotos WHERE idProduto = %s ORDER BY dataUpload
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idProduto,))
            return [
                {
                    "idFoto":       r[0],
                    "idProduto":    r[1],
                    "tipoFoto":     r[2],
                    "nomeArquivo":  r[3],
                    "nomeOriginal": r[4],
                    "dataUpload":   r[5].strftime("%d/%m/%Y %H:%M") if r[5] else "",
                    "url":          f"/uploads/{r[3]}",
                }
                for r in cursor.fetchall()
            ]
        except Exception as e:
            print(f"Erro ao buscar fotos: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def _buscar_nome_arquivo(self, idFoto: int):
        sql = "SELECT nomeArquivo FROM produto_fotos WHERE idFoto = %s"
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
        sql = "DELETE FROM produto_fotos WHERE idFoto = %s"
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
            print(f"Erro ao deletar foto: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)
