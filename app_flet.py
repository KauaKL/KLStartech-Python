# app_flet.py
"""
DashFin — App Flet com:
- Gráfico interativo (Plotly) + previsão (Prophet)
- Geração de relatórios (Excel/PDF)
- Automação periódica
- Alertas inteligentes por E-MAIL (SMTP) e WhatsApp (Twilio)
- Cooldown para evitar alertas repetidos
- Uso de variáveis de ambiente via python-dotenv

Dependências:
pip install flet plotly pandas requests prophet fpdf xlsxwriter twilio python-dotenv

Variáveis de ambiente (preferível usar .env):
# SMTP (ex: Gmail)
ALERT_EMAIL_HOST=smtp.gmail.com
ALERT_EMAIL_PORT=587
ALERT_EMAIL_USER=seu_email@gmail.com
ALERT_EMAIL_PASS=senha_ou_app_password
ALERT_EMAIL_TO=destino@exemplo.com  # opcional se inserir no app
"""

import os
import threading
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from typing import Optional

import pandas as pd
import plotly.express as px
from fpdf import FPDF
from prophet import Prophet

import flet as ft
from flet.plotly_chart import PlotlyChart

from twilio.rest import Client
from dotenv import load_dotenv

from data import pegar_dados

# Carrega .env se existir
load_dotenv()

# Pasta de relatórios
REPORTS_FOLDER = "reports"
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# ----- Configurações de credenciais (lê do ambiente) -----
SMTP_HOST = os.getenv("ALERT_EMAIL_HOST")
SMTP_PORT = int(os.getenv("ALERT_EMAIL_PORT") or 587)
SMTP_USER = os.getenv("ALERT_EMAIL_USER")
SMTP_PASS = os.getenv("ALERT_EMAIL_PASS")
DEFAULT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
DEFAULT_WHATSAPP_TO = os.getenv("ALERT_WHATSAPP_TO")

# ----- Estado para evitar alertas repetidos -----
# Mapeia chave (moeda, valor_alvo) -> timestamp do último alerta enviado
_last_alert_times = {}

def _alert_key(moeda: str, valor_alvo: float) -> str:
    return f"{moeda.upper()}__{valor_alvo}"

def can_send_alert(moeda: str, valor_alvo: float, cooldown_seconds: int) -> bool:
    key = _alert_key(moeda, valor_alvo)
    last = _last_alert_times.get(key)
    if not last:
        return True
    return (datetime.now() - last).total_seconds() >= cooldown_seconds

def mark_alert_sent(moeda: str, valor_alvo: float):
    key = _alert_key(moeda, valor_alvo)
    _last_alert_times[key] = datetime.now()

