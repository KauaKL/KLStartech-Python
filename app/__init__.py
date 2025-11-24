# =====================================================
# 🚀 __init__.py — Pacote Principal DashFin Supremo
# by KLStarTech (Kauã Lima) + DeepSeek AI
# =====================================================

"""
💹 DashFin Supremo - Sistema de Inteligência Financeira Avançada

Módulos Principais:
- 🤖 estelar.py: Assistente virtual com Live2D e voz
- 📊 crm_dashboard.py: Sistema de Gestão de Clientes
- 📧 email_utils.py: Sistema de e-mails profissionais  
- 📊 data_utils.py: Análise de dados e previsões
- 🤖 automation.py: Automação inteligente
- 🎨 main.py: Interface Streamlit principal

Versão: 3.0 Suprema
Desenvolvido por: KLStarTech (Kauã Lima)
Otimizado por: DeepSeek AI
"""

__version__ = "3.0.0"
__author__ = "KLStarTech (Kauã Lima)"
__email__ = "kaua@klstartech.com"
__description__ = "Sistema de inteligência financeira com IA assistente"

# =====================================================
# 🌟 IMPORTAÇÕES PRINCIPAIS - CRM PRIMEIRO!
# =====================================================

# ✅ 1. PRIMEIRO: Importar CRM 
try:
    from crm_dashboard import (
        display_crm_dashboard,
        get_crm_metrics_summary
    )
    CRM_AVAILABLE = True
except ImportError as e:
    CRM_AVAILABLE = False
    print(f"⚠️ Módulo CRM não disponível: {e}")

    # Fallbacks para CRM
    def display_crm_dashboard():
        import streamlit as st
        st.error("📊 Dashboard CRM não disponível - Verifique app/crm_dashboard.py")
    
    def get_crm_metrics_summary():
        return {
            'ticket_volume': 0,
            'response_time': 0,
            'satisfaction': 0,
            'revenue': 0
        }

# ✅ 2. DEPOIS: Outros módulos
try:
    from app.estelar import (
        voz_boas_vindas,
        exibir_estelar_ui,
        responder_estelar
    )
except ImportError:
    # Fallback para desenvolvimento
    def voz_boas_vindas():
        print("🔊 Estelar: Sistema de voz não disponível")
    
    def exibir_estelar_ui():
        print("🤖 Interface Estelar: Módulo não disponível")
    
    def responder_estelar(msg, use_ai=False):
        return "Sistema Estelar temporariamente indisponível"

try:
    from app.email_utils import (
        send_email_alert,
        send_email_with_attachments,
        send_financial_report,
        EmailNotifier
    )
except ImportError:
    # Fallbacks para email_utils
    def send_email_alert(*args, **kwargs):
        print("📧 Sistema de e-mail não disponível")
        return False, "Módulo de e-mail não disponível"
    
    def send_email_with_attachments(*args, **kwargs):
        return False, "Módulo de e-mail não disponível"
    
    def send_financial_report(*args, **kwargs):
        return False, "Módulo de e-mail não disponível"
    
    class EmailNotifier:
        def send_alert(self, *args, **kwargs):
            return False

try:
    from app.data_utils import (
        pegar_dados_cache,
        gerar_previsao_prophet,
        calcular_indicadores_tecnicos,
        gerar_relatorio_completo,
        gerar_pdf_cache,
        gerar_excel_cache
    )
except ImportError:
    # Fallbacks para data_utils
    import pandas as pd
    
    def pegar_dados_cache(*args, **kwargs):
        print("📊 Módulo de dados não disponível")
        return pd.DataFrame()
    
    def gerar_previsao_prophet(*args, **kwargs):
        return pd.DataFrame()
    
    def calcular_indicadores_tecnicos(*args, **kwargs):
        return {}
    
    def gerar_relatorio_completo(*args, **kwargs):
        return {}
    
    def gerar_pdf_cache(*args, **kwargs):
        return b""
    
    def gerar_excel_cache(*args, **kwargs):
        return b""

try:
    from app.automation import (
        can_send_alert,
        mark_alert_sent,
        get_alert_history,
        iniciar_automacao,
        parar_automacao,
        criar_sistema_automacao,
        AutomationConfig
    )
