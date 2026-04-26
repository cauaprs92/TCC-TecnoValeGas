import sys
from unittest.mock import MagicMock 

# ── Mock do mysql ANTES de qualquer import do projeto ────────────────────────
sys.modules['mysql']           = MagicMock()
sys.modules['mysql.connector'] = MagicMock()

import io
import json
import unittest
from unittest.mock import patch

from flask import Flask, jsonify
from src.error_response import ErrorResponse


def _token_valido(f):
    """Substitui @jwt.validate_token: sempre deixa passar."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def _build_app():
    """
    Cria uma instância Flask com todos os blueprints registrados,
    aplicando patch no JWT para não validar token de verdade.
    """
    with patch("src.middleware.jwtMiddleware.JwtMiddleware.validate_token",
               side_effect=_token_valido):

        from src.routers.loginRoteador   import login_bp
        from src.routers.clienteRoteador import cliente_bp
        from src.routers.produtoRoteador import produto_bp
        from src.routers.obraRoteador    import obra_bp   # nome correto do arquivo

        app = Flask(__name__)
        app.register_blueprint(login_bp)
        app.register_blueprint(cliente_bp)
        app.register_blueprint(produto_bp)
        app.register_blueprint(obra_bp)

        @app.errorhandler(ErrorResponse)
        def handle_error(e):
            return jsonify({"status": False, "msg": e.args[0], "error": e.error}), e.httpCode

        app.config["TESTING"] = True
        return app


# ── Modelo fake (simula objetos retornados pelo DAO) ─────────────────────────

def _cliente_fake(id_=1):
    c = MagicMock()
    c._idCliente       = id_
    c._nomeCliente     = "Joao Silva"
    c._CNPJCPF         = "12345678900"
    c._enderecoCliente = "Rua das Flores, 100"
    c._contatoCliente  = "(11) 99999-9999"
    return c


def _produto_fake(id_=1):
    p = MagicMock()
    p._idProduto   = id_
    p._nomeProduto = "Cano PVC"
    p._qtdProduto  = 50
    p._descProduto = "Cano 6 metros"
    return p


TOKEN = "Bearer token_fake_para_testes"
HDR   = {"Authorization": TOKEN, "Content-Type": "application/json"}


# ════════════════════════════════════════════════════════════════════════════
# TESTES DE LOGIN
# ════════════════════════════════════════════════════════════════════════════

class TesteLoginRoteador(unittest.TestCase):

    def setUp(self):
        self.app    = _build_app()
        self.client = self.app.test_client()

    @patch("src.routers.loginRoteador.controller")
    def test_login_sucesso(self, mock_ctrl):
        """Login com credenciais válidas deve retornar 200 e um token."""
        mock_ctrl.autenticar.return_value = (True, "Administrador")

        resp  = self.client.post("/login",
                    data=json.dumps({"email": "adm123@gmail.com", "senha": "adm123"}),
                    headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(dados["status"])
        self.assertIn("token", dados)
        self.assertEqual(dados["nomeLogin"], "Administrador")
        print(f"  ✔ LOGIN correto          → {resp.status_code} | {dados['msg']}")

    @patch("src.routers.loginRoteador.controller")
    def test_login_credenciais_erradas(self, mock_ctrl):
        """Login com senha errada deve retornar 401."""
        mock_ctrl.autenticar.return_value = (False, "Email ou senha incorretos.")

        resp  = self.client.post("/login",
                    data=json.dumps({"email": "adm123@gmail.com", "senha": "errada"}),
                    headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 401)
        self.assertFalse(dados["status"])
        print(f"  ✔ LOGIN senha errada     → {resp.status_code} | {dados['msg']}")

    def test_login_body_vazio(self):
        """Requisição sem body deve retornar 400."""
        resp = self.client.post("/login", data="{}", headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ LOGIN body vazio       → {resp.status_code}")

    def test_login_email_invalido(self):
        """Email sem @ deve retornar 400."""
        resp = self.client.post("/login",
                    data=json.dumps({"email": "emailinvalido", "senha": "adm123"}),
                    headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ LOGIN email inválido   → {resp.status_code}")

    def test_login_senha_curta(self):
        """Senha com menos de 6 caracteres deve retornar 400."""
        resp = self.client.post("/login",
                    data=json.dumps({"email": "adm@adm.com", "senha": "123"}),
                    headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ LOGIN senha curta      → {resp.status_code}")


# ════════════════════════════════════════════════════════════════════════════
# TESTES DE CLIENTE
# ════════════════════════════════════════════════════════════════════════════

class TesteClienteRoteador(unittest.TestCase):

    def setUp(self):
        self.app    = _build_app()
        self.client = self.app.test_client()

    def _body_cliente(self, **kwargs):
        base = {
            "idCliente":       1,
            "nomeCliente":     "Joao Silva",
            "CNPJCPF":         "12345678900",
            "enderecoCliente": "Rua das Flores, 100",
            "contatoCliente":  "(11) 99999-9999",
        }
        base.update(kwargs)
        return json.dumps({"cliente": base})

    @patch("src.routers.clienteRoteador.controller")
    def test_cadastrar_sucesso(self, mock_ctrl):
        mock_ctrl.cadastrar.return_value = (True, "Cliente cadastrado com sucesso!")

        resp  = self.client.post("/cliente", data=self._body_cliente(), headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(dados["status"])
        print(f"  ✔ CLIENTE cadastrar ok   → {resp.status_code} | {dados['msg']}")

    @patch("src.routers.clienteRoteador.controller")
    def test_cadastrar_id_duplicado(self, mock_ctrl):
        mock_ctrl.cadastrar.return_value = (False, "Ja existe um cliente com o ID 1.")

        resp  = self.client.post("/cliente", data=self._body_cliente(), headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 400)
        self.assertFalse(dados["status"])
        print(f"  ✔ CLIENTE id duplicado   → {resp.status_code} | {dados['msg']}")

    def test_cadastrar_sem_nome(self):
        body = json.dumps({"cliente": {"idCliente": 2}})
        resp = self.client.post("/cliente", data=body, headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ CLIENTE sem nome       → {resp.status_code}")

    def test_cadastrar_body_vazio(self):
        resp = self.client.post("/cliente", data="{}", headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ CLIENTE body vazio     → {resp.status_code}")

    @patch("src.routers.clienteRoteador.controller")
    def test_listar(self, mock_ctrl):
        mock_ctrl.listar.return_value = [_cliente_fake(1), _cliente_fake(2)]

        resp  = self.client.get("/cliente", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(dados["clientes"]), 2)
        print(f"  ✔ CLIENTE listar         → {resp.status_code} | {len(dados['clientes'])} clientes")

    @patch("src.routers.clienteRoteador.controller")
    def test_listar_vazio(self, mock_ctrl):
        mock_ctrl.listar.return_value = []

        resp  = self.client.get("/cliente", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(dados["clientes"], [])
        print(f"  ✔ CLIENTE listar vazio   → {resp.status_code}")

    @patch("src.routers.clienteRoteador.controller")
    def test_buscar_por_id_encontrado(self, mock_ctrl):
        mock_ctrl.buscar_por_id.return_value = _cliente_fake(1)

        resp  = self.client.get("/cliente/1", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(dados["cliente"]["idCliente"], 1)
        print(f"  ✔ CLIENTE buscar id=1    → {resp.status_code}")

    @patch("src.routers.clienteRoteador.controller")
    def test_buscar_por_id_nao_encontrado(self, mock_ctrl):
        mock_ctrl.buscar_por_id.return_value = None

        resp = self.client.get("/cliente/999", headers=HDR)
        self.assertEqual(resp.status_code, 404)
        print(f"  ✔ CLIENTE buscar id=999  → {resp.status_code}")

    @patch("src.routers.clienteRoteador.controller")
    def test_editar_sucesso(self, mock_ctrl):
        mock_ctrl.editar.return_value = (True, "Cliente atualizado com sucesso!")

        resp = self.client.put("/cliente/1", data=self._body_cliente(), headers=HDR)
        self.assertEqual(resp.status_code, 200)
        print(f"  ✔ CLIENTE editar ok      → {resp.status_code}")

    @patch("src.routers.clienteRoteador.controller")
    def test_editar_falha(self, mock_ctrl):
        mock_ctrl.editar.return_value = (False, "Erro ao atualizar cliente.")

        resp = self.client.put("/cliente/1", data=self._body_cliente(), headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ CLIENTE editar falha   → {resp.status_code}")

    @patch("src.routers.clienteRoteador.controller")
    def test_deletar_sucesso(self, mock_ctrl):
        mock_ctrl.deletar.return_value = (True, "Cliente deletado com sucesso!")

        resp = self.client.delete("/cliente/1", headers=HDR)
        self.assertEqual(resp.status_code, 200)
        print(f"  ✔ CLIENTE deletar ok     → {resp.status_code}")

    @patch("src.routers.clienteRoteador.controller")
    def test_deletar_nao_encontrado(self, mock_ctrl):
        mock_ctrl.deletar.return_value = (False, "Cliente nao encontrado.")

        resp = self.client.delete("/cliente/99", headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ CLIENTE deletar 404    → {resp.status_code}")


# ════════════════════════════════════════════════════════════════════════════
# TESTES DE PRODUTO
# ════════════════════════════════════════════════════════════════════════════

class TesteProdutoRoteador(unittest.TestCase):

    def setUp(self):
        self.app    = _build_app()
        self.client = self.app.test_client()

    def _body_produto(self, **kwargs):
        base = {
            "idProduto":   1,
            "nomeProduto": "Cano PVC",
            "qtdProduto":  50,
            "descProduto": "Cano 6 metros",
        }
        base.update(kwargs)
        return json.dumps({"produto": base})

    @patch("src.routers.produtoRoteador.controller")
    def test_cadastrar_sucesso(self, mock_ctrl):
        mock_ctrl.cadastrar.return_value = (True, "Produto cadastrado com sucesso!", None)

        resp  = self.client.post("/produto", data=self._body_produto(), headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(dados["status"])
        print(f"  ✔ PRODUTO cadastrar ok   → {resp.status_code} | {dados['msg']}")

    @patch("src.routers.produtoRoteador.controller")
    def test_cadastrar_com_aviso_estoque(self, mock_ctrl):
        aviso = "ATENCAO: Estoque de 'Valvula' esta muito baixo (3 unidades)."
        mock_ctrl.cadastrar.return_value = (True, "Produto cadastrado com sucesso!", aviso)

        resp  = self.client.post("/produto",
                    data=self._body_produto(nomeProduto="Valvula", qtdProduto=3),
                    headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 201)
        self.assertIn("aviso", dados)
        print(f"  ✔ PRODUTO aviso estoque  → {resp.status_code} | aviso: {dados['aviso'][:40]}...")

    def test_cadastrar_nome_com_numero(self):
        resp = self.client.post("/produto",
                    data=json.dumps({"produto": {"nomeProduto": "Cano2", "qtdProduto": 10, "descProduto": ""}}),
                    headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ PRODUTO nome c/ nro    → {resp.status_code}")

    def test_cadastrar_quantidade_negativa(self):
        resp = self.client.post("/produto",
                    data=json.dumps({"produto": {"nomeProduto": "Cano PVC", "qtdProduto": -1, "descProduto": ""}}),
                    headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ PRODUTO qtd negativa   → {resp.status_code}")

    def test_cadastrar_quantidade_acima_max(self):
        resp = self.client.post("/produto",
                    data=json.dumps({"produto": {"nomeProduto": "Cano PVC", "qtdProduto": 10000, "descProduto": ""}}),
                    headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ PRODUTO qtd acima max  → {resp.status_code}")

    @patch("src.routers.produtoRoteador.controller")
    def test_listar(self, mock_ctrl):
        mock_ctrl.listar.return_value = [_produto_fake(1), _produto_fake(2), _produto_fake(3)]

        resp  = self.client.get("/produto", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(dados["produtos"]), 3)
        print(f"  ✔ PRODUTO listar         → {resp.status_code} | {len(dados['produtos'])} produtos")

    @patch("src.routers.produtoRoteador.controller")
    def test_buscar_por_id_encontrado(self, mock_ctrl):
        mock_ctrl.buscar_por_id.return_value = _produto_fake(1)

        resp  = self.client.get("/produto/1", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(dados["produto"]["idProduto"], 1)
        print(f"  ✔ PRODUTO buscar id=1    → {resp.status_code}")

    @patch("src.routers.produtoRoteador.controller")
    def test_buscar_por_id_nao_encontrado(self, mock_ctrl):
        mock_ctrl.buscar_por_id.return_value = None

        resp = self.client.get("/produto/999", headers=HDR)
        self.assertEqual(resp.status_code, 404)
        print(f"  ✔ PRODUTO buscar id=999  → {resp.status_code}")

    @patch("src.routers.produtoRoteador.controller")
    def test_verificar_estoque_ok(self, mock_ctrl):
        mock_ctrl.buscar_por_id.return_value     = _produto_fake(1)
        mock_ctrl.verificar_estoque.return_value = (True, "Estoque disponivel.")

        resp  = self.client.get("/produto/1/estoque?quantidade=5", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(dados["status"])
        print(f"  ✔ PRODUTO estoque ok     → {resp.status_code} | {dados['msg']}")

    @patch("src.routers.produtoRoteador.controller")
    def test_verificar_estoque_insuficiente(self, mock_ctrl):
        mock_ctrl.buscar_por_id.return_value     = _produto_fake(1)
        mock_ctrl.verificar_estoque.return_value = (False, "Estoque insuficiente para 'Cano PVC'.")

        resp = self.client.get("/produto/1/estoque?quantidade=9999", headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ PRODUTO estoque insuf. → {resp.status_code}")

    @patch("src.routers.produtoRoteador.controller")
    def test_editar_sucesso(self, mock_ctrl):
        mock_ctrl.editar.return_value = (True, "Produto atualizado com sucesso!", None)

        resp = self.client.put("/produto/1", data=self._body_produto(), headers=HDR)
        self.assertEqual(resp.status_code, 200)
        print(f"  ✔ PRODUTO editar ok      → {resp.status_code}")

    @patch("src.routers.produtoRoteador.controller")
    def test_deletar_sucesso(self, mock_ctrl):
        mock_ctrl.deletar.return_value = (True, "Produto deletado com sucesso!", None)

        resp = self.client.delete("/produto/1", headers=HDR)
        self.assertEqual(resp.status_code, 200)
        print(f"  ✔ PRODUTO deletar ok     → {resp.status_code}")

    @patch("src.routers.produtoRoteador.controller")
    def test_deletar_vinculado_obra(self, mock_ctrl):
        mock_ctrl.deletar.return_value = (
            False, "Erro ao deletar produto. Verifique se ele nao esta vinculado a uma obra.", None
        )
        resp = self.client.delete("/produto/1", headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ PRODUTO deletar vinc.  → {resp.status_code}")


# ════════════════════════════════════════════════════════════════════════════
# TESTES DE OBRA
# ════════════════════════════════════════════════════════════════════════════

class TesteObraRoteador(unittest.TestCase):

    def setUp(self):
        self.app    = _build_app()
        self.client = self.app.test_client()

    def _body_obra(self, **kwargs):
        base_obra = {
            "codCliente": 1,
            "descObra":   "Instalacao de gas residencial",
            "dataObra":   "2026-03-14",
            "statusObra": "Em andamento",
            "respObra":   "Carlos",
        }
        base_obra.update(kwargs)
        return json.dumps({
            "obra": base_obra,
            "produtosUsados": [
                {"idProduto": 1, "quantidade": 5},
                {"idProduto": 2, "quantidade": 2},
            ],
        })

    def _obra_tuple(self, id_=1):
        return (id_, 1, "Instalacao de gas", "2026-03-14", "Em andamento", "Carlos")

    @patch("src.routers.obraRoteador.controller")
    def test_cadastrar_sucesso(self, mock_ctrl):
        mock_ctrl.cadastrar.return_value = (True, "Obra cadastrada com sucesso!")

        resp  = self.client.post("/obra", data=self._body_obra(), headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(dados["status"])
        print(f"  ✔ OBRA cadastrar ok      → {resp.status_code} | {dados['msg']}")

    @patch("src.routers.obraRoteador.controller")
    def test_cadastrar_cliente_inexistente(self, mock_ctrl):
        mock_ctrl.cadastrar.return_value = (False, "Cliente nao encontrado.")

        resp = self.client.post("/obra", data=self._body_obra(codCliente=999), headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ OBRA cliente inexist.  → {resp.status_code}")

    def test_cadastrar_status_invalido(self):
        resp = self.client.post("/obra", data=self._body_obra(statusObra="Voando"), headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ OBRA status inválido   → {resp.status_code}")

    def test_cadastrar_data_invalida(self):
        resp = self.client.post("/obra", data=self._body_obra(dataObra="14/03/2026"), headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ OBRA data inválida     → {resp.status_code}")

    def test_cadastrar_sem_produtos(self):
        body = json.dumps({
            "obra": {
                "codCliente": 1, "descObra": "Teste", "dataObra": "2026-01-01",
                "statusObra": "Em andamento", "respObra": "Carlos",
            },
            "produtosUsados": [],
        })
        resp = self.client.post("/obra", data=body, headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ OBRA sem produtos      → {resp.status_code}")

    def test_cadastrar_sem_responsavel(self):
        resp = self.client.post("/obra", data=self._body_obra(respObra=""), headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ OBRA sem responsável   → {resp.status_code}")

    @patch("src.routers.obraRoteador.controller")
    def test_listar(self, mock_ctrl):
        mock_ctrl.listar.return_value = [self._obra_tuple(1), self._obra_tuple(2)]

        resp  = self.client.get("/obra", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(dados["obras"]), 2)
        print(f"  ✔ OBRA listar            → {resp.status_code} | {len(dados['obras'])} obras")

    @patch("src.routers.obraRoteador.controller")
    def test_buscar_por_id_encontrado(self, mock_ctrl):
        mock_ctrl.buscar_por_id.return_value = self._obra_tuple(1)

        resp  = self.client.get("/obra/1", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(dados["obra"]["idObra"], 1)
        print(f"  ✔ OBRA buscar id=1       → {resp.status_code}")

    @patch("src.routers.obraRoteador.controller")
    def test_buscar_por_id_nao_encontrado(self, mock_ctrl):
        mock_ctrl.buscar_por_id.return_value = None

        resp = self.client.get("/obra/999", headers=HDR)
        self.assertEqual(resp.status_code, 404)
        print(f"  ✔ OBRA buscar id=999     → {resp.status_code}")

    @patch("src.routers.obraRoteador.controller")
    def test_listar_por_cliente(self, mock_ctrl):
        mock_ctrl.listar_por_cliente.return_value = (True, "Obras do cliente Joao", [self._obra_tuple(1)])

        resp  = self.client.get("/obra/cliente/1", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(dados["obras"]), 1)
        print(f"  ✔ OBRA por cliente       → {resp.status_code} | {dados['msg']}")

    @patch("src.routers.obraRoteador.controller")
    def test_listar_por_cliente_inexistente(self, mock_ctrl):
        mock_ctrl.listar_por_cliente.return_value = (False, "Cliente nao encontrado.", [])

        resp = self.client.get("/obra/cliente/999", headers=HDR)
        self.assertEqual(resp.status_code, 404)
        print(f"  ✔ OBRA cliente inexist.  → {resp.status_code}")

    @patch("src.routers.obraRoteador.controller")
    def test_buscar_produtos_da_obra(self, mock_ctrl):
        mock_ctrl.buscar_por_id.return_value           = self._obra_tuple(1)
        mock_ctrl.buscar_produtos_da_obra.return_value = [
            {"nome": "Cano PVC", "quantidade": 5},
            {"nome": "Valvula",  "quantidade": 2},
        ]

        resp  = self.client.get("/obra/1/produtos", headers=HDR)
        dados = resp.get_json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(dados["produtos"]), 2)
        print(f"  ✔ OBRA produtos          → {resp.status_code} | {len(dados['produtos'])} itens")

    @patch("src.routers.obraRoteador.controller")
    def test_atualizar_status_valido(self, mock_ctrl):
        mock_ctrl.atualizar_status.return_value = (True, "Status atualizado com sucesso!")

        resp = self.client.patch("/obra/1/status",
                    data=json.dumps({"statusObra": "Concluida"}),
                    headers=HDR)
        self.assertEqual(resp.status_code, 200)
        print(f"  ✔ OBRA status válido     → {resp.status_code}")

    def test_atualizar_status_invalido(self):
        resp = self.client.patch("/obra/1/status",
                    data=json.dumps({"statusObra": "Inventado"}),
                    headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ OBRA status inválido   → {resp.status_code}")

    @patch("src.routers.obraRoteador.controller")
    def test_deletar_sucesso(self, mock_ctrl):
        mock_ctrl.deletar.return_value = (True, "Obra deletada com sucesso!")

        resp = self.client.delete("/obra/1", headers=HDR)
        self.assertEqual(resp.status_code, 200)
        print(f"  ✔ OBRA deletar ok        → {resp.status_code}")

    @patch("src.routers.obraRoteador.controller")
    def test_deletar_nao_encontrada(self, mock_ctrl):
        mock_ctrl.deletar.return_value = (False, "Obra nao encontrada.")

        resp = self.client.delete("/obra/99", headers=HDR)
        self.assertEqual(resp.status_code, 400)
        print(f"  ✔ OBRA deletar 404       → {resp.status_code}")


# ════════════════════════════════════════════════════════════════════════════
# RUNNER
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suites = [
        ("LOGIN",   loader.loadTestsFromTestCase(TesteLoginRoteador)),
        ("CLIENTE", loader.loadTestsFromTestCase(TesteClienteRoteador)),
        ("PRODUTO", loader.loadTestsFromTestCase(TesteProdutoRoteador)),
        ("OBRA",    loader.loadTestsFromTestCase(TesteObraRoteador)),
    ]

    total_ok = total_fail = total_err = 0

    for nome, suite in suites:
        print(f"\n{'═'*55}")
        print(f"  {nome}")
        print(f"{'═'*55}")
        resultado = unittest.TextTestRunner(verbosity=0, stream=io.StringIO()).run(suite)
        total_ok   += resultado.testsRun - len(resultado.failures) - len(resultado.errors)
        total_fail += len(resultado.failures)
        total_err  += len(resultado.errors)

        for falha in resultado.failures:
            print(f"  ✘ FALHOU: {falha[0]}\n    {falha[1].splitlines()[-1]}")
        for erro in resultado.errors:
            print(f"  ✘ ERRO:   {erro[0]}\n    {erro[1].splitlines()[-1]}")

    print(f"\n{'─'*55}")
    print(f"  Resultado final → ✔ {total_ok} ok | ✘ {total_fail} falhas | ⚠ {total_err} erros")
    print(f"{'─'*55}\n")