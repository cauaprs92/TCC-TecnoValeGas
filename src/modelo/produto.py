class Produto:
    def __init__(self):
        self._idProduto     = None
        self._nomeProduto   = None
        self._qtdProduto    = None
        self._descProduto   = None
        self._qtdMaxima     = 9999
        self._idFornecedor  = None
        self._nomeFornecedor = None

        # Ajustes opcionais do cálculo do estoque mínimo (gravados no banco)
        self._qtdMinimaManual   = None
        self._prazoEntregaDias  = None   # prazo próprio; None usa o do fornecedor
        self._consumoEstimado   = None
        self._periodoEstimativa = None   # 'dia' | 'semana' | 'mes'

        # Resultado do cálculo (src/service/estoqueMinimo.py), preenchido na
        # leitura. _qtdMinima é o mínimo efetivo: manual ou calculado.
        self._qtdMinima      = 0
        self._estoqueMinimo  = {}
