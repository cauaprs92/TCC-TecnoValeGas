"""Arquivos enviados pelos usuários (fotos de obra/produto e notas fiscais),
gravados em uploads/ com nome aleatório e servidos em /uploads/<nome>."""
import os
import uuid
from flask import request
from src.error_response import ErrorResponse

UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))

EXT_IMAGEM = {"jpg", "jpeg", "png", "gif", "webp"}


def salvar_arquivo_da_requisicao(extensoes: set) -> tuple:
    """Valida e grava o campo 'arquivo' do formulário.
    Retorna (nome gravado em disco, nome original do arquivo)."""
    arquivo = request.files.get("arquivo")
    if arquivo is None:
        raise ErrorResponse(400, "Nenhum arquivo enviado.", {"message": "Campo 'arquivo' ausente."})
    if not arquivo.filename:
        raise ErrorResponse(400, "Arquivo inválido.", {"message": "Nome de arquivo vazio."})

    ext = arquivo.filename.rsplit(".", 1)[1].lower() if "." in arquivo.filename else ""
    if ext not in extensoes:
        permitidos = ", ".join(sorted(e.upper() for e in extensoes))
        raise ErrorResponse(400, "Tipo de arquivo não permitido.", {"message": f"Permitidos: {permitidos}."})

    # Nome aleatório: não dá para adivinhar a URL nem sobrescrever outro arquivo.
    nome = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    arquivo.save(os.path.join(UPLOADS_DIR, nome))
    return nome, arquivo.filename


def apagar_arquivos(*nomes):
    for nome in nomes:
        caminho = os.path.join(UPLOADS_DIR, os.path.basename(nome))
        if os.path.exists(caminho):
            os.remove(caminho)