# ----- Funções de envio de alerta ----- 
def send_email_alert(subject: str, body: str, to_address: Optional[str] = None) -> bool:
    """Envia e-mail via SMTP. Retorna True se sucesso."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print("SMTP não configurado. Pule envio de e-mail.")
        return False
    to = to_address or DEFAULT_EMAIL_TO
    if not to:
        print("Nenhum destino de e-mail configurado.")
        return False
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = to

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [to], msg.as_string())
        server.quit()
        print(f"E-mail enviado para {to}")
        return True
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return False

def send_whatsapp_alert(body: str, to_number: Optional[str] = None) -> bool:
    """Envia WhatsApp via Twilio. Retorna True se sucesso."""
    if not TWILIO_SID or not TWILIO_TOKEN or not TWILIO_WHATSAPP_FROM:
        print("Twilio não configurado. Pule envio de WhatsApp.")
        return False
    to = to_number or DEFAULT_WHATSAPP_TO
    if not to:
        print("Nenhum destino WhatsApp configurado.")
        return False
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(
            body=body,
            from_=TWILIO_WHATSAPP_FROM,
            to=to
        )
        print(f"WhatsApp enviado SID: {message.sid}")
        return True
    except Exception as e:
        print("Erro ao enviar WhatsApp:", e)
        return False

# ----- Funções de previsão / relatório -----
def gerar_previsao(df: pd.DataFrame, dias_futuros: int = 7) -> pd.DataFrame:
    """Gera previsão com Prophet e retorna DataFrame com cols (timestamp, bid, min, max)."""
    df_prophet = df[['timestamp', 'bid']].rename(columns={'timestamp': 'ds', 'bid': 'y'})
    if len(df_prophet) < 2:
        # Poucos dados: repetir último
        last = df_prophet['ds'].iloc[-1] if len(df_prophet) else datetime.now()
        return pd.DataFrame({
            'timestamp': [last + pd.Timedelta(days=i+1) for i in range(dias_futuros)],
            'bid': [float(df['bid'].iloc[-1])] * dias_futuros,
            'min': [float(df['bid'].iloc[-1])] * dias_futuros,
            'max': [float(df['bid'].iloc[-1])] * dias_futuros,
        })
    modelo = Prophet(daily_seasonality=True)
    modelo.fit(df_prophet)
    futuro = modelo.make_future_dataframe(periods=dias_futuros)
    previsao = modelo.predict(futuro)
    df_pred = previsao[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(columns={
        'ds': 'timestamp',
        'yhat': 'bid',
        'yhat_lower': 'min',
        'yhat_upper': 'max'
    })
    return df_pred.tail(dias_futuros)

def gerar_excel_arquivo(df: pd.DataFrame, moeda: str) -> str:
    file_path = os.path.join(REPORTS_FOLDER, f"{moeda}_cotacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    df.to_excel(file_path, index=False)
    return file_path

def gerar_pdf_arquivo(df: pd.DataFrame, moeda: str) -> str:
    df_pred = gerar_previsao(df, dias_futuros=3)
    file_path = os.path.join(REPORTS_FOLDER, f"{moeda}_cotacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Cotações {moeda}/BRL", ln=True, align="C")
    pdf.ln(8)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, "Histórico:", ln=True)
    for i in range(len(df)):
        pdf.cell(0, 7, f"{df.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df.iloc[i]['bid']:.4f}", ln=True)
    pdf.ln(6)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Previsão (3 dias):", ln=True)
    pdf.set_font("Arial", "", 11)
    for i in range(len(df_pred)):
        pdf.cell(0, 7, f"{df_pred.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df_pred.iloc[i]['bid']:.4f}", ln=True)
    pdf.output(file_path)
    return file_path

# ----- Função que verifica condição e envia alertas ----- 
def verificar_e_alertar(page: ft.Page, moeda: str, df: pd.DataFrame, valor_alvo: float,
                        enviar_email: bool, enviar_whatsapp: bool,
                        email_to: Optional[str], whatsapp_to: Optional[str],
                        cooldown_seconds: int):
    """
    Se o último valor >= valor_alvo e tiver cooldown ok, envia alertas configurados.
    Também calcula previsão para tentar estimar em quantos dias o alvo pode ser atingido.
    """
    try:
        atual = float(df['bid'].iloc[-1])
    except Exception as e:
        print("Erro ao obter valor atual:", e)
        return

    # só alerta se valor atual >= alvo
    if atual < valor_alvo:
        return

    if not can_send_alert(moeda, valor_alvo, cooldown_seconds):
        print("Cooldown ativo — não envia alerta duplicado.")
        return

    # calcula previsão para informar em quantos dias o alvo seria alcançado (se aplicável)
    df_pred = gerar_previsao(df, dias_futuros=14)
    dias_para_alvo = None
    for i, v in enumerate(df_pred['bid'].values):
        if v >= valor_alvo:
            dias_para_alvo = i + 1
            break

    # Mensagem
    timestamp = df['timestamp'].iloc[-1].strftime("%Y-%m-%d %H:%M")
    previsao_text = f"\nPrevisão: {f'atingirá em ~{dias_para_alvo} dia(s)' if dias_para_alvo else 'não prevista nos próximos 14 dias'}"
    subject = f"[Alerta] {moeda}/BRL ultrapassou R$ {valor_alvo:.2f}"
    body = (f"Alerta automático — {moeda}/BRL ultrapassou o valor-alvo!\n\n"
            f"Valor atual: R$ {atual:.4f}\n"
            f"Alvo definido: R$ {valor_alvo:.2f}\n"
            f"Data/Hora (último registro): {timestamp}\n"
            f"{previsao_text}\n\n"
            "Mensagem enviada pelo DashFin.")

    # Enviar em threads para não travar a UI
    def _send_tasks():
        results = []
        if enviar_email:
            ok_mail = send_email_alert(subject, body, to_address=email_to)
            results.append(("email", ok_mail))
        if enviar_whatsapp:
            ok_wa = send_whatsapp_alert(body, to_number=whatsapp_to)
            results.append(("whatsapp", ok_wa))
        # marca como enviado se algum canal retornou sucesso
        if any(ok for (_, ok) in results):
            mark_alert_sent(moeda, valor_alvo)

    threading.Thread(target=_send_tasks, daemon=True).start()

    # Notificação imediata na UI
    page.snack_bar = ft.SnackBar(ft.Text(f"⚠️ Alerta: {moeda} >= R$ {valor_alvo:.2f} — verificando envios..."))
    page.snack_bar.open = True
    page.update()

# ----- Automator (mesma lógica) -----
class Automator:
    def __init__(self):
        self._thread = None
        self._stop_event = threading.Event()

    def start(self, moeda, dias, intervalo, on_update):
        if self._thread and self._thread.is_alive():
            return False
        self._stop_event.clear()

        def _loop():
            while not self._stop_event.is_set():
                try:
                    on_update(moeda, dias)
                except Exception as e:
                    print("Erro no on_update:", e)
                for _ in range(max(1, intervalo)):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=2)
            return True
        return False

# ----- UI principal (Flet) -----
def main(page: ft.Page):
    page.title = "DashFin — Mobile/Desktop"
    page.scroll = "always"
    page.padding = 12

    # Controles principais
    moeda_dropdown = ft.Dropdown(options=[ft.dropdown.Option("USD"), ft.dropdown.Option("EUR"), ft.dropdown.Option("BTC")], value="USD")
    dias_slider = ft.Slider(min=5, max=30, value=7, divisions=25, label="{value} dias")

    intervalo_input = ft.TextField(label="Intervalo automação (segundos)", value="3600", width=200)
    btn_atualizar = ft.ElevatedButton("🔄 Atualizar", width=150)
    btn_excel = ft.ElevatedButton("📊 Exportar Excel", width=150)
    btn_pdf = ft.ElevatedButton("📄 Exportar PDF", width=150)
    btn_auto = ft.ElevatedButton("▶ Iniciar automação", width=200)

    # Alertas UI
    alvo_input = ft.TextField(label="Valor alvo (R$)", value="6.00", width=180)
    cooldown_input = ft.TextField(label="Cooldown (segundos)", value="3600", width=180)

    checkbox_email = ft.Checkbox(label="Enviar por E-mail", value=bool(SMTP_HOST and SMTP_USER and SMTP_PASS))
    email_to_input = ft.TextField(label="E-mail destino (opcional)", value=(os.getenv("ALERT_EMAIL_TO") or ""), width=260)

    checkbox_whatsapp = ft.Checkbox(label="Enviar por WhatsApp (Twilio)", value=bool(TWILIO_SID and TWILIO_TOKEN and TWILIO_WHATSAPP_FROM))
    whatsapp_to_input = ft.TextField(label="WhatsApp destino (ex: whatsapp:+55...)", value=(os.getenv("ALERT_WHATSAPP_TO") or ""), width=260)

    lbl_status = ft.Text("", size=12)
    previsao_list = ft.Column([])
    plot_chart = PlotlyChart()
    automator = Automator()

    # Função que atualiza UI, plota gráfico, salva df no client_storage e verifica alertas
    def atualizar_ui(moeda: str, dias: int):
        try:
            lbl_status.value = "Atualizando dados..."
            page.update()

            df = pegar_dados(moeda, dias)
            # garantir tipos
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['bid'] = df['bid'].astype(float)

            # previsão (5 dias)
            df_pred = gerar_previsao(df, dias_futuros=5)

            # criar gráfico
            fig = px.line(df, x="timestamp", y="bid", title=f"{moeda}/BRL — Últimos {dias} dias", labels={"timestamp": "Data", "bid": "Valor (R$)"}, markers=True)
            fig.add_scatter(x=df_pred["timestamp"], y=df_pred["bid"], mode="lines+markers", name="Previsão")
            plot_chart.figure = fig

            # lista de previsão
            previsao_list.controls.clear()
            previsao_list.controls.append(ft.Text("📈 Previsão (5 dias):", weight=ft.FontWeight.BOLD))
            for i in range(len(df_pred)):
                previsao_list.controls.append(ft.Text(f"{df_pred.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df_pred.iloc[i]['bid']:.4f}"))

            lbl_status.value = f"✅ Atualizado: {moeda} (último: R$ {df['bid'].iloc[-1]:.4f})"
            page.client_storage.set("last_df", df.to_json(date_format="iso", orient="split"))

            # verificar alertas configurados
            try:
                valor_alvo = float(alvo_input.value)
                cooldown = int(cooldown_input.value)
                enviar_email = checkbox_email.value
                enviar_whatsapp = checkbox_whatsapp.value
                email_to = email_to_input.value.strip() or None
                whatsapp_to = whatsapp_to_input.value.strip() or None

                # chama função de verificação/alerta (assíncrona de envio)
                verificar_e_alertar(page, moeda, df, valor_alvo, enviar_email, enviar_whatsapp, email_to, whatsapp_to, cooldown)
            except Exception as e:
                print("Erro ao processar alertas:", e)

            page.update()
        except Exception as e:
            lbl_status.value = f"Erro na atualização: {e}"
            page.update()

    # handlers de export / automação
    def gerar_excel(e):
        df_json = page.client_storage.get("last_df")
        if not df_json:
            lbl_status.value = "⚠️ Primeiro atualize os dados."
            page.update()
            return
        df = pd.read_json(df_json, orient="split")
        path = gerar_excel_arquivo(df, moeda_dropdown.value)
        lbl_status.value = f"📊 Excel salvo: {path}"
        page.update()

    def gerar_pdf(e):
        df_json = page.client_storage.get("last_df")
        if not df_json:
            lbl_status.value = "⚠️ Primeiro atualize os dados."
            page.update()
            return
        df = pd.read_json(df_json, orient="split")
        path = gerar_pdf_arquivo(df, moeda_dropdown.value)
        lbl_status.value = f"📄 PDF salvo: {path}"
        page.update()

    def automacao(e):
        if btn_auto.text.startswith("▶"):
            try:
                intervalo = int(intervalo_input.value)
            except:
                intervalo = 3600
            automator.start(moeda_dropdown.value, int(dias_slider.value), intervalo, atualizar_ui)
            btn_auto.text = "■ Parar automação"
            lbl_status.value = "🔁 Automação iniciada"
        else:
            automator.stop()
            btn_auto.text = "▶ Iniciar automação"
            lbl_status.value = "⏹ Automação parada"
        page.update()

    # ligações de botões
    btn_atualizar.on_click = lambda e: atualizar_ui(moeda_dropdown.value, int(dias_slider.value))
    btn_excel.on_click = gerar_excel
    btn_pdf.on_click = gerar_pdf
    btn_auto.on_click = automacao

    # layout
    controles = ft.Column([
        ft.Text("Controles", weight=ft.FontWeight.BOLD),
        ft.Row([ft.Text("Moeda:"), moeda_dropdown], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([ft.Text("Histórico:"), dias_slider], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([btn_atualizar, btn_auto]),
        ft.Row([btn_excel, btn_pdf]),
        ft.Divider(height=8),
        ft.Text("Alertas", weight=ft.FontWeight.BOLD),
        ft.Row([alvo_input, cooldown_input], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([checkbox_email, checkbox_whatsapp]),
        email_to_input,
        whatsapp_to_input,
        ft.Divider(height=8),
        intervalo_input,
        lbl_status
    ], spacing=8, width=360)

    painel_direito = ft.Column([plot_chart, previsao_list], expand=True)

    page.add(ft.Row([controles, painel_direito], expand=True))
    # Carregar dados iniciais
    atualizar_ui(moeda_dropdown.value, int(dias_slider.value))

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
