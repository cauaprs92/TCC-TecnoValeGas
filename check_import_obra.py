import sys, os, traceback
root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root)
try:
    from src.routers.obraRoteador import obra_bp
    print('import ok')
except Exception:
    traceback.print_exc()
