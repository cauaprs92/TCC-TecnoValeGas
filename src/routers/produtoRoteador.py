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


# ─── POST /produto ────────────────────────────────────────────────────────────
@produto_bp.route("", methods=["POST"])
@jwt.validate_token
@middleware.validate_body
def cadastrar():
    """Cadastra um novo produto no estoque."""
    body    = request.get_json()
    produto = body["produto"]

    sucesso, mensagem, aviso = controller.cadastrar(
        produto.get("idProduto"),
        produto.get("nomeProduto"),
        produto.get("qtdProduto"),
        produto.get("descProduto", ""),
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
    """Lista todos os produtos do estoque."""
    produtos = controller.listar()

    resultado = [
        {
            "idProduto":   p._idProduto,
            "nomeProduto": p._nomeProduto,
            "qtdProduto":  p._qtdProduto,
            "descProduto": p._descProduto,
        }
        for p in produtos
    ]

    return jsonify({"status": True, "produtos": resultado}), 200


# ─── GET /produto/<idProduto> ─────────────────────────────────────────────────
@produto_bp.route("/<int:idProduto>", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def buscar_por_id(idProduto: int):
    """Busca um produto pelo ID."""
    produto = controller.buscar_por_id(idProduto)

    if not produto:
        raise ErrorResponse(404, "Produto não encontrado.", {"message": f"Nenhum produto com ID {idProduto}."})

    resultado = {
        "idProduto":   produto._idProduto,
        "nomeProduto": produto._nomeProduto,
        "qtdProduto":  produto._qtdProduto,
        "descProduto": produto._descProduto,
    }

    return jsonify({"status": True, "produto": resultado}), 200


# ─── PUT /produto/<idProduto> ─────────────────────────────────────────────────
@produto_bp.route("/<int:idProduto>", methods=["PUT"])
@jwt.validate_token
@middleware.validate_id_param
@middleware.validate_body
def editar(idProduto: int):
    """Atualiza os dados de um produto existente."""
    body    = request.get_json()
    produto = body["produto"]

    sucesso, mensagem, aviso = controller.editar(
        idProduto,
        produto.get("nomeProduto"),
        produto.get("qtdProduto"),
        produto.get("descProduto", ""),
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
    """Remove um produto pelo ID."""
    sucesso, mensagem, _ = controller.deletar(idProduto)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── GET /produto/<idProduto>/estoque ─────────────────────────────────────────
@produto_bp.route("/<int:idProduto>/estoque", methods=["GET"])
@jwt.validate_token
@middleware.validate_id_param
def verificar_estoque(idProduto: int):
    """Verifica a disponibilidade de estoque de um produto."""
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