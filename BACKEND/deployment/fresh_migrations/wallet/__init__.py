"""Compatibility import path; canonical wallet code is in BACKEND/WALLET-BACKEND."""
from pathlib import Path
__path__=[str(Path(__file__).resolve().parents[4]/'BACKEND/WALLET-BACKEND/fresh_migrations/wallet')]
