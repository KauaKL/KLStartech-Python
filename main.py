import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
import plotly.express as px
from prophet import Prophet
from fpdf import FPDF
from datetime import datetime
import threading
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from dotenv import load_dotenv
import os
import tempfile
from streamlit_autorefresh import st_autorefresh
import requests

# ==========================
# 🔧 CONFIGURAÇÕES INICIAIS
# ==========================
load_dotenv()

SMTP_HOST = os.getenv("ALERT_EMAIL_HOST")
SMTP_PORT = int(os.getenv("ALERT_EMAIL_PORT") or 587)
SMTP_USER = os.getenv("ALERT_EMAIL_USER")
SMTP_PASS = os.getenv("ALERT_EMAIL_PASS")
DEFAULT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM") or "whatsapp:+14155238886"
DEFAULT_WHATSAPP_TO = os.getenv("ALERT_WHATSAPP_TO")

_last_alert_times = {}
alert_log = []

# ==========================
# ⚠️ FUNÇÕES DE ALERTA
# ==========================
def _alert_key(moeda, valor):
    return f"{moeda.upper()}__{valor}"

def can_send_alert(moeda, valor_alvo, cooldown):
    key = _alert_key(moeda, valor_alvo)
    last = _last_alert_times.get(key)
    if not last:
        return True
    return (datetime.now() - last).total_seconds() >= cooldown

def mark_alert_sent(moeda, valor, canais):
    key = _alert_key(moeda, valor)
    _last_alert_times[key] = datetime.now()
    alert_log.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), moeda, valor, canais))

def send_email_alert(subject, body, to_address=None):
    to = to_address or DEFAULT_EMAIL_TO
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and to):
        print("⚠️ Configuração de e-mail ausente.")
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
        print(f"📧 E-mail enviado para {to}")
        return True
    except Exception as e:
        print("Erro no envio de e-mail:", e)
        return False

def send_whatsapp_alert(body, to_number=None):
    to = to_number or DEFAULT_WHATSAPP_TO
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_WHATSAPP_FROM and to):
        print("⚠️ Configuração do Twilio ausente.")
        return False
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        msg = client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=body,
            to=to
        )
        print(f"✅ WhatsApp enviado: SID={msg.sid}")
        return True
    except Exception as e:
        print("Erro no envio do WhatsApp:", e)
        return False

# ==========================
# 🌍 OBTENDO DADOS DAS MOEDAS
# ==========================
def pegar_dados_frankfurter(moeda, dias):
    end = datetime.now()
    start = end - pd.Timedelta(days=dias)
    url = f"https://api.frankfurter.app/{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}?to=BRL&from={moeda}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        df = pd.DataFrame(list(data["rates"].items()), columns=["timestamp", "bid"])
        df["bid"] = df["bid"].apply(lambda x: x["BRL"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)
        return df
    except Exception as e:
        st.warning(f"⚠️ Erro ao buscar Frankfurter {moeda}: {e}")
        return pd.DataFrame(columns=["timestamp", "bid"])

def pegar_dados_btc(dias):
    try:
        url = "https://api.coindesk.com/v1/bpi/historical/close.json?currency=BRL"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()["bpi"]
        df = pd.DataFrame(list(data.items()), columns=["timestamp", "bid"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)
        return df.tail(dias)
    except Exception as e:
        st.warning(f"⚠️ Erro ao buscar BTC: {e}")
        return pd.DataFrame(columns=["timestamp", "bid"])

@st.cache_data(ttl=300)
def pegar_dados_cache(moeda, dias):
    moeda = moeda.upper()
    if moeda in ["USD", "EUR"]:
        return pegar_dados_frankfurter(moeda, dias)
    elif moeda == "BTC":
        return pegar_dados_btc(dias)
    else:
        return pd.DataFrame(columns=["timestamp", "bid"])

# ==========================
# 📈 PREVISÃO E EXPORTAÇÃO
# ==========================
@st.cache_data(ttl=300)
def gerar_previsao_prophet(df, dias_previsao):
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "bid"])
    df_prophet = df.rename(columns={"timestamp": "ds", "bid": "y"})
    modelo = Prophet(daily_seasonality=True)
    modelo.fit(df_prophet)
    futuro = modelo.make_future_dataframe(periods=dias_previsao)
    forecast = modelo.predict(futuro)
    df_pred = forecast[["ds", "yhat"]].tail(dias_previsao).rename(columns={"ds": "timestamp", "yhat": "bid"})
    return df_pred

@st.cache_data
def gerar_pdf_cache(df, df_pred, moeda):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Cotações {moeda}/BRL", ln=True, align="C")
    pdf.ln(5)
    if not df.empty:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(df["timestamp"], df["bid"], label="Histórico")
        if not df_pred.empty:
            ax.plot(df_pred["timestamp"], df_pred["bid"], label="Previsão", linestyle="--", color="red")
        ax.legend()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.savefig(tmpfile.name)
            pdf.image(tmpfile.name, x=10, w=190)
        plt.close(fig)
    return pdf.output(dest="S").encode("latin-1")

@st.cache_data
def gerar_excel_cache(df, df_pred):
    df_pred_renamed = df_pred.rename(columns={"bid": "Valor"})
    df_total = pd.concat([df, df_pred_renamed], ignore_index=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_total.to_excel(writer, index=False, sheet_name="Cotações")
    return output.getvalue()

# ==========================
# 🧠 DASHBOARD STREAMLIT
# ==========================
st.set_page_config(page_title="DashFin Supremo", layout="wide")
st.title("💹 DashFin Supremo — Dashboard Financeiro Avançado")

st.markdown("### 🔧 Status dos serviços:")
st.write(f"📧 E-mail: {'✅ Ativo' if SMTP_USER else '❌ Inativo'}")
st.write(f"💬 WhatsApp: {'✅ Ativo' if TWILIO_SID else '❌ Inativo'}")

moeda = st.selectbox("Moeda", ["USD", "EUR", "BTC"])
dias = st.slider("Dias de histórico", 5, 90, 30)
dias_previsao = st.slider("Dias de previsão", 1, 14, 7)
valor_alvo = st.number_input("Valor alvo para alerta (R$)", min_value=0.0, value=6.0)
cooldown = st.number_input("Cooldown alerta (segundos)", min_value=0, value=3600)
enviar_email = st.checkbox("Enviar alerta por e-mail", value=True)
email_to = st.text_input("E-mail destino", value=DEFAULT_EMAIL_TO or "")
enviar_whatsapp = st.checkbox("Enviar alerta por WhatsApp", value=True)
whatsapp_to = st.text_input("WhatsApp destino", value=DEFAULT_WHATSAPP_TO or "whatsapp:+55XXXXXXXXXXX")

# 🔔 BOTÃO DE TESTE COMPLETO
if st.button("🚨 Testar Alerta (visual + som + envio)"):
    alerta_teste = f"🚨 [TESTE] Alerta de sistema ativo!\nMoeda: {moeda}\nHorário: {datetime.now():%d/%m %H:%M:%S}"
    st.markdown(
        """
        <style>
        .alerta-pisca {
            animation: piscar 1s infinite;
            font-size:22px;
            color:red;
            font-weight:bold;
        }
        @keyframes piscar {
            0% {opacity: 1;}
            50% {opacity: 0.2;}
            100% {opacity: 1;}
        }
        </style>
        <div class="alerta-pisca">🚨 ALERTA DE TESTE ATIVADO! 🚨</div>
        """,
        unsafe_allow_html=True,
    )
    st.audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg")
    canais = []
    def enviar():
        if enviar_email:
            send_email_alert("🔔 Alerta de Teste", alerta_teste, email_to)
            canais.append("E-mail")
        if enviar_whatsapp:
            send_whatsapp_alert(alerta_teste, whatsapp_to)
            canais.append("WhatsApp")
        mark_alert_sent(moeda, valor_alvo, ",".join(canais))
    threading.Thread(target=enviar, daemon=True).start()
    st.success(f"✅ Alerta de teste enviado com sucesso via {', '.join(canais) or 'nenhum canal configurado'}!")

refresh_interval = st.slider("Atualização automática (segundos)", 10, 300, 60)

# ==========================
# 🚀 FUNÇÃO PRINCIPAL
# ==========================
def atualizar_dashboard():
    df = pegar_dados_cache(moeda, dias)
    if df.empty:
        st.error(f"Nenhum dado disponível para {moeda}.")
        return df, pd.DataFrame()

    st.subheader(f"📊 Estatísticas — {moeda}/BRL")
    st.metric("Média", f"R$ {df['bid'].mean():.2f}")
    st.metric("Máximo", f"R$ {df['bid'].max():.2f}")
    st.metric("Mínimo", f"R$ {df['bid'].min():.2f}")

    fig_hist = px.line(df, x="timestamp", y="bid", title=f"{moeda}/BRL - Últimos {dias} dias", markers=True)
    st.plotly_chart(fig_hist, use_container_width=True, key=f"hist_{moeda}")

    df_pred = gerar_previsao_prophet(df, dias_previsao)

    if not df_pred.empty:
        st.subheader("🔮 Previsão de Cotação (IA Prophet)")
        for i in range(len(df_pred)):
            st.write(f"{df_pred.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df_pred.iloc[i]['bid']:.2f}")

    fig_comb = px.line(df, x="timestamp", y="bid", title=f"{moeda}/BRL — Histórico + Previsão")
    if not df_pred.empty:
        fig_comb.add_scatter(x=df_pred["timestamp"], y=df_pred["bid"], mode="lines+markers", name="Previsão IA")
    st.plotly_chart(fig_comb, use_container_width=True, key=f"comb_{moeda}")

    ult_valor = df["bid"].iloc[-1]
    if ult_valor >= valor_alvo and can_send_alert(moeda, valor_alvo, cooldown):
        alerta = f"🚨 ALERTA REAL: {moeda}/BRL atingiu R$ {ult_valor:.2f} (≥ {valor_alvo:.2f})"
        st.audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg")
        st.markdown(
            """
            <style>
            .alerta-pisca {
                animation: piscar 1s infinite;
                font-size:22px;
                color:red;
                font-weight:bold;
            }
            @keyframes piscar {
                0% {opacity: 1;}
                50% {opacity: 0.2;}
                100% {opacity: 1;}
            }
            </style>
            <div class="alerta-pisca">🚨 ALERTA ATIVO! VALOR ATINGIDO!</div>
            """,
            unsafe_allow_html=True,
        )
        def enviar():
            canais = []
            if enviar_email:
                send_email_alert(f"Alerta {moeda}", alerta, email_to)
                canais.append("E-mail")
            if enviar_whatsapp:
                send_whatsapp_alert(alerta, whatsapp_to)
                canais.append("WhatsApp")
            mark_alert_sent(moeda, valor_alvo, ",".join(canais))
        threading.Thread(target=enviar, daemon=True).start()

    if alert_log:
        st.subheader("📜 Histórico de Alertas")
        log_df = pd.DataFrame(alert_log, columns=["Data/Hora", "Moeda", "Valor Alvo", "Canais"])
        st.dataframe(log_df)
    else:
        st.info("Nenhum alerta enviado ainda.")

    st.download_button("📘 Baixar Excel", gerar_excel_cache(df, df_pred),
                       file_name=f"{moeda}_cotacoes.xlsx",
                       mime="application/vnd.openxmlformats-officedocument-spreadsheetml.sheet")
    st.download_button("📄 Baixar PDF", gerar_pdf_cache(df, df_pred, moeda),
                       file_name=f"{moeda}_cotacoes.pdf", mime="application/pdf")

    return df, df_pred

# ==========================
# 🔁 ATUALIZAÇÃO AUTOMÁTICA
# ==========================
st_autorefresh(interval=refresh_interval * 1000, key="autorefresh")
df, df_pred = atualizar_dashboard()
