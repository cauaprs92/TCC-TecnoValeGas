import os
import uuid
from flask import Blueprint, request, jsonify, g
from src.controller.produtoController    import ProdutoController
from src.controller.historicoController  import HistoricoController
from src.middleware.produtoMiddleware    import ProdutoMiddleware
from src.middleware.jwtMiddleware        import JwtMiddleware
from src.dao.fotoProdutoDAO              import FotoProdutoDAO
from src.error_response                  import ErrorResponse

produto_bp     = Blueprint("produto", __name__, url_prefix="/produto")
controller     = ProdutoController()
historico_ctrl = HistoricoController()
middleware     = ProdutoMiddleware()
jwt            = JwtMiddleware()
foto_dao       = FotoProdutoDAO()

UPLOADS_DIR        = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'uploads')
_ALLOWED_EXT       = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf'}

def _extensao_permitida(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in _ALLOWED_EXT


@produto_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


def _serializar(p) -> dict:
    return {
        "idProduto":      p._idProduto,
        "nomeProduto":    p._nomeProduto,
        "qtdProduto":     p._qtdProduto,
        "descProduto":    p._descProduto,
        "qtdMinima":      p._qtdMinima,
        "qtdMaxima":      p._qtdMaxima,
        "idFornecedor":   p._idFornecedor,
        "nomeFornecedor": p._nomeFornecedor,
    }


# ─── POST /produto ────────────────────────────────────────────────────────────
@produto_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def cadastrar():
    produto = request.get_json()["produto"]
    nome    = produto.get("nomeProduto")

    sucesso, mensagem, aviso, idProduto = controller.cadastrar(
        nome,
        produto.get("qtdProduto"),
        produto.get("descProduto", ""),
        int(produto.get("qtdMinima") or 0),
        int(produto.get("qtdMaxima") or 9999),
        produto.get("fornecedor"),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Cadastrou", "Produto",
        f"Cadastrou o produto '{nome}'",
    )

    resposta = {"status": True, "msg": mensagem, "idProduto": idProduto}
    if aviso:
        resposta["aviso"] = aviso
    return jsonify(resposta), 201


# ─── GET /produto ─────────────────────────────────────────────────────────────
@produto_bp.route("", methods=["GET"])
@jwt.validate_token
def listar():
    produtos = controller.listar()
    return jsonify({"status": True, "produtos": [_serializar(p) for p in produtos]}), 200


# ─── GET /produto/<idProduto> ─────────────────────────────────────────────────
@produto_bp.route("/<int:idProduto>", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_por_id(idProduto: int):
    produto = controller.buscar_por_id(idProduto)

    if not produto:
        raise ErrorResponse(404, "Produto não encontrado.", {"message": f"Nenhum produto com ID {idProduto}."})

    return jsonify({"status": True, "produto": _serializar(produto)}), 200


# ─── PUT /produto/<idProduto> ─────────────────────────────────────────────────
@produto_bp.route("/<int:idProduto>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_body
def editar(idProduto: int):
    produto = request.get_json()["produto"]
    nome    = produto.get("nomeProduto")

    sucesso, mensagem, aviso = controller.editar(
        idProduto,
        nome,
        produto.get("qtdProduto"),
        produto.get("descProduto", ""),
        int(produto.get("qtdMinima") or 0),
        int(produto.get("qtdMaxima") or 9999),
        produto.get("fornecedor"),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Editou", "Produto",
        f"Editou o produto '{nome}' (ID: {idProduto})",
    )

    resposta = {"status": True, "msg": mensagem}
    if aviso:
        resposta["aviso"] = aviso
    return jsonify(resposta), 200


# ─── DELETE /produto/<idProduto> ──────────────────────────────────────────────
@produto_bp.route("/<int:idProduto>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def deletar(idProduto: int):
    produto = controller.buscar_por_id(idProduto)
    nome    = produto._nomeProduto if produto else str(idProduto)

    sucesso, mensagem, _ = controller.deletar(idProduto)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Deletou", "Produto",
        f"Deletou o produto '{nome}' (ID: {idProduto})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── GET /produto/<idProduto>/fotos ──────────────────────────────────────────
@produto_bp.route("/<int:idProduto>/fotos", methods=["GET"])
@jwt.validate_token
def listar_fotos(idProduto: int):
    fotos = foto_dao.buscar_por_produto(idProduto)
    return jsonify({"status": True, "fotos": fotos}), 200


# ─── POST /produto/<idProduto>/fotos ─────────────────────────────────────────
@produto_bp.route("/<int:idProduto>/fotos", methods=["POST"])
@jwt.validate_token
def upload_foto(idProduto: int):
    if 'arquivo' not in request.files:
        raise ErrorResponse(400, "Nenhum arquivo enviado.", {"message": "Campo 'arquivo' ausente."})

    arquivo = request.files['arquivo']
    if not arquivo.filename:
        raise ErrorResponse(400, "Arquivo inválido.", {"message": "Nome de arquivo vazio."})

    if not _extensao_permitida(arquivo.filename):
        raise ErrorResponse(400, "Tipo de arquivo não permitido.", {"message": "Permitidos: JPG, PNG, GIF, WebP, PDF."})

    tipoFoto = request.form.get('tipoFoto', 'produto')
    if tipoFoto not in ('produto', 'nota_fiscal'):
        tipoFoto = 'produto'

    ext        = arquivo.filename.rsplit('.', 1)[1].lower()
    nome_unico = f"{uuid.uuid4().hex}.{ext}"

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    arquivo.save(os.path.join(UPLOADS_DIR, nome_unico))

    idFoto = foto_dao.inserir(idProduto, tipoFoto, nome_unico, arquivo.filename)
    if not idFoto:
        raise ErrorResponse(500, "Erro ao salvar foto no banco.", {"message": "Falha ao inserir registro."})

    return jsonify({
        "status": True,
        "foto": {
            "idFoto":       idFoto,
            "tipoFoto":     tipoFoto,
            "nomeArquivo":  nome_unico,
            "nomeOriginal": arquivo.filename,
            "url":          f"/uploads/{nome_unico}",
        }
    }), 201


# ─── DELETE /produto/<idProduto>/fotos/<idFoto> ───────────────────────────────
@produto_bp.route("/<int:idProduto>/fotos/<int:idFoto>", methods=["DELETE"])
@jwt.validate_token
def deletar_foto(idProduto: int, idFoto: int):
    nome = foto_dao.deletar(idFoto)
    if not nome:
        raise ErrorResponse(404, "Foto não encontrada.", {"message": f"Foto {idFoto} não existe."})

    caminho = os.path.join(UPLOADS_DIR, nome)
    if os.path.exists(caminho):
        os.remove(caminho)

    return jsonify({"status": True, "msg": "Foto removida."}), 200


# ─── GET /produto/<idProduto>/estoque ─────────────────────────────────────────
@produto_bp.route("/<int:idProduto>/estoque", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def verificar_estoque(idProduto: int):
    quantidade = request.args.get("quantidade", 1)

    try:
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ErrorResponse(400, "Parâmetro inválido.", {"message": "O parâmetro 'quantidade' deve ser um inteiro positivo."})

    disponivel, mensagem = controller.verificar_estoque(idProduto, quantidade)

    if not disponivel:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 200
