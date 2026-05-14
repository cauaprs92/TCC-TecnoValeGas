import os
import sys
import traceback
from flask import Flask, jsonify, send_from_directory, abort
from flask_cors import CORS
from werkzeug.exceptions import NotFound

_raw_origins    = os.getenv("ALLOWED_ORIGINS", "http://localhost:5000,http://127.0.0.1:5000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.error_response import ErrorResponse
from src.routers import cliente_bp, produto_bp, obra_bp, login_bp, admin_bp, responsavel_bp, relatorio_bp

STATIC_DIR  = os.path.join(BASE_DIR, "view")
IMAGES_DIR  = os.path.join(BASE_DIR, "images")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

# ─── CORS — restringe às origens permitidas ──────────────────────────────────
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

# ─── Registro dos Blueprints ──────────────────────────────────────────────────
app.register_blueprint(login_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(obra_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(responsavel_bp)
app.register_blueprint(relatorio_bp)


# ─── Servir o frontend ────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Redireciona para a tela de login."""
    return send_from_directory(STATIC_DIR, "login.html")

@app.route("/images/<path:filename>")
def serve_image(filename):
    """Serve imagens da pasta /images na raiz do projeto."""
    return send_from_directory(IMAGES_DIR, filename)


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