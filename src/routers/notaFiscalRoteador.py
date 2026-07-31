from flask import Blueprint, request, jsonify, g
from src.controller.notaFiscalController import NotaFiscalController
from src.controller.historicoController  import HistoricoController
from src.middleware.jwtMiddleware        import JwtMiddleware, CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO
from src.error_response                  import ErrorResponse

nota_fiscal_bp = Blueprint("nota_fiscal", __name__, url_prefix="/nota-fiscal")
controller     = NotaFiscalController()
historico_ctrl = HistoricoController()
jwt            = JwtMiddleware()


@nota_fiscal_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


def _fmt_data(valor):
    return valor.strftime("%Y-%m-%d %H:%M:%S") if valor else None


def _serializar_item(i) -> dict:
    return {
        "idItem":               i._idItem,
        "idNotaFiscal":         i._idNotaFiscal,
        "idProduto":            i._idProduto,
        "codProdutoFornecedor": i._codProdutoFornecedor,
        "nomeProdutoNota":      i._nomeProdutoNota,
        "quantidade":           i._quantidade,
        "valorUnitario":        i._valorUnitario,
        "valorTotal":           i._valorTotal,
        "statusItem":           i._statusItem,
        "sugestao":             i._sugestao,
    }


def _serializar(n) -> dict:
    return {
        "idNotaFiscal":   n._idNotaFiscal,
        "chaveAcesso":    n._chaveAcesso,
        "numero":         n._numero,
        "serie":          n._serie,
        "idFornecedor":   n._idFornecedor,
        "nomeFornecedor": n._nomeFornecedor,
        "cnpjFornecedor": n._cnpjFornecedor,
        "dataEmissao":    _fmt_data(n._dataEmissao),
        "valorTotal":     n._valorTotal,
        "nomeArquivo":    n._nomeArquivo,
        "dataImportacao": _fmt_data(n._dataImportacao),
        "itens":          [_serializar_item(i) for i in n._itens],
    }


# ─── POST /nota-fiscal/importar ───────────────────────────────────────────────
@nota_fiscal_bp.route("/importar", methods=["POST"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def importar():
    if 'arquivo' not in request.files:
        raise ErrorResponse(400, "Nenhum arquivo enviado.", {"message": "Campo 'arquivo' ausente."})

    arquivo = request.files['arquivo']
    if not arquivo.filename:
        raise ErrorResponse(400, "Arquivo inválido.", {"message": "Nome de arquivo vazio."})

    if not arquivo.filename.lower().endswith('.xml'):
        raise ErrorResponse(400, "Tipo de arquivo não permitido.", {"message": "Envie o XML da NF-e."})

    conteudo = arquivo.read()

    sucesso, mensagem, nota, reaberta = controller.importar_xml(conteudo, arquivo.filename)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    if reaberta:
        historico_ctrl.registrar(
            g.admin_id, g.jwt_payload.get("nomeLogin"),
            "Reabriu", "Nota Fiscal",
            f"Reabriu a conferência da nota fiscal nº {nota._numero} "
            f"de '{nota._nomeFornecedor}'",
        )
    else:
        historico_ctrl.registrar(
            g.admin_id, g.jwt_payload.get("nomeLogin"),
            "Importou", "Nota Fiscal",
            f"Importou a nota fiscal nº {nota._numero} de '{nota._nomeFornecedor}' "
            f"({len(nota._itens)} itens)",
        )

    return jsonify({
        "status":   True,
        "msg":      mensagem,
        "reaberta": reaberta,
        "nota":     _serializar(nota),
    }), 200 if reaberta else 201


# ─── GET /nota-fiscal/<idNotaFiscal>/itens ────────────────────────────────────
@nota_fiscal_bp.route("/<int:idNotaFiscal>/itens", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def listar_itens(idNotaFiscal: int):
    nota = controller.buscar_nota(idNotaFiscal)

    if not nota:
        raise ErrorResponse(404, "Nota fiscal não encontrada.",
                            {"message": f"Nenhuma nota fiscal com ID {idNotaFiscal}."})

    apenasPendentes = request.args.get("pendentes", "").lower() in ('1', 'true', 'sim')
    itens = [i for i in nota._itens if i._statusItem == 'pendente'] if apenasPendentes else nota._itens

    return jsonify({
        "status": True,
        "nota":   _serializar(nota),
        "itens":  [_serializar_item(i) for i in itens],
    }), 200


# ─── PATCH /nota-fiscal/item/<idItem>/confirmar ───────────────────────────────
@nota_fiscal_bp.route("/item/<int:idItem>/confirmar", methods=["PATCH"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def confirmar_item(idItem: int):
    corpo = request.get_json(silent=True) or {}
    acao  = corpo.get("acao")

    sucesso, mensagem, idProduto = controller.confirmar_item(
        idItem,
        acao,
        corpo.get("idProduto"),
        corpo.get("qtdMinima"),
        corpo.get("qtdMaxima"),
        corpo.get("produto"),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    acoes = {
        "repor":   ("Repôs",     "Repôs o estoque do produto ID {id} a partir do item {item} da nota fiscal"),
        "criar":   ("Cadastrou", "Cadastrou o produto ID {id} a partir do item {item} da nota fiscal"),
        "ignorar": ("Ignorou",   "Ignorou o item {item} da nota fiscal"),
    }
    rotulo, descricao = acoes[(acao or "").strip().lower()]
    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        rotulo, "Nota Fiscal",
        descricao.format(id=idProduto, item=idItem),
    )

    return jsonify({"status": True, "msg": mensagem, "idProduto": idProduto}), 200
