# =====================================================
# 📧 email_utils.py — VERSÃO OTIMIZADA
# =====================================================

import os
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from datetime import datetime
import logging
from typing import List, Tuple, Optional, Dict, Any
import ssl
from dataclasses import dataclass

# =====================================================
# 🏗️ Estruturas de Dados
# =====================================================
@dataclass
class EmailConfig:
    """Configuração centralizada de e-mail"""
    host: str = os.getenv("ALERT_EMAIL_HOST", "smtp.gmail.com")
    port: int = int(os.getenv("ALERT_EMAIL_PORT", "587"))
    user: str = os.getenv("ALERT_EMAIL_USER")
    password: str = os.getenv("ALERT_EMAIL_PASS")
    default_to: str = os.getenv("ALERT_EMAIL_TO")
    timeout: int = 30
    use_tls: bool = True

@dataclass
class EmailResult:
    """Resultado padronizado do envio"""
    success: bool
    message: str
    recipient: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# =====================================================
# ⚙️ Configuração Avançada
# =====================================================
load_dotenv()

# Config singleton
EMAIL_CONFIG = EmailConfig()

# Logging profissional
logger = logging.getLogger("KLStarTech_Email")

class EmailTemplate:
    """Templates HTML reutilizáveis"""
    
    @staticmethod
    def financial_report(subject: str, data: Dict[str, Any]) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         padding: 30px; color: white; text-align: center; }}
                .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                              gap: 15px; padding: 20px; }}
                .metric-card {{ background: white; padding: 20px; border-radius: 10px; 
                              box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 4px solid #667eea; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; 
                         color: #6c757d; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>💹 DashFin Supremo</h1>
                <h2>{subject}</h2>
            </div>
            <div class="metric-grid">
                {''.join([f'<div class="metric-card"><h3>{k}</h3><p style="font-size: 24px; margin: 10px 0; color: #28a745;">{v}</p></div>' 
                         for k, v in data.items()])}
            </div>
            <div class="footer">
                Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • KLStarTech
            </div>
        </body>
        </html>
        """

# =====================================================
# 🔌 Conexão SMTP com Pool
# =====================================================
class SMTPConnectionPool:
    """Pool de conexões SMTP para melhor performance"""
    
    _connections = []
    
    @classmethod
    def get_connection(cls) -> Optional[smtplib.SMTP]:
        """Obtém conexão do pool ou cria nova"""
        try:
            if cls._connections:
                return cls._connections.pop()
            return cls._create_connection()
        except Exception as e:
            logger.error(f"❌ Erro no pool de conexões: {e}")
            return None
    
    @classmethod
    def _create_connection(cls) -> Optional[smtplib.SMTP]:
        """Cria nova conexão SMTP"""
        try:
            server = smtplib.SMTP(EMAIL_CONFIG.host, EMAIL_CONFIG.port, 
                                timeout=EMAIL_CONFIG.timeout)
            
            if EMAIL_CONFIG.use_tls:
                server.starttls(context=ssl.create_default_context())
            
            server.login(EMAIL_CONFIG.user, EMAIL_CONFIG.password)
            logger.info(f"✅ Nova conexão SMTP: {EMAIL_CONFIG.host}:{EMAIL_CONFIG.port}")
            return server
            
        except Exception as e:
            logger.error(f"❌ Falha na conexão SMTP: {e}")
            return None
    
    @classmethod
    def return_connection(cls, connection: smtplib.SMTP):
        """Retorna conexão ao pool"""
        if connection and connection.noop()[0] == 250:  # Verifica se ainda está válida
            cls._connections.append(connection)
        else:
            try:
                connection.quit()
            except:
                pass

# =====================================================
# ✉️ Núcleo do Sistema de E-mail
# =====================================================
def send_email_advanced(
    subject: str, 
    body: str, 
    to_address: str = None,
    html_body: str = None,
    attachments: List[Tuple[str, bytes, str]] = None,
    priority: str = "normal"
) -> EmailResult:
    """
    Função principal unificada para envio de e-mails
    """
    # Validação e configuração
    to = to_address or EMAIL_CONFIG.default_to
    if not to:
        return EmailResult(False, "❌ Nenhum destinatário especificado", to)
    
    if not all([EMAIL_CONFIG.user, EMAIL_CONFIG.password]):
        return EmailResult(False, "❌ Configuração SMTP incompleta", to)

    # Preparar mensagem
    try:
        msg = _create_email_message(subject, body, to, html_body, attachments, priority)
        server = SMTPConnectionPool.get_connection()
        
        if not server:
            return EmailResult(False, "❌ Falha na conexão SMTP", to)
        
        server.send_message(msg)
        SMTPConnectionPool.return_connection(server)
        
        logger.info(f"✅ E-mail enviado para {to}: {subject}")
        return EmailResult(True, "✅ E-mail enviado com sucesso", to)
        
    except Exception as e:
        error_msg = f"❌ Erro ao enviar e-mail: {str(e)}"
        logger.error(error_msg)
        return EmailResult(False, error_msg, to)

def _create_email_message(
    subject: str, 
    body: str, 
    to: str,
    html_body: str = None,
    attachments: List[Tuple[str, bytes, str]] = None,
    priority: str = "normal"
) -> MIMEMultipart:
    """Cria a mensagem de e-mail com todos os componentes"""
    
    # Definir tipo de mensagem
    if attachments:
        msg = MIMEMultipart("mixed")
    elif html_body:
        msg = MIMEMultipart("alternative")
    else:
        msg = MIMEMultipart()  # Fallback
    
    # Headers e prioridade
    priority_headers = {
        "high": ("🚨 ALTA PRIORIDADE: ", "1"),
        "normal": ("", "3"),
        "low": ("ℹ️ ", "5")
    }
    
    prefix, priority_level = priority_headers.get(priority, ("", "3"))
    
    msg["Subject"] = f"{prefix}{subject}"
    msg["From"] = f"DashFin Supremo <{EMAIL_CONFIG.user}>"
    msg["To"] = to
    msg["X-Priority"] = priority_level
    msg["Date"] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
    
    # Corpo da mensagem
    if html_body:
        text_part = MIMEText(body, "plain", "utf-8")
        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(text_part)
        msg.attach(html_part)
    else:
        msg.attach(MIMEText(body, "plain", "utf-8"))
    
    # Anexos
    if attachments:
        for filename, data, mime_type in attachments:
            _attach_file(msg, filename, data, mime_type)
    
    return msg

def _attach_file(msg: MIMEMultipart, filename: str, data: bytes, mime_type: str):
    """Adiciona anexo à mensagem"""
    try:
        main_type, sub_type = mime_type.split("/", 1)
        part = MIMEBase(main_type, sub_type)
        part.set_payload(data)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{filename}"'
        )
        msg.attach(part)
        logger.debug(f"📎 Anexado: {filename}")
    except Exception as e:
        logger.warning(f"⚠️ Falha ao anexar {filename}: {e}")

# =====================================================
# 📊 Funções Especializadas (Mantidas compatíveis)
# =====================================================
def send_email_alert(subject: str, body: str, to_address: str = None, 
                    html_body: str = None) -> Tuple[bool, str]:
    """Compatibilidade com código existente"""
    result = send_email_advanced(subject, body, to_address, html_body)
    return result.success, result.message

def send_financial_report(to_address: str, subject: str, data: dict, 
                         charts: List[Tuple[str, bytes]] = None) -> Tuple[bool, str]:
    """Versão otimizada do relatório financeiro"""
    html_body = EmailTemplate.financial_report(subject, data)
    
    attachments = []
    if charts:
        attachments = [(f"{name}.png", data, "image/png") for name, data in charts]
    
    result = send_email_advanced(
        subject=f"📊 Relatório: {subject}",
        body=f"Relatório: {subject}\n\n" + "\n".join([f"{k}: {v}" for k, v in data.items()]),
        to_address=to_address,
        html_body=html_body,
        attachments=attachments
    )
    
    return result.success, result.message

# =====================================================
# 🔔 Sistema de Notificações Avançado
# =====================================================
class AdvancedEmailNotifier:
    """Sistema de notificações com métricas e filas"""
    
    def __init__(self):
        self.sent_count = 0
        self.failed_count = 0
        self.last_sent = None
    
    def send_alert(self, title: str, message: str, priority: str = "medium") -> bool:
        """Envia alerta com tracking"""
        priority_map = {
            "high": "high",
            "medium": "normal", 
            "low": "low"
        }
        
        email_priority = priority_map.get(priority, "normal")
        subject = f"{'🚨' if priority == 'high' else '⚠️'} {title}"
        
        result = send_email_advanced(
            subject=subject,
            body=message,
            priority=email_priority
        )
        
        if result.success:
            self.sent_count += 1
            self.last_sent = result.timestamp
        else:
            self.failed_count += 1
            
        return result.success
    
    def get_detailed_stats(self) -> dict:
        """Estatísticas detalhadas"""
        return {
            "sent_count": self.sent_count,
            "failed_count": self.failed_count,
            "success_rate": self.sent_count / max(1, self.sent_count + self.failed_count) * 100,
            "last_sent": self.last_sent,
            "smtp_configured": bool(EMAIL_CONFIG.user and EMAIL_CONFIG.password),
            "default_recipient": EMAIL_CONFIG.default_to
        }

# =====================================================
# 🧪 Teste da Versão Otimizada
# =====================================================
if __name__ == "__main__":
    print("🚀 TESTE DA VERSÃO OTIMIZADA - KLSTARTECH")
    print("=" * 50)
    
    # Teste básico
    print("1. 📧 Teste de e-mail unificado...")
    result = send_email_advanced(
        subject="Teste Sistema Otimizado",
        body="Sistema de e-mail KLStarTech - Versão Avançada!",
        priority="normal"
    )
    print(f"   Resultado: {result.message}")
    
    # Teste com template
    print("\n2. 📊 Teste de relatório financeiro...")
    sample_data = {
        "Receita Total": "R$ 150.000,00",
        "Despesas": "R$ 45.000,00", 
        "Lucro Líquido": "R$ 105.000,00",
        "Crescimento": "+15%"
    }
    
    success, msg = send_financial_report(
        to_address=EMAIL_CONFIG.default_to,
        subject="Relatório Trimestral 2024",
        data=sample_data
    )
    print(f"   Resultado: {msg}")
    
    # Teste do notificador avançado
    print("\n3. 🔔 Teste do notificador avançado...")
    notifier = AdvancedEmailNotifier()
    notifier.send_alert("Sistema Otimizado", "Tudo funcionando perfeitamente!", "high")
    
    print(f"\n📈 Estatísticas detalhadas:")
    for k, v in notifier.get_detailed_stats().items():
        print(f"   {k}: {v}")
    
    print("✅ Teste completo da versão otimizada!")