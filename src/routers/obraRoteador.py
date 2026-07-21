import os
from io import BytesIO
from flask import Blueprint, request, jsonify, g, send_file
import pypdf
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from src.controller.obraController      import ObraController
from src.controller.historicoController import HistoricoController
from src.middleware.obraMiddleware      import ObraMiddleware
from src.middleware.jwtMiddleware       import JwtMiddleware
from src.error_response                 import ErrorResponse
from src.dao.conexao                    import Conexao

_PDF_TEMPLATE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "FOLHA DE ROSTO 2.pdf")
)

obra_bp        = Blueprint("obra", __name__, url_prefix="/obra")
controller     = ObraController()
historico_ctrl = HistoricoController()
middleware     = ObraMiddleware()
jwt            = JwtMiddleware()


@obra_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


def _serializar(o):
    return {
        "idObra":         o[0],
        "codCliente":     o[1],
        "descObra":       o[2],
        "dataInicio":     str(o[3]) if o[3] else None,
        "dataFim":        str(o[4]) if o[4] else None,
        "statusObra":     o[5],
        "respObra":       o[6],
        "obsObra":        o[7],
        "orientacaoObra": o[8],
        "tipoObra":         o[9]  if len(o) > 9  else None,
        "clientePrimario":  o[10] if len(o) > 10 else None,
        "fieldObra":        o[11] if len(o) > 11 else None,
        "unidadeObra":      o[12] if len(o) > 12 else None,
        "emailContato":     o[13] if len(o) > 13 else None,
        "celular1":         o[14] if len(o) > 14 else None,
        "celular2":         o[15] if len(o) > 15 else None,
        "valorObra":        float(o[16]) if len(o) > 16 and o[16] is not None else None,
    }


# ─── POST /obra ───────────────────────────────────────────────────────────────
@obra_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def cadastrar():
    body                = request.get_json()
    dados_obra          = body["obra"]
    produtos_usados     = body.get("produtosUsados", [])
    servicos_vinculados = body.get("servicosVinculados", [])
    desc                = dados_obra.get("descObra", "")

    sucesso, mensagem = controller.cadastrar(dados_obra, produtos_usados, servicos_vinculados)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Cadastrou", "Obra",
        f"Cadastrou a obra '{desc}'",
    )

    return jsonify({"status": True, "msg": mensagem}), 201


# ─── GET /obra ────────────────────────────────────────────────────────────────
@obra_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    obras = controller.listar()
    return jsonify({"status": True, "obras": [_serializar(o) for o in obras]}), 200


# ─── GET /obra/<idObra> ───────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_por_id(idObra: int):
    obra = controller.buscar_por_id(idObra)

    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    return jsonify({"status": True, "obra": _serializar(obra)}), 200


# ─── GET /obra/cliente/<idCliente> ────────────────────────────────────────────
@obra_bp.route("/cliente/<int:idCliente>", methods=["GET"])
@jwt.validate_token
def listar_por_cliente(idCliente: int):
    sucesso, mensagem, obras = controller.listar_por_cliente(idCliente)

    if not sucesso:
        raise ErrorResponse(404, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem, "obras": [_serializar(o) for o in obras]}), 200


# ─── GET /obra/<idObra>/produtos ──────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/produtos", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_produtos_da_obra(idObra: int):
    obra = controller.buscar_por_id(idObra)
    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    produtos = controller.buscar_produtos_da_obra(idObra)
    return jsonify({"status": True, "produtos": produtos}), 200


# ─── GET /obra/<idObra>/servicos ─────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/servicos", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_servicos_da_obra(idObra: int):
    obra = controller.buscar_por_id(idObra)
    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    servicos = controller.buscar_servicos_da_obra(idObra)
    return jsonify({"status": True, "servicos": servicos}), 200


# ─── PUT /obra/<idObra> ───────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_update_body
def atualizar(idObra: int):
    body           = request.get_json()
    dados_obra     = body["obra"]
    produtos_novos = body.get("produtosNovos") or []
    servicos_novos = body.get("servicosNovos") or []
    desc           = dados_obra.get("descObra", "")

    sucesso, mensagem = controller.atualizar(idObra, dados_obra, produtos_novos, servicos_novos)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Editou", "Obra",
        f"Editou a obra '{desc}' (ID: {idObra})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── PATCH /obra/<idObra>/produto/<idProduto> ────────────────────────────────
@obra_bp.route("/<int:idObra>/produto/<int:idProduto>", methods=["PATCH"])
@jwt.validate_token
@middleware.validate_id_param
def atualizar_produto_obra(idObra: int, idProduto: int):
    body     = request.get_json() or {}
    nova_qtd = body.get("quantidade")
    if nova_qtd is None or int(nova_qtd) < 1:
        raise ErrorResponse(400, "Quantidade inválida.", {"message": "Informe uma quantidade >= 1."})
    sucesso, mensagem = controller.atualizar_produto_obra(idObra, idProduto, int(nova_qtd))
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /obra/<idObra>/produto/<idProduto> ───────────────────────────────
@obra_bp.route("/<int:idObra>/produto/<int:idProduto>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def remover_produto_obra(idObra: int, idProduto: int):
    sucesso, mensagem = controller.remover_produto_obra(idObra, idProduto)
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    return jsonify({"status": True, "msg": mensagem}), 200


# ─── PATCH /obra/<idObra>/status ─────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/status", methods=["PATCH"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_status_body
def atualizar_status(idObra: int):
    body        = request.get_json()
    novo_status = body["statusObra"]

    sucesso, mensagem = controller.atualizar_status(idObra, novo_status)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Editou", "Obra",
        f"Alterou status da obra ID {idObra} para '{novo_status}'",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /obra/<idObra> ────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def deletar(idObra: int):
    obra = controller.buscar_por_id(idObra)
    desc = obra[2] if obra else str(idObra)

    sucesso, mensagem = controller.deletar(idObra)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Deletou", "Obra",
        f"Deletou a obra '{desc}' (ID: {idObra})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── GET /obra/<idObra>/relatorio ────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/relatorio", methods=["GET"])
