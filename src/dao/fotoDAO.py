from src.dao.banco import consultar, consultar_um, executar, inserir


class FotoDAO:
    """Fotos de uma entidade — obra_fotos (dono idObra) ou produto_fotos (dono
    idProduto, com tipoFoto 'produto' ou 'nota_fiscal')."""

    def __init__(self, tabela: str, dono: str, com_tipo: bool = False):
        self.tabela, self.dono, self.com_tipo = tabela, dono, com_tipo

    def inserir(self, id_dono: int, nome_arquivo: str, nome_original: str, tipo: str = None):
        colunas = [self.dono, "nomeArquivo", "nomeOriginal"] + (["tipoFoto"] if self.com_tipo else [])
        valores = [id_dono, nome_arquivo, nome_original] + ([tipo] if self.com_tipo else [])
        return inserir(
            f"INSERT INTO {self.tabela} ({', '.join(colunas)}) VALUES ({', '.join(['%s'] * len(colunas))})",
            valores, erro=f"Erro ao inserir foto em {self.tabela}:")

    def buscar(self, id_dono: int) -> list:
        tipo = ", tipoFoto" if self.com_tipo else ""
        linhas = consultar(f"""
            SELECT idFoto, nomeArquivo, nomeOriginal, dataUpload{tipo}
            FROM {self.tabela} WHERE {self.dono} = %s ORDER BY dataUpload
        """, (id_dono,), erro=f"Erro ao buscar fotos em {self.tabela}:")
        fotos = []
        for r in linhas:
            foto = {
                "idFoto":       r[0],
                self.dono:      id_dono,
                "nomeArquivo":  r[1],
                "nomeOriginal": r[2],
                "dataUpload":   r[3].strftime("%d/%m/%Y %H:%M") if r[3] else "",
                "url":          f"/uploads/{r[1]}",
            }
            if self.com_tipo:
                foto["tipoFoto"] = r[4]
            fotos.append(foto)
        return fotos

    def nomes_arquivos(self, id_dono: int) -> list:
        return [r[0] for r in consultar(f"SELECT nomeArquivo FROM {self.tabela} WHERE {self.dono} = %s",
                                        (id_dono,), erro="Erro ao listar arquivos:")]

    def deletar(self, id_foto: int, id_dono: int):
        """Só apaga a foto se ela pertencer ao dono informado. Retorna o nome do
        arquivo (para apagar do disco) ou None."""
        row = consultar_um(f"SELECT nomeArquivo FROM {self.tabela} WHERE idFoto = %s AND {self.dono} = %s",
                           (id_foto, id_dono), erro="Erro ao buscar foto:")
        if not row:
            return None
        if not executar(f"DELETE FROM {self.tabela} WHERE idFoto = %s", (id_foto,),
                        erro="Erro ao deletar foto:"):
            return None
        return row[0]


def foto_obra_dao() -> FotoDAO:
    return FotoDAO("obra_fotos", "idObra")


def foto_produto_dao() -> FotoDAO:
    return FotoDAO("produto_fotos", "idProduto", com_tipo=True)
