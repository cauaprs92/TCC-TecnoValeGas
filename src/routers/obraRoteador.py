from functools import wraps
from flask import Blueprint, request, jsonify, g
from src.controller.obraController      import ObraController
from src.controller.historicoController import HistoricoController
from src.middleware.obraMiddleware      import ObraMiddleware
from src.middleware.jwtMiddleware       import (
    JwtMiddleware, CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA
)
from src.error_response                 import ErrorResponse
from src.routers.clienteRoteador        import serializar_cliente
from src.dao.fotoDAO                    import foto_obra_dao
from src.uploads                        import EXT_IMAGEM, salvar_arquivo_da_requisicao, apagar_arquivos

obra_bp        = Blueprint("obra", __name__, url_prefix="/obra")
controller     = ObraController()
historico_ctrl = HistoricoController()
middleware     = ObraMiddleware()
jwt            = JwtMiddleware()
foto_dao       = foto_obra_dao()


def _serializar(o, equipe=None, nome_cliente=None):
    dados = {
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
        "setorObra":        o[17] if len(o) > 17 else None,
    }
    dados["funcionarios"] = equipe or []
    dados["nomeCliente"]  = nome_cliente
    return dados


def exigir_acesso_obra(f):
    """Bloqueia o funcionário de obra em qualquer rota de uma obra que não seja
    dele. Vai depois de @jwt.validate_token, que preenche g.cargo e g.admin_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        id_obra = kwargs.get("idObra")
        if id_obra and not controller.usuario_pode_ver_obra(g.get("cargo"), g.get("admin_id"), id_obra):
            raise ErrorResponse(
                403, "Você não tem acesso a esta obra.",
                {"message": "Esta obra não está designada para você."}
            )
        return f(*args, **kwargs)
    return decorated


def _descrever_equipe(ids_funcionarios) -> str:
    """Trecho com os nomes da equipe para a linha do histórico."""
    if not ids_funcionarios:
        return ""
    disponiveis = {u["idLogin"]: u["nomeLogin"] for u in controller.listar_funcionarios_disponiveis()}
    nomes = [disponiveis.get(i, f"ID {i}") for i in ids_funcionarios]
    return f" — equipe: {', '.join(nomes)}"


# ─── POST /obra ───────────────────────────────────────────────────────────────
@obra_bp.route("", methods=["POST"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO)
@middleware.validate_body
def cadastrar():
    body                = request.get_json()
    dados_obra          = body["obra"]
    produtos_usados     = body.get("produtosUsados", [])
    servicos_vinculados = body.get("servicosVinculados", [])
    funcionarios        = body.get("funcionarios", [])
    desc                = dados_obra.get("descObra", "")

    sucesso, mensagem = controller.cadastrar(
        dados_obra, produtos_usados, servicos_vinculados, funcionarios
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Cadastrou", "Obra",
        f"Cadastrou a obra '{desc}'{_descrever_equipe(funcionarios)}",
    )

    return jsonify({"status": True, "msg": mensagem}), 201


# ─── GET /obra ────────────────────────────────────────────────────────────────
@obra_bp.route("", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA)
def listar():
    # Funcionário de obra recebe só as obras em que está na equipe.
    obras   = controller.listar_para_usuario(g.get("cargo"), g.get("admin_id"))
    equipes = controller.buscar_equipes_das_obras([o[0] for o in obras])
    # O nome do cliente vem junto porque nem todo cargo tem acesso à aba
    # Clientes — sem isso a listagem mostraria só o código do cliente.
    nomes   = controller.buscar_nomes_clientes([o[1] for o in obras])
    return jsonify({
        "status": True,
        "obras":  [_serializar(o, equipes.get(o[0]), nomes.get(o[1])) for o in obras],
    }), 200


# ─── GET /obra/funcionarios ───────────────────────────────────────────────────
# Usuários de cargo 'Obra' — é a lista que alimenta o seletor de equipe.
@obra_bp.route("/funcionarios", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO)
def listar_funcionarios():
    return jsonify({"status": True, "funcionarios": controller.listar_funcionarios_disponiveis()}), 200


# ─── GET /obra/<idObra> ───────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA)
@exigir_acesso_obra
def buscar_por_id(idObra: int):
    obra = controller.buscar_por_id(idObra)

    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    equipe = controller.buscar_equipe_da_obra(idObra)
    nomes  = controller.buscar_nomes_clientes([obra[1]])
    return jsonify({"status": True, "obra": _serializar(obra, equipe, nomes.get(obra[1]))}), 200


# ─── GET /obra/<idObra>/cliente ───────────────────────────────────────────────
# O funcionário de obra não tem acesso à lista de clientes, mas precisa ver os
# dados do cliente da obra dele. Aqui ele recebe só esse cliente.
@obra_bp.route("/<int:idObra>/cliente", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA)
@exigir_acesso_obra
def buscar_cliente_da_obra(idObra: int):
    cliente = controller.buscar_cliente_da_obra(idObra)
    if not cliente:
        raise ErrorResponse(404, "Cliente da obra não encontrado.",
                            {"message": f"Nenhum cliente vinculado à obra {idObra}."})

    return jsonify({"status": True, "cliente": serializar_cliente(cliente)}), 200


# ─── GET /obra/<idObra>/produtos ──────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/produtos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA)
@exigir_acesso_obra
def buscar_produtos_da_obra(idObra: int):
    obra = controller.buscar_por_id(idObra)
    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    produtos = controller.buscar_produtos_da_obra(idObra)
    return jsonify({"status": True, "produtos": produtos}), 200


# ─── GET /obra/<idObra>/servicos ─────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/servicos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA)
@exigir_acesso_obra
def buscar_servicos_da_obra(idObra: int):
    obra = controller.buscar_por_id(idObra)
    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    servicos = controller.buscar_servicos_da_obra(idObra)
    return jsonify({"status": True, "servicos": servicos}), 200


# ─── GET /obra/<idObra>/fotos ─────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/fotos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO, CARGO_OBRA)
@exigir_acesso_obra
def listar_fotos(idObra: int):
    fotos = foto_dao.buscar(idObra)
    return jsonify({"status": True, "fotos": fotos}), 200


# ─── POST /obra/<idObra>/fotos ────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>/fotos", methods=["POST"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_OBRA)
@exigir_acesso_obra
def upload_foto(idObra: int):
    obra = controller.buscar_por_id(idObra)
    if not obra:
        raise ErrorResponse(404, "Obra não encontrada.", {"message": f"Nenhuma obra com ID {idObra}."})

    nome_unico, nome_original = salvar_arquivo_da_requisicao(EXT_IMAGEM)
    idFoto = foto_dao.inserir(idObra, nome_unico, nome_original)
    if not idFoto:
        apagar_arquivos(nome_unico)
        raise ErrorResponse(500, "Erro ao salvar foto no banco.", {"message": "Falha ao inserir registro."})

    return jsonify({
        "status": True,
        "foto": {
            "idFoto":       idFoto,
            "nomeArquivo":  nome_unico,
            "nomeOriginal": nome_original,
            "url":          f"/uploads/{nome_unico}",
        }
    }), 201


# ─── DELETE /obra/<idObra>/fotos/<idFoto> ─────────────────────────────────────
@obra_bp.route("/<int:idObra>/fotos/<int:idFoto>", methods=["DELETE"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_OBRA)
@exigir_acesso_obra
def deletar_foto(idObra: int, idFoto: int):
    nome = foto_dao.deletar(idFoto, idObra)
    if not nome:
        raise ErrorResponse(404, "Foto não encontrada.", {"message": f"Foto {idFoto} não existe."})

    apagar_arquivos(nome)

    return jsonify({"status": True, "msg": "Foto removida."}), 200


# ─── PUT /obra/<idObra> ───────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["PUT"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_OBRA)
@exigir_acesso_obra
@middleware.validate_update_body
def atualizar(idObra: int):
    body           = request.get_json()
    dados_obra     = body["obra"]
    produtos_novos = body.get("produtosNovos") or []
    servicos_novos = body.get("servicosNovos") or []
    desc           = dados_obra.get("descObra", "")
    # Ausente = não mexe na equipe; lista vazia = esvazia a equipe de propósito.
    funcionarios   = body.get("funcionarios") if "funcionarios" in body else None

    # Quem decide a designação é a Administração. O funcionário edita tudo na
    # obra dele, menos quem trabalha nela — senão poderia se remover da equipe
    # (perdendo o acesso) ou incluir gente que não foi designada.
    if g.get("cargo") != CARGO_ADMINISTRACAO:
        funcionarios = None

    sucesso, mensagem = controller.atualizar(
        idObra, dados_obra, produtos_novos, servicos_novos, funcionarios
    )

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    equipe_txt = _descrever_equipe(funcionarios) if funcionarios is not None else ""
    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Editou", "Obra",
        f"Editou a obra '{desc}' (ID: {idObra}){equipe_txt}",
    )

    return jsonify({"status": True, "msg": mensagem}), 200


# ─── PATCH /obra/<idObra>/produto/<idProduto> ────────────────────────────────
@obra_bp.route("/<int:idObra>/produto/<int:idProduto>", methods=["PATCH"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_OBRA)
@exigir_acesso_obra
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
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_OBRA)
@exigir_acesso_obra
def remover_produto_obra(idObra: int, idProduto: int):
    sucesso, mensagem = controller.remover_produto_obra(idObra, idProduto)
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    return jsonify({"status": True, "msg": mensagem}), 200


# ─── PATCH /obra/<idObra>/servico/<idServico> ────────────────────────────────
@obra_bp.route("/<int:idObra>/servico/<int:idServico>", methods=["PATCH"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_OBRA)
@exigir_acesso_obra
def atualizar_servico_obra(idObra: int, idServico: int):
    body           = request.get_json() or {}
    id_servico_novo = body.get("idServicoNovo")
    if not id_servico_novo:
        raise ErrorResponse(400, "Serviço inválido.", {"message": "Informe o novo serviço."})
    sucesso, mensagem = controller.atualizar_servico_obra(idObra, idServico, int(id_servico_novo))
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /obra/<idObra>/servico/<idServico> ───────────────────────────────
@obra_bp.route("/<int:idObra>/servico/<int:idServico>", methods=["DELETE"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_OBRA)
@exigir_acesso_obra
def remover_servico_obra(idObra: int, idServico: int):
    sucesso, mensagem = controller.remover_servico_obra(idObra, idServico)
    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})
    return jsonify({"status": True, "msg": mensagem}), 200


# ─── DELETE /obra/<idObra> ────────────────────────────────────────────────────
@obra_bp.route("/<int:idObra>", methods=["DELETE"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_OBRA)
@exigir_acesso_obra
def deletar(idObra: int):
    obra = controller.buscar_por_id(idObra)
    desc = obra[2] if obra else str(idObra)

    sucesso, mensagem, arquivos = controller.deletar(idObra)

    if not sucesso:
        raise ErrorResponse(400, mensagem, {"message": mensagem})

    apagar_arquivos(*arquivos)

    historico_ctrl.registrar(
        g.admin_id, g.jwt_payload.get("nomeLogin"),
        "Deletou", "Obra",
        f"Deletou a obra '{desc}' (ID: {idObra})",
    )

    return jsonify({"status": True, "msg": mensagem}), 200
