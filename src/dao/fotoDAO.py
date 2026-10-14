from src.dao.banco import consultar, consultar_um, executar, inserir


class FotoDAO:
    """Fotos de uma entidade — obra_fotos (dono idObra) ou produto_fotos (dono
    idProduto, com tipoFoto 'produto' ou 'nota_fiscal'). O arquivo fica na
    própria linha, em base64 (conteudo), e nomeArquivo é o identificador
    aleatório usado na URL /uploads/<nomeArquivo>."""

    def __init__(self, tabela: str, dono: str, com_tipo: bool = False):
        self.tabela, self.dono, self.com_tipo = tabela, dono, com_tipo

    def inserir(self, id_dono: int, arquivo: dict, tipo: str = None):
        """`arquivo` é o dict de ler_arquivo_da_requisicao."""
        colunas = [self.dono, "nomeArquivo", "nomeOriginal", "tipoMime", "conteudo"]             + (["tipoFoto"] if self.com_tipo else [])
        valores = [id_dono, arquivo["nomeArquivo"], arquivo["nomeOriginal"],
                   arquivo["tipoMime"], arquivo["conteudo"]] + ([tipo] if self.com_tipo else [])
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

    def buscar_arquivo(self, nome_arquivo: str):
        """(tipoMime, conteudo em base64) da foto com esse nome, ou None."""
        return consultar_um(f"SELECT tipoMime, conteudo FROM {self.tabela} WHERE nomeArquivo = %s",
                            (nome_arquivo,), erro="Erro ao buscar arquivo:")

    def deletar(self, id_foto: int, id_dono: int) -> bool:
        """Só apaga a foto se ela pertencer ao dono informado."""
        if not consultar_um(f"SELECT 1 FROM {self.tabela} WHERE idFoto = %s AND {self.dono} = %s",
                            (id_foto, id_dono), erro="Erro ao buscar foto:"):
            return False
        return bool(executar(f"DELETE FROM {self.tabela} WHERE idFoto = %s", (id_foto,),
                             erro="Erro ao deletar foto:"))


def foto_obra_dao() -> FotoDAO:
    return FotoDAO("obra_fotos", "idObra")


def foto_produto_dao() -> FotoDAO:
    return FotoDAO("produto_fotos", "idProduto", com_tipo=True)
