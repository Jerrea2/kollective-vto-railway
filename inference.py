import os, sys, importlib.util
from fastapi import FastAPI

# This file is only a shim. It loads the real IDM-VTON backend from
# src/Kollective-vto2/inference.py and exposes its FastAPI 'app' here.

HERE = os.path.abspath(os.path.dirname(__file__))
BACKEND_PATH = os.path.join(HERE, "src", "Kollective-vto2", "inference.py")

spec = importlib.util.spec_from_file_location("kollective_vto2_backend", BACKEND_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

app: FastAPI = mod.app
