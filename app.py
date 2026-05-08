import os
import sys
import traceback
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import NotFound

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.error_response import ErrorResponse
from src.routers import cliente_bp, produto_bp, obra_bp, login_bp

STATIC_DIR = os.path.join(BASE_DIR, "view")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

# ─── CORS — permite requisições do frontend ───────────────────────────────────
CORS(app, resources={r"/*": {"origins": "*"}})

# ─── Registro dos Blueprints ──────────────────────────────────────────────────
app.register_blueprint(login_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(obra_bp)


# ─── Servir o frontend ────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Redireciona para a tela de login."""
    return send_from_directory(STATIC_DIR, "login.html")

@app.route("/dashboard")
def dashboard():
    """Serve a página principal do sistema."""
    return send_from_directory(STATIC_DIR, "index.html")


# ─── Tratamento global de ErrorResponse ──────────────────────────────────────
@app.errorhandler(ErrorResponse)
def handle_error_response(e: ErrorResponse):
    stack_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
    return jsonify({
        "status": False,
        "msg":    e.args[0],
        "error":  e.error,
        "stack":  stack_str,
    }), e.httpCode


# ─── Tratamento global de erros inesperados ───────────────────────────────────
@app.errorhandler(Exception)
def handle_generic_error(e: Exception):
    if isinstance(e, NotFound):
        return jsonify({
            "status": False,
            "msg":    "Recurso não encontrado.",
            "error":  str(e),
        }), 404

    stack_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
    print("🟡 handle_generic_error:", e)
    return jsonify({
        "status": False,
        "msg":    "Erro interno no servidor.",
        "error":  str(e),
        "stack":  stack_str,
    }), 500


if __name__ == "__main__":
    print("🚀 Servidor rodando em: http://127.0.0.1:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)