except ImportError:
    # Fallbacks para automation
    def can_send_alert(*args, **kwargs):
        return True
    
    def mark_alert_sent(*args, **kwargs):
        print("🔔 Alerta registrado (modo fallback)")
    
    def get_alert_history():
        return []
    
    def iniciar_automacao(*args, **kwargs):
        print("🤖 Automação não disponível")
    
    def parar_automacao():
        print("🛑 Automação parada (modo fallback)")
    
    def criar_sistema_automacao(*args, **kwargs):
        return None
    
    class AutomationConfig:
        pass

# =====================================================
# 🎯 CONFIGURAÇÃO DO PACOTE
# =====================================================

# Variáveis globais de configuração
CONFIG = {
    "version": __version__,
    "debug_mode": False,
    "max_cache_size": 1000,
    "supported_currencies": ["USD", "EUR", "BTC", "ETH", "ADA"],
    "default_avatar": "hologram.gif",
    "update_channel": "stable",
    "crm_available": CRM_AVAILABLE
}

def get_version():
    """Retorna a versão do pacote"""
    return __version__

def get_supported_currencies():
    """Retorna lista de moedas suportadas"""
    return CONFIG["supported_currencies"]

def set_debug_mode(enabled: bool):
    """Ativa/desativa modo debug"""
    CONFIG["debug_mode"] = enabled
    print(f"🔧 Modo debug {'ativado' if enabled else 'desativado'}")

def get_config():
    """Retorna configuração atual"""
    return CONFIG.copy()

# =====================================================
# 🔧 UTILITÁRIOS DO PACOTE
# =====================================================

def check_dependencies():
    """
    Verifica se todas as dependências estão disponíveis
    Retorna dict com status de cada módulo
    """
    dependencies = {
        "streamlit": False,
        "pandas": False,
        "plotly": False,
        "prophet": False,
        "fpdf": False,
        "xlsxwriter": False,
        "speechrecognition": False,
        "pyttsx3": False
    }
    
    try:
        import streamlit
        dependencies["streamlit"] = True
    except ImportError:
        pass
        
    try:
        import pandas
        dependencies["pandas"] = True
    except ImportError:
        pass
        
    try:
        import plotly
        dependencies["plotly"] = True
    except ImportError:
        pass
        
    try:
        from prophet import Prophet
        dependencies["prophet"] = True
    except ImportError:
        pass
        
    try:
        from fpdf import FPDF
        dependencies["fpdf"] = True
    except ImportError:
        pass
        
    try:
        import xlsxwriter
        dependencies["xlsxwriter"] = True
    except ImportError:
        pass
        
    try:
        import speech_recognition
        dependencies["speechrecognition"] = True
    except ImportError:
        pass
        
    try:
        import pyttsx3
        dependencies["pyttsx3"] = True
    except ImportError:
        pass
    
    return dependencies

def system_status():
    """
    Retorna status completo do sistema
    """
    deps = check_dependencies()
    
    status = {
        "version": __version__,
        "dependencies": deps,
        "modules_available": {
            "estelar": "voz_boas_vindas" in globals(),
            "crm": CRM_AVAILABLE,
            "email_utils": "send_email_alert" in globals(),
            "data_utils": "pegar_dados_cache" in globals(),
            "automation": "can_send_alert" in globals()
        },
        "config": CONFIG
    }
    
    return status

# =====================================================
# 🎪 INICIALIZAÇÃO DO PACOTE
# =====================================================

# Mensagem de inicialização (apenas na primeira importação)
print(f"""
💹 DashFin Supremo v{__version__}
===============================

Sistema de inteligência financeira com assistente IA
Desenvolvido por {__author__}

Módulos carregados:
🤖 Estelar Assistant
📊 CRM Avançado {'✅' if CRM_AVAILABLE else '❌'}
📧 Sistema de E-mails  
📊 Análise de Dados
🤖 Automação Inteligente

Digite `app.system_status()` para verificar o sistema.
""")

# =====================================================
# 🧪 TESTE RÁPIDO (quando executado diretamente)
# =====================================================

if __name__ == "__main__":
    print("🧪 TESTE DO PACOTE DASHFIN SUPREMO")
    print("=" * 40)
    
    # Verificar status do sistema
    status = system_status()
    print("📋 Status do Sistema:")
    for key, value in status.items():
        if key == "dependencies":
            print("  📦 Dependências:")
            for dep, available in value.items():
                print(f"    {'✅' if available else '❌'} {dep}")
        elif key == "modules_available":
            print("  🗂️ Módulos:")
            for module, available in value.items():
                print(f"    {'✅' if available else '❌'} {module}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n🚀 Sistema pronto! Versão {__version__}")