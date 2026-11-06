#!/usr/bin/env python3
"""
System Medic - Basic Health Check Script for Claudebot
Checks: Ollama, Playwright chromium, .env files
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def check_ollama():
    """Check if Ollama is running."""
    result = {"status": "unknown", "version": None, "last_check": datetime.now().isoformat()}
    
    try:
        proc = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            timeout=5
        )
        if proc.returncode == 0:
            data = json.loads(proc.stdout.decode()) if proc.stdout else {}
            result["status"] = "running"
            result["version"] = data.get("models", [{}])[0].get("name", "unknown") if data.get("models") else "unknown"
        else:
            result["status"] = "stopped"
    except FileNotFoundError:
        result["status"] = "not_installed"
    except subprocess.TimeoutExpired:
        result["status"] = "not_responding"
    except Exception as e:
        result["status"] = f"error: {str(e)}"
    
    return result


def check_playwright():
    """Check if Playwright chromium is installed."""
    result = {"chromium": "unknown", "last_install": None}
    
    try:
        proc = subprocess.run(
            [sys.executable, "-c", 
             "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(); b.close(); p.stop()"],
            capture_output=True,
            timeout=30
        )
        if proc.returncode == 0:
            result["chromium"] = "installed"
        else:
            result["chromium"] = "missing"
    except Exception as e:
        result["chromium"] = f"error: {str(e)}"
    
    return result


def check_env():
    """Check if .env files are present."""
    required_files = [".env", "credentials.json"]
    result = {}
    
    for f in required_files:
        path = Path(f)
        result[f] = "present" if path.exists() else "missing"
    
    return result


def fix_ollama():
    """Restart Ollama."""
    print("[System Medic] Restarting Ollama...")
    
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        print("[System Medic] Ollama restart command sent.")
        return True
    except Exception as e:
        print(f"[System Medic] Failed to restart Ollama: {e}")
        return False


def fix_playwright():
    """Install Playwright chromium."""
    print("[System Medic] Installing Chromium for Playwright...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True
        )
        print("[System Medic] Chromium installed successfully.")
        return True
    except Exception as e:
        print(f"[System Medic] Failed to install Chromium: {e}")
        return False


def fix_env():
    """Report missing .env files."""
    missing = []
    for f in [".env", "credentials.json"]:
        if not Path(f).exists():
            missing.append(f)
    
    if missing:
        print(f"[System Medic] Missing files: {', '.join(missing)}")
        print("[System Medic] Please create these files manually or from .env.example template.")
    else:
        print("[System Medic] All .env files present.")
    
    return len(missing) == 0


def full_status():
    """Run all checks and print status."""
    print("=" * 50)
    print("SYSTEM MEDIC - Health Check Report")
    print("=" * 50)
    
    print("\n[1/3] Checking Ollama...")
    ollama = check_ollama()
    print(f"    Status: {ollama['status']}")
    
    print("\n[2/3] Checking Playwright...")
    pw = check_playwright()
    print(f"    Chromium: {pw['chromium']}")
    
    print("\n[3/3] Checking .env files...")
    env = check_env()
    for k, v in env.items():
        print(f"    {k}: {v}")
    
    print("\n" + "=" * 50)


def main():
    if len(sys.argv) < 2:
        full_status()
        sys.exit(0)
    
    command = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command == "check":
        if target == "ollama" or not target:
            print(json.dumps(check_ollama(), indent=2))
        elif target == "playwright":
            print(json.dumps(check_playwright(), indent=2))
        elif target == "env":
            print(json.dumps(check_env(), indent=2))
        elif target == "all":
            full_status()
    
    elif command == "fix":
        if target == "ollama":
            fix_ollama()
        elif target == "playwright":
            fix_playwright()
        elif target == "env":
            fix_env()
    
    elif command == "repair":
        print("[System Medic] Running auto-repair...")
        fix_ollama()
        fix_playwright()
        fix_env()
    
    elif command == "status":
        full_status()
    
    else:
        print(f"Unknown command: {command}")
        print("Usage: python medic.py [check|fix|repair|status] [ollama|playwright|env|all]")
        sys.exit(1)


if __name__ == "__main__":
    main()