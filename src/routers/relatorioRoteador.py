from flask import Blueprint, jsonify
from src.middleware.jwtMiddleware import JwtMiddleware
from src.dao.conexao              import Conexao
from src.error_response           import ErrorResponse

relatorio_bp = Blueprint("relatorio", __name__, url_prefix="/relatorio")
jwt          = JwtMiddleware()


@relatorio_bp.errorhandler(ErrorResponse)
def handle_error(e: ErrorResponse):
    return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode


# ─── GET /relatorio/obras-produtos ────────────────────────────────────────────
# Retorna as últimas obras com total de produtos consumidos (para o gráfico)
@relatorio_bp.route("/obras-produtos", methods=["GET"])
@jwt.validate_token
def obras_produtos():
    sql = """
        SELECT o.idObra, o.descObra,
               COUNT(po.idProduto)            AS numProdutos,
               COALESCE(SUM(po.qtdProdutosObra), 0) AS totalConsumido
        FROM obras o
        LEFT JOIN produtosObras po ON o.idObra = po.idObra
        GROUP BY o.idObra, o.descObra
        ORDER BY o.idObra DESC
        LIMIT 10
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
                "idObra":         r[0],
                "descObra":       r[1],
                "numProdutos":    r[2],
                "totalConsumido": int(r[3]),
            }
            for r in rows
        ]
        return jsonify({"status": True, "dados": data}), 200
    except Exception as e:
        return jsonify({"status": False, "msg": str(e)}), 500
    finally:
        Conexao.fechar_conexao(conexao, cursor)


# ─── GET /relatorio/produtos-consumidos ───────────────────────────────────────
# Retorna total consumido por produto (para exportação)
@relatorio_bp.route("/produtos-consumidos", methods=["GET"])
@jwt.validate_token
def produtos_consumidos():
    sql = """
        SELECT p.idProduto, p.nomeProduto,
               COALESCE(SUM(po.qtdProdutosObra), 0) AS totalConsumido,
               p.qtdProduto AS estoqueAtual,
               p.qtdMinima
        FROM produtos p
        LEFT JOIN produtosObras po ON p.idProduto = po.idProduto
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
def grafico_produtos():
    sql = """
        SELECT p.idProduto, p.nomeProduto,
               o.idObra, o.descObra, c.nomeCliente,
               po.qtdProdutosObra
        FROM produtos p
        JOIN produtosObras po ON p.idProduto = po.idProduto
        JOIN obras o          ON o.idObra    = po.idObra
        LEFT JOIN clientes c  ON c.idCliente = o.codCliente
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
                "nomeCliente": r[4] or f"Cliente #{r[2]}",
                "qtd":         int(r[5]),
            })

        data = sorted(produtos.values(), key=lambda x: x["totalConsumido"], reverse=True)
        return jsonify({"status": True, "dados": data}), 200
    except Exception as e:
        return jsonify({"status": False, "msg": str(e)}), 500
    finally:
        Conexao.fechar_conexao(conexao, cursor)
