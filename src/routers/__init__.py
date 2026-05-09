from .clienteRoteador import cliente_bp
from .produtoRoteador import produto_bp
from .obraRoteador    import obra_bp
from .loginRoteador   import login_bp
from .adminRoteador   import admin_bp

__all__ = [
    "cliente_bp",
    "produto_bp",
    "obra_bp",
    "login_bp",
    "admin_bp",
]