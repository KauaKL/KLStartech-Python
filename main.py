# main.py - DashFin completo com alertas
import streamlit as st
import pandas as pd
import numpy as np
import io
import time
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
from data import pegar_dados
from datetime import datetime
import threading
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from dotenv import load_dotenv
import os

# ----- Carregar variáveis de ambiente -----
load_dotenv()

SMTP_HOST = os.getenv("ALERT_EMAIL_HOST")
SMTP_PORT = int(os.getenv("ALERT_EMAIL_PORT") or 587)
SMTP_USER = os.getenv("ALERT_EMAIL_USER")
SMTP_PASS = os.getenv("ALERT_EMAIL_PASS")
DEFAULT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
DEFAULT_WHATSAPP_TO = os.getenv("ALERT_WHATSAPP_TO")

# Estado para cooldown de alertas
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

# ----- Envio de alertas -----
def send_email_alert(subject: str, body: str, to_address=None):
    to = to_address or DEFAULT_EMAIL_TO
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and to):
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
        return True
    except Exception as e:
        print("Erro email:", e)
        return False

def send_whatsapp_alert(body: str, to_number=None):
    to = to_number or DEFAULT_WHATSAPP_TO
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_WHATSAPP_FROM and to):
        return False
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=body, from_=TWILIO_WHATSAPP_FROM, to=to)
        return True
    except Exception as e:
        print("Erro WhatsApp:", e)
        return False

# ----- Config Streamlit -----
st.set_page_config(page_title="DashFin — Financeiro", layout='centered')
st.title("DashFin — Dashboard Financeiro")
st.markdown("Visualize cotações, previsões e receba alertas automáticos!")

# Entrada do usuário
moeda = st.selectbox("Moeda", ["USD", "EUR", "BTC"])
dias = st.slider("Dias de histórico", 5, 30, 7)
valor_alvo = st.number_input("Valor alvo para alerta (R$)", min_value=0.0, value=6.0)
cooldown = st.number_input("Cooldown alerta (segundos)", min_value=0, value=3600)
enviar_email = st.checkbox("Enviar alerta por E-mail", value=bool(SMTP_HOST and SMTP_USER and SMTP_PASS))
email_to = st.text_input("E-mail destino (opcional)", value=DEFAULT_EMAIL_TO)
enviar_whatsapp = st.checkbox("Enviar alerta por WhatsApp", value=bool(TWILIO_SID and TWILIO_TOKEN and TWILIO_WHATSAPP_FROM))
whatsapp_to = st.text_input("WhatsApp destino (opcional)", value=DEFAULT_WHATSAPP_TO)

# Buscar dados
st.write("Buscando dados...")
df = pegar_dados(moeda, dias)
st.success("Dados carregados!")

# Estatísticas
st.subheader(f"Estatísticas - {moeda}/BRL")
st.write(f"Média: R$ {df['bid'].mean():.2f}")
st.write(f"Mínimo: R$ {df['bid'].min():.2f}")
st.write(f"Máximo: R$ {df['bid'].max():.2f}")

# Gráfico Plotly
fig = px.line(df, x='timestamp', y='bid', title=f"{moeda}/BRL - Últimos {dias} dias", markers=True)
st.plotly_chart(fig, use_container_width=True)

# ----- Previsão Linear -----
st.subheader("Previsão de Cotação (3 dias)")
df_reset = df.reset_index(drop=True)
X = np.arange(len(df_reset)).reshape(-1,1)
y = df_reset['bid'].values
modelo = LinearRegression()
modelo.fit(X,y)
X_futuro = np.arange(len(df_reset), len(df_reset)+3).reshape(-1,1)
y_pred = modelo.predict(X_futuro)
df_pred = pd.DataFrame({
    'timestamp':[df_reset['timestamp'].iloc[-1]+pd.Timedelta(days=i+1) for i in range(3)],
    'bid':y_pred
})
for i in range(3):
    st.write(f"{df_pred.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df_pred.iloc[i]['bid']:.2f}")

# Gráfico Matplotlib
fig2, ax2 = plt.subplots()
ax2.plot(df_reset['bid'].values, label='Histórico', marker='o')
ax2.scatter(range(len(df_reset), len(df_reset)+3), y_pred, color='red', label='Previsão', marker='x')
ax2.set_title(f"{moeda}/BRL - Previsão")
ax2.set_xlabel("Dias")
ax2.set_ylabel("Valor (R$)")
ax2.legend()
st.pyplot(fig2)

# ----- Função alertas -----
def verificar_alerta():
    atual = df_reset['bid'].iloc[-1]
    if atual >= valor_alvo and can_send_alert(moeda, valor_alvo, cooldown):
        texto = f"Alerta {moeda}/BRL: valor atual R$ {atual:.2f} >= {valor_alvo:.2f}"
        def enviar():
            if enviar_email:
                send_email_alert(f"Alerta {moeda}", texto, email_to or None)
            if enviar_whatsapp:
                send_whatsapp_alert(texto, whatsapp_to or None)
            mark_alert_sent(moeda, valor_alvo)
        threading.Thread(target=enviar, daemon=True).start()
        st.success(texto)
    else:
        st.info(f"Último valor R$ {atual:.2f} — sem alerta")

verificar_alerta()

# ----- Download Excel -----
def gerar_excel(df, df_pred):
    df_total = pd.concat([df, df_pred], ignore_index=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_total.to_excel(writer, index=False, sheet_name='Cotações')
    return output.getvalue()

st.download_button("Baixar Excel", gerar_excel(df, df_pred), file_name=f"{moeda}_cotacoes.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ----- Download PDF -----
def gerar_pdf(df, df_pred, moeda):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial",'B',16)
    pdf.cell(0,10,f"Cotações {moeda}/BRL", ln=True, align='C')
    pdf.ln(8)
    pdf.set_font("Arial",'',12)
    pdf.cell(0,8,"Histórico:", ln=True)
    for i in range(len(df)):
        pdf.cell(0,7,f"{df.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df.iloc[i]['bid']:.2f}", ln=True)
    pdf.ln(6)
    pdf.set_font("Arial",'B',12)
    pdf.cell(0,8,"Previsão:", ln=True)
    pdf.set_font("Arial",'',12)
    for i in range(len(df_pred)):
        pdf.cell(0,7,f"{df_pred.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df_pred.iloc[i]['bid']:.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

st.download_button("Baixar PDF", gerar_pdf(df, df_pred, moeda),
                   file_name=f"{moeda}_cotacoes.pdf", mime="application/pdf")

st.success("Dashboard carregado com sucesso!")
