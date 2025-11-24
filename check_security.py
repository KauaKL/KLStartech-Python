#!/usr/bin/env python3
"""
🛡️ check_security.py — Verificador de Segurança Git
Verifica se não há arquivos sensíveis no repositório
"""

import os
import subprocess
from pathlib import Path

def check_git_security():
    print("🛡️  VERIFICAÇÃO DE SEGURANÇA GIT")
    print("=" * 50)
    
    # Verificar se é um repositório git
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Não é um repositório Git")
        return
    
    # Verificar por arquivos sensíveis
    sensitive_files = [
        '.env',
        'config_secret.py',
        'keys.json',
        'credentials/',
        'secrets/'
    ]
    
    print("\n🔍 Verificando arquivos sensíveis...")
    
    for file in sensitive_files:
        if Path(file).exists():
            print(f"🚨 ALERTA: {file} existe localmente!")
            print("   💡 Certifique-se de que está no .gitignore")
    
    # Verificar git status
    print("\n📊 Status do Git:")
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    
    if result.stdout:
        print("Arquivos modificados/novos:")
        for line in result.stdout.strip().split('\n'):
            status = line[:2]
            filename = line[3:]
            
            if any(sensitive in filename for sensitive in ['.env', 'secret', 'key', 'password']):
                print(f"   🚨 {status} {filename} → POTENCIALMENTE SENSÍVEL!")
            else:
                print(f"   📄 {status} {filename}")
    else:
        print("✅ Nenhuma modificação pendente")
    
    # Verificar .gitignore
    print("\n📋 Verificando .gitignore...")
    if Path('.gitignore').exists():
        with open('.gitignore', 'r') as f:
            content = f.read()
        
        required_patterns = ['.env', '__pycache__', '*.pyc', 'storage/', 'reports/']
        missing = [pattern for pattern in required_patterns if pattern not in content]
        
        if missing:
            print("❌ Padrões faltando no .gitignore:")
            for pattern in missing:
                print(f"   - {pattern}")
        else:
            print("✅ .gitignore parece completo")
    else:
        print("❌ .gitignore não encontrado!")

if __name__ == "__main__":
    check_git_security()