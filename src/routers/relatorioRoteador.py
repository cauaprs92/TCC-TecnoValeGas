from flask import Blueprint, jsonify
from src.middleware.jwtMiddleware import JwtMiddleware, CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO
from src.dao.conexao              import Conexao
from src.error_response           import ErrorResponse

relatorio_bp = Blueprint("relatorio", __name__, url_prefix="/relatorio")
jwt          = JwtMiddleware()


@relatorio_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


# ─── GET /relatorio/produtos-consumidos ───────────────────────────────────────
# Retorna total consumido por produto (para exportação)
@relatorio_bp.route("/produtos-consumidos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def produtos_consumidos():
    # Consumo = produtos avulsos + receita dos serviços (vw_consumo_obra).
    # Obra cancelada já devolveu o material ao estoque, então não conta.
    sql = """
        SELECT p.idProduto, p.nomeProduto,
               COALESCE(SUM(c.quantidade), 0) AS totalConsumido,
               p.qtdProduto AS estoqueAtual,
               p.qtdMinima
        FROM produtos p
        LEFT JOIN (
            SELECT v.idProduto, v.quantidade
            FROM vw_consumo_obra v
            JOIN obras o ON o.idObra = v.idObra
            WHERE o.statusObra <> 'Cancelada'
        ) c ON c.idProduto = p.idProduto
        GROUP BY p.idProduto, p.nomeProduto, p.qtdProduto, p.qtdMinima
        ORDER BY totalConsumido DESC
    """
    conexao = Conexao.obter_conexao()
    if not conexao:
        return jsonify({"status": False, "msg": "Erro de conexão."}), 500
    cursor = conexao.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        data = [
            {
                "idProduto":      r[0],
                "nomeProduto":    r[1],
                "totalConsumido": int(r[2]),
                "estoqueAtual":   r[3],
                "qtdMinima":      r[4],
            }
            for r in rows
        ]
        return jsonify({"status": True, "dados": data}), 200
    except Exception as e:
        return jsonify({"status": False, "msg": str(e)}), 500
    finally:
        Conexao.fechar_conexao(conexao, cursor)


# ─── GET /relatorio/grafico-produtos ─────────────────────────────────────────
@relatorio_bp.route("/grafico-produtos", methods=["GET"])
@jwt.validate_token
@jwt.require_cargo(CARGO_ADMINISTRACAO, CARGO_ALMOXARIFADO)
def grafico_produtos():
    sql = """
        SELECT p.idProduto, p.nomeProduto,
               o.idObra, o.descObra, c.nomeCliente,
               SUM(v.quantidade), o.codCliente
        FROM vw_consumo_obra v
        JOIN produtos p       ON p.idProduto = v.idProduto
        JOIN obras o          ON o.idObra    = v.idObra
        LEFT JOIN clientes c  ON c.idCliente = o.codCliente
        WHERE o.statusObra <> 'Cancelada'
        GROUP BY p.idProduto, p.nomeProduto, o.idObra, o.descObra, c.nomeCliente, o.codCliente
        ORDER BY p.idProduto, o.idObra
    """
    conexao = Conexao.obter_conexao()
    if not conexao:
        return jsonify({"status": False, "msg": "Erro de conexão."}), 500
    cursor = conexao.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()

        produtos = {}
        for r in rows:
            pid = r[0]
            if pid not in produtos:
                produtos[pid] = {"idProduto": pid, "nomeProduto": r[1], "totalConsumido": 0, "obras": []}
            produtos[pid]["totalConsumido"] += int(r[5])
            produtos[pid]["obras"].append({
                "idObra":      r[2],
                "descObra":    r[3],
                "nomeCliente": r[4] or f"Cliente #{r[6]}",
                "qtd":         int(r[5]),
            })

        data = sorted(produtos.values(), key=lambda x: x["totalConsumido"], reverse=True)
        return jsonify({"status": True, "dados": data}), 200
    except Exception as e:
        return jsonify({"status": False, "msg": str(e)}), 500
    finally:
        Conexao.fechar_conexao(conexao, cursor)
