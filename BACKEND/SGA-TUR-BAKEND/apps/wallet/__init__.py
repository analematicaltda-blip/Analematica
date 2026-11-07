"""Compatibility import path; canonical wallet code is in WALLET-BACKEND."""
from pathlib import Path
__path__=[str(Path(__file__).resolve().parents[4]/'WALLET-BACKEND/apps/wallet')]
