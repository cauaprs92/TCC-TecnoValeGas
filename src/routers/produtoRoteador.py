from flask import Blueprint, request, jsonify
from src.controller.produtoController import ProdutoController
from src.middleware.produtoMiddleware import ProdutoMiddleware
from src.middleware.jwtMiddleware import JwtMiddleware
from src.error_response import ErrorResponse

produto_bp = Blueprint("produto", __name__, url_prefix="/produto")
controller = ProdutoController()
middleware = ProdutoMiddleware()
jwt = JwtMiddleware()


@produto_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


def _serializar(p) -> dict:
    return {
        "idProduto":   p._idProduto,
        "nomeProduto": p._nomeProduto,
        "qtdProduto":  p._qtdProduto,
        "descProduto": p._descProduto,
        "qtdMinima":   p._qtdMinima,
        "qtdMaxima":   p._qtdMaxima,
    }


# ─── POST /produto ────────────────────────────────────────────────────────────
@produto_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def cadastrar():
    produto = request.get_json()["produto"]

    sucesso, mensagem, aviso = controller.cadastrar(
        produto.get("nomeProduto"),
        produto.get("qtdProduto"),
        produto.get("descProduto", ""),
        int(produto.get("qtdMinima") or 0),
        int(produto.get("qtdMaxima") or 9999),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    resposta = {"status": True, "msg": mensagem}
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

    sucesso, mensagem, aviso = controller.editar(
        idProduto,
        produto.get("nomeProduto"),
        produto.get("qtdProduto"),
        produto.get("descProduto", ""),
        int(produto.get("qtdMinima") or 0),
        int(produto.get("qtdMaxima") or 9999),
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    resposta = {"status": True, "msg": mensagem}
    if aviso:
        resposta["aviso"] = aviso
    return jsonify(resposta), 200


# ─── DELETE /produto/<idProduto> ──────────────────────────────────────────────
@produto_bp.route("/<int:idProduto>", methods=["DELETE"])
@jwt.validate_token
@middleware.validate_id_param
def deletar(idProduto: int):
    sucesso, mensagem, _ = controller.deletar(idProduto)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 200


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
