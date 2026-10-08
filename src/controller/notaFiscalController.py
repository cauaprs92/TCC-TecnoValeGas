from src.dao.notaFiscalDAO import NotaFiscalDAO
from src.controller.produtoController import ProdutoController
from src.service.nfeParser import parse_nfe, NFeParserError
from src.service.pdfParaXml import pdf_para_nfe_xml

_ACOES_VALIDAS = ('repor', 'criar', 'ignorar')
_FORMATOS = ('.xml', '.pdf')


class NotaFiscalController:

    def __init__(self):
        self.dao          = NotaFiscalDAO()
        self.produto_ctrl = ProdutoController()

    # ─── Importação ───────────────────────────────────────────────────────────

    @staticmethod
    def formato_suportado(nomeArquivo: str) -> bool:
        return (nomeArquivo or "").lower().endswith(_FORMATOS)

    def importar_arquivo(self, conteudo, nomeArquivo: str) -> tuple:
        """Lê o arquivo (XML ou PDF), grava a nota e seus itens e devolve a nota
        pronta para conferência.

        O PDF da nota é convertido em XML de NF-e antes; daí em diante o
        caminho é o mesmo do XML (parse_nfe).

        Se a chave já existe, reabre a nota em vez de recusar o arquivo — um
        produto excluído por engano precisa poder ser conferido de novo. Vale
        também entre formatos: a mesma nota importada por PDF e depois por XML
        tem a mesma chave e não duplica.

        Retorna (sucesso, mensagem, nota, reaberta).
        """
        if not self.formato_suportado(nomeArquivo):
            return False, "Formato não suportado. Envie o XML ou o PDF da NF-e.", None, False

        try:
            if nomeArquivo.lower().endswith(".pdf"):
                conteudo = pdf_para_nfe_xml(conteudo)
            dadosNota = parse_nfe(conteudo)
        except NFeParserError as e:
            return False, str(e), None, False

        idExistente = self.dao.buscar_id_por_chave(dadosNota["chaveAcesso"])
        if idExistente:
            return self._reabrir(idExistente)

        dadosNota["nomeArquivo"] = (nomeArquivo or "").strip() or None

        idNotaFiscal = self.dao.inserir_nota_com_itens(dadosNota)
        if not idNotaFiscal:
            return False, "Erro ao salvar a nota fiscal.", None, False

        nota = self.dao.buscar_nota_com_itens(idNotaFiscal)
        if not nota:
            return False, "Erro ao carregar a nota fiscal importada.", None, False

        return True, "Nota fiscal importada com sucesso!", nota, False

    def _reabrir(self, idNotaFiscal: int) -> tuple:
        """Reabre uma nota já importada, trazendo de volta os itens conferíveis."""
        reabertos = self.dao.reabrir_itens(idNotaFiscal)

        nota = self.dao.buscar_nota_com_itens(idNotaFiscal)
        if not nota:
            return False, "Erro ao carregar a nota fiscal.", None, False

        pendentes = sum(1 for i in nota._itens if i._statusItem == 'pendente')
        if not pendentes:
            return False, ("Esta nota já foi importada e todos os itens já estão no estoque."), None, False

        if reabertos:
            mensagem = (f"Nota reaberta — {reabertos} item voltou para a conferência."
                        if reabertos == 1 else
                        f"Nota reaberta — {reabertos} itens voltaram para a conferência.")
        else:
            mensagem = (f"Esta nota já foi importada — {pendentes} item ainda pendente."
                        if pendentes == 1 else
                        f"Esta nota já foi importada — {pendentes} itens ainda pendentes.")

        return True, mensagem, nota, True

    # ─── Conferência ──────────────────────────────────────────────────────────

    def confirmar_item(self, idItem, acao, idProduto=None, dadosNovoProduto=None) -> tuple:
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
            quantidade = int(round(item._quantidade or 0))
            if quantidade <= 0:
                return False, "A quantidade do item na nota deve ser maior que zero.", None

            # Mesma validação do cadastro de produto (nome, máximo, estoque
            # mínimo, custo e margem). Estoque e fornecedor vêm da nota.
            dados = dict(dadosNovoProduto or {})
            dados["nomeProduto"] = dados.get("nomeProduto") or item._nomeProdutoNota
            dados["qtdProduto"]  = quantidade
            dados["fornecedor"]  = None
            valido, mensagem, produto = self.produto_ctrl.montar(dados)
            if not valido:
                return False, mensagem, None
            return self.dao.confirmar_item(idItem, 'criar', novoProduto=produto)

        return self.dao.confirmar_item(idItem, 'ignorar')
