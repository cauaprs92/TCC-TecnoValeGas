from src.dao.notaFiscalDAO import NotaFiscalDAO
from src.service.nfeParser import parse_nfe, NFeParserError

_ACOES_VALIDAS = ('repor', 'criar', 'ignorar')


class NotaFiscalController:

    def __init__(self):
        self.dao = NotaFiscalDAO()

    # ─── Importação ───────────────────────────────────────────────────────────

    def importar_xml(self, conteudoXml, nomeArquivo: str = None) -> tuple:
        """Lê o XML, grava a nota e seus itens e devolve a nota pronta para conferência.

        Retorna (sucesso, mensagem, nota).
        """
        try:
            dadosNota = parse_nfe(conteudoXml)
        except NFeParserError as e:
            return False, str(e), None

        if self.dao.verificar_chave_existe(dadosNota["chaveAcesso"]):
            return False, "Esta nota já foi importada anteriormente.", None

        dadosNota["nomeArquivo"] = (nomeArquivo or "").strip() or None

        idNotaFiscal = self.dao.inserir_nota(dadosNota)
        if not idNotaFiscal:
            return False, "Erro ao salvar a nota fiscal.", None

        if not self.dao.inserir_itens(idNotaFiscal, dadosNota["itens"]):
            return False, "Erro ao salvar os itens da nota fiscal.", None

        nota = self.dao.buscar_nota_com_itens(idNotaFiscal)
        if not nota:
            return False, "Erro ao carregar a nota fiscal importada.", None

        return True, "Nota fiscal importada com sucesso!", nota

    # ─── Conferência ──────────────────────────────────────────────────────────

    def buscar_nota(self, idNotaFiscal: int):
        return self.dao.buscar_nota_com_itens(idNotaFiscal)

    def listar_itens_pendentes(self, idNotaFiscal: int) -> list:
        nota = self.dao.buscar_nota_com_itens(idNotaFiscal)
        if not nota:
            return []
        return [i for i in nota._itens if i._statusItem == 'pendente']

    def confirmar_item(self, idItem, acao, idProduto=None, quantidadeMinima=None,
                       quantidadeMaxima=None, dadosNovoProduto=None) -> tuple:
        """Valida a decisão do usuário antes de aplicá-la ao estoque.

        Retorna (sucesso, mensagem, idProduto).
        """
        try:
            idItem = int(idItem)
            if idItem <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return False, "ID do item deve ser um inteiro positivo.", None

        acao = (acao or "").strip().lower()
        if acao not in _ACOES_VALIDAS:
            return False, "Ação inválida. Use 'repor', 'criar' ou 'ignorar'.", None

        item = self.dao.buscar_item_por_id(idItem)
        if not item:
            return False, "Item da nota fiscal não encontrado.", None
        if item._statusItem != 'pendente':
            return False, "Este item já foi conferido anteriormente.", None

        if acao == 'repor':
            try:
                idProduto = int(idProduto)
                if idProduto <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return False, "Selecione um produto para repor o estoque.", None
            return self.dao.confirmar_item(idItem, 'repor', idProduto=idProduto)

        if acao == 'criar':
            dados = dadosNovoProduto or {}
            nome  = (dados.get("nomeProduto") or item._nomeProdutoNota or "").strip()
            if not nome:
                return False, "Nome do produto não pode ser vazio.", None
            if len(nome) < 3:
                return False, "Nome deve ter pelo menos 3 caracteres.", None

            valido, mensagem, qtdMin = self._validar_limite(quantidadeMinima, 0, "mínima")
            if not valido:
                return False, mensagem, None
            valido, mensagem, qtdMax = self._validar_limite(quantidadeMaxima, 9999, "máxima")
            if not valido:
                return False, mensagem, None
            if qtdMax > 0 and qtdMin > qtdMax:
                return False, "Quantidade mínima não pode ser maior que a máxima.", None

            quantidade = int(round(item._quantidade or 0))
            if quantidade <= 0:
                return False, "A quantidade do item na nota deve ser maior que zero.", None
            if qtdMax > 0 and quantidade > qtdMax:
                return False, (f"A quantidade da nota ({quantidade}) passa da quantidade "
                               f"máxima informada ({qtdMax})."), None

            dados["nomeProduto"] = nome
            return self.dao.confirmar_item(
                idItem, 'criar',
                quantidadeMinima=qtdMin, quantidadeMaxima=qtdMax, dadosNovoProduto=dados
            )

        return self.dao.confirmar_item(idItem, 'ignorar')

    def _validar_limite(self, valor, padrao: int, rotulo: str) -> tuple:
        if valor is None or valor == "":
            return True, "", padrao
        try:
            limite = int(valor)
        except (ValueError, TypeError):
            return False, f"Quantidade {rotulo} deve ser um número inteiro.", None
        if limite < 0:
            return False, f"Quantidade {rotulo} não pode ser negativa.", None
        return True, "", limite
