from flask import Blueprint, request, jsonify, g
from src.controller.produtoController    import ProdutoController
from src.controller.historicoController  import HistoricoController
from src.middleware.produtoMiddleware    import ProdutoMiddleware
from src.middleware.jwtMiddleware        import JwtMiddleware, CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA
from src.dao.fotoDAO                     import foto_produto_dao
from src.uploads                         import EXT_IMAGEM, salvar_arquivo_da_requisicao, apagar_arquivos
from src.error_response                  import ErrorResponse

produto_bp     = Blueprint("produto", __name__, url_prefix="/produto")
controller     = ProdutoController()
historico_ctrl = HistoricoController()
middleware     = ProdutoMiddleware()
jwt            = JwtMiddleware()
foto_dao       = foto_produto_dao()


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
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
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
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA)
def listar():
    produtos = controller.listar()
    return jsonify({"status": True, "produtos": [_serializar(p) for p in produtos]}), 200


# ─── GET /produto/<idProduto> ─────────────────────────────────────────────────
@produto_bp.route("/<int:idProduto>", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA)
def buscar_por_id(idProduto: int):
    produto = controller.buscar_por_id(idProduto)

    if not produto:
        raise ErrorResponse(404, "Produto não encontrado.", {"message": f"Nenhum produto com ID {idProduto}."})

    return jsonify({"status": True, "produto": _serializar(produto)}), 200


# ─── PUT /produto/<idProduto> ─────────────────────────────────────────────────
@produto_bp.route("/<int:idProduto>", methods=["PUT"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
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
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def deletar(idProduto: int):
    produto = controller.buscar_por_id(idProduto)
    nome    = produto._nomeProduto if produto else str(idProduto)
    # As linhas de produto_fotos saem por ON DELETE CASCADE; os arquivos, não.
    arquivos = foto_dao.nomes_arquivos(idProduto)

    sucesso, mensagem, _ = controller.deletar(idProduto)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    apagar_arquivos(*arquivos)

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Deletou", "Produto",
        f"Deletou o produto '{nome}' (ID: {idProduto})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── GET /produto/<idProduto>/fotos ──────────────────────────────────────────
@produto_bp.route("/<int:idProduto>/fotos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA)
def listar_fotos(idProduto: int):
    fotos = foto_dao.buscar(idProduto)
    return jsonify({"status": True, "fotos": fotos}), 200


# ─── POST /produto/<idProduto>/fotos ─────────────────────────────────────────
@produto_bp.route("/<int:idProduto>/fotos", methods=["POST"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def upload_foto(idProduto: int):
    if not controller.buscar_por_id(idProduto):
        raise ErrorResponse(404, "Produto não encontrado.", {"message": f"Nenhum produto com ID {idProduto}."})

    tipoFoto = request.form.get('tipoFoto', 'produto')
    if tipoFoto not in ('produto', 'nota_fiscal'):
        tipoFoto = 'produto'

    # Nota fiscal pode vir digitalizada em PDF; foto de produto, só imagem.
    nome_unico, nome_original = salvar_arquivo_da_requisicao(EXT_IMAGEM | {"pdf"})
    idFoto = foto_dao.inserir(idProduto, nome_unico, nome_original, tipoFoto)
    if not idFoto:
        apagar_arquivos(nome_unico)
        raise ErrorResponse(500, "Erro ao salvar foto no banco.", {"message": "Falha ao inserir registro."})

    return jsonify({
        "status": True,
        "foto": {
            "idFoto":       idFoto,
            "tipoFoto":     tipoFoto,
            "nomeArquivo":  nome_unico,
            "nomeOriginal": nome_original,
            "url":          f"/uploads/{nome_unico}",
        }
    }), 201


# ─── DELETE /produto/<idProduto>/fotos/<idFoto> ───────────────────────────────
@produto_bp.route("/<int:idProduto>/fotos/<int:idFoto>", methods=["DELETE"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def deletar_foto(idProduto: int, idFoto: int):
    nome = foto_dao.deletar(idFoto, idProduto)
    if not nome:
        raise ErrorResponse(404, "Foto não encontrada.", {"message": f"Foto {idFoto} não existe."})

    apagar_arquivos(nome)

    return jsonify({"status": True, "msg": "Foto removida."}), 200