@jwt.validate_token
def gerar_relatorio_obra(idObra: int):
    sql = """
        SELECT o.idObra, o.codCliente, o.descObra, o.dataInicio, o.dataFim,
               o.respObra, o.celular1,
               c.CNPJCPF, c.contatoCliente, c.rua, c.numero,
               c.bairro, c.cep, c.cidade, c.estado
        FROM obras o
        LEFT JOIN clientes c ON c.idCliente = o.codCliente
        WHERE o.idObra = %s
    """
    conexao = Conexao.obter_conexao()
    if not conexao:
        raise ErrorResponse(500, "Erro de conexão.", {})
    cursor = conexao.cursor()
    try:
        cursor.execute(sql, (idObra,))
        row = cursor.fetchone()
    finally:
        Conexao.fechar_conexao(conexao, cursor)

    if not row:
        raise ErrorResponse(404, "Obra não encontrada.", {})

    (id_obra, cod_cliente, desc_obra, data_inicio, data_fim,
     resp_obra, celular1,
     cnpj_cpf, contato, rua, numero, bairro, cep, cidade, estado) = row

    def fmt_data(d):
        if not d:
            return ""
        s = str(d).split("T")[0]
        parts = s.split("-")
        return f"{parts[2]}/{parts[1]}/{parts[0]}" if len(parts) == 3 else s

    def wrap_text(text, max_chars):
        words = (text or "").split()
        lines, current = [], ""
        for word in words:
            if len(current) + len(word) + 1 <= max_chars:
                current = f"{current} {word}".strip()
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    FONT      = "Helvetica"
    FONT_SIZE = 10
    LINE_H    = FONT_SIZE + 3

    overlay_buf = BytesIO()
    c = rl_canvas.Canvas(overlay_buf, pagesize=A4)
    c.setFont(FONT, FONT_SIZE)

    def t(x, y, val):
        if val:
            c.drawString(x, y, str(val))

    # ── Cobrir textos pré-impressos que serão substituídos ──
    c.setFillColorRGB(1, 1, 1)
    c.rect(318, 769,  87, 13, fill=1, stroke=0)   # underscores DATA INÍCIO
    c.rect(450, 769,  80, 13, fill=1, stroke=0)   # underscores TÉRMINO
    c.setFillColorRGB(0, 0, 0)

    # ── Valores ──
    t(310, 807, resp_obra)                                   # FIELD: SA-
    t(470, 756, str(cod_cliente) if cod_cliente else "")     # CÓD.CLIENTE
    t(320, 775, fmt_data(data_inicio))                       # DATA INÍCIO
    t(452, 775, fmt_data(data_fim))                          # TÉRMINO
    t(97,  728, rua or "")                                   # ENDEREÇO
    t(325, 728, str(numero) if numero else "")               # Nº
    t(415, 728, bairro or "")                                # BAIRRO
    t(64,  699, cep or "")                                   # CEP
    t(262, 699, cidade or "")                                # CIDADE

    # CNPJ (14 dígitos) vs CPF (11 dígitos)
    digits = "".join(ch for ch in (cnpj_cpf or "") if ch.isdigit())
    if len(digits) > 11:
        t(68, 680, cnpj_cpf or "")    # campo CNPJ
    else:
        t(242, 680, cnpj_cpf or "")   # campo CPF

    t(90,  659, contato or "")                               # CONTATO
    t(332, 659, celular1 or "")                              # TELEFONE

    # DESCRIÇÃO DA OBRA — com quebra de linha
    desc_lines = wrap_text(desc_obra, 68)
    for i, linha in enumerate(desc_lines[:3]):
        t(120, 643 - i * LINE_H, linha)

    # TÉCNICO RESPONSÁVEL (rodapé)
    t(176, 64, resp_obra)

    c.showPage()
    c.save()
    overlay_buf.seek(0)

    reader         = pypdf.PdfReader(_PDF_TEMPLATE)
    overlay_reader = pypdf.PdfReader(overlay_buf)
    writer         = pypdf.PdfWriter()

    page1 = reader.pages[0]
    page1.merge_page(overlay_reader.pages[0])
    writer.add_page(page1)
    for p in reader.pages[1:]:
        writer.add_page(p)

    output_buf = BytesIO()
    writer.write(output_buf)
    output_buf.seek(0)

    return send_file(
        output_buf,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"relatorio_obra_{idObra}.pdf",
    )
