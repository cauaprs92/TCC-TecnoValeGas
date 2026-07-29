class NotaFiscal:
    def __init__(self):
        self._idNotaFiscal   = None
        self._chaveAcesso    = None
        self._numero         = None
        self._serie          = None
        self._idFornecedor   = None
        self._nomeFornecedor = None
        self._cnpjFornecedor = None
        self._dataEmissao    = None
        self._valorTotal     = None
        self._nomeArquivo    = None
        self._dataImportacao = None
        self._itens          = []


class NotaFiscalItem:
    def __init__(self):
        self._idItem               = None
        self._idNotaFiscal         = None
        self._idProduto            = None
        self._codProdutoFornecedor = None
        self._nomeProdutoNota      = None
        self._quantidade           = None
        self._valorUnitario        = None
        self._valorTotal           = None
        self._statusItem           = 'pendente'
        self._sugestao             = None
