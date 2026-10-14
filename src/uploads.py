"""Arquivos enviados pelos usuários (fotos de obra/produto e notas fiscais).
O conteúdo vai para o banco em base64, junto com o tipo MIME, e é servido em
/uploads/<nome>, onde <nome> é um identificador aleatório gravado na linha."""
import base64
import uuid
from flask import request
from src.error_response import ErrorResponse

EXT_IMAGEM = {"jpg", "jpeg", "png", "gif", "webp"}

TIPOS_MIME = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "gif": "image/gif",  "webp": "image/webp", "pdf": "application/pdf",
}


def ler_arquivo_da_requisicao(extensoes: set) -> dict:
    """Valida o campo 'arquivo' do formulário e devolve
    {nomeArquivo, nomeOriginal, tipoMime, conteudo (base64)}."""
    arquivo = request.files.get("arquivo")
    if arquivo is None:
        raise ErrorResponse(400, "Nenhum arquivo enviado.", {"message": "Campo 'arquivo' ausente."})
    if not arquivo.filename:
        raise ErrorResponse(400, "Arquivo inválido.", {"message": "Nome de arquivo vazio."})

    ext = arquivo.filename.rsplit(".", 1)[1].lower() if "." in arquivo.filename else ""
    if ext not in extensoes:
        permitidos = ", ".join(sorted(e.upper() for e in extensoes))
        raise ErrorResponse(400, "Tipo de arquivo não permitido.", {"message": f"Permitidos: {permitidos}."})

    dados = arquivo.read()
    if not dados:
        raise ErrorResponse(400, "Arquivo inválido.", {"message": "O arquivo está vazio."})

    # Nome aleatório: é ele que vai na URL, então não dá para adivinhá-la.
    return {
        "nomeArquivo":  f"{uuid.uuid4().hex}.{ext}",
        "nomeOriginal": arquivo.filename,
        "tipoMime":     TIPOS_MIME.get(ext, "application/octet-stream"),
        "conteudo":     base64.b64encode(dados).decode("ascii"),
    }
