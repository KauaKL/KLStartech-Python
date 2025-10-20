# app_flet.py
import os
import threading
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from prophet import Prophet
import flet as ft
from flet.plotly_chart import PlotlyChart

from data import pegar_dados

# Pasta de relatórios
REPORTS_FOLDER = "reports"
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# ---------- IA: previsão Prophet ----------
def gerar_previsao(df: pd.DataFrame, dias_futuros: int = 7) -> pd.DataFrame:
    df_prophet = df[['timestamp', 'bid']].rename(columns={'timestamp': 'ds', 'bid': 'y'})
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

# ---------- Relatórios ----------
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
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    for i in range(len(df)):
        pdf.cell(0, 8, f"{df.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df.iloc[i]['bid']:.4f}", ln=True)
    pdf.ln(8)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Previsão (3 dias):", ln=True)
    pdf.set_font("Arial", "", 12)
    for i in range(len(df_pred)):
        pdf.cell(0, 8, f"{df_pred.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df_pred.iloc[i]['bid']:.4f}", ln=True)
    pdf.output(file_path)
    return file_path

# ---------- Automação ----------
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
                on_update(moeda, dias)
                for _ in range(intervalo):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            return True
        return False

# ---------- UI ----------
def main(page: ft.Page):
    page.title = "DashFin — Mobile/Desktop"
    page.scroll = "always"
    page.padding = 12

    moeda_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("USD"), ft.dropdown.Option("EUR"), ft.dropdown.Option("BTC")],
        value="USD"
    )
    dias_slider = ft.Slider(min=5, max=30, value=7, divisions=25, label="{value} dias")

    intervalo_input = ft.TextField(label="Intervalo automação (segundos)", value="3600", width=200)
    btn_atualizar = ft.ElevatedButton("🔄 Atualizar", width=150)
    btn_excel = ft.ElevatedButton("📊 Exportar Excel", width=150)
    btn_pdf = ft.ElevatedButton("📄 Exportar PDF", width=150)
    btn_auto = ft.ElevatedButton("▶ Iniciar automação", width=200)

    lbl_status = ft.Text("", size=12)
    previsao_list = ft.Column([])
    plot_chart = PlotlyChart()
    automator = Automator()

    def atualizar_ui(moeda, dias):
        lbl_status.value = "Atualizando dados..."
        page.update()
        df = pegar_dados(moeda, dias)
        df_pred = gerar_previsao(df, dias_futuros=5)

        # gráfico interativo com previsão
        fig = px.line(df, x="timestamp", y="bid", title=f"{moeda}/BRL — Últimos {dias} dias", markers=True)
        fig.add_scatter(x=df_pred["timestamp"], y=df_pred["bid"], mode="lines+markers", name="Previsão")
        plot_chart.figure = fig

        previsao_list.controls.clear()
        previsao_list.controls.append(ft.Text("📈 Previsão (5 dias):", weight=ft.FontWeight.BOLD))
        for i in range(len(df_pred)):
            previsao_list.controls.append(ft.Text(f"{df_pred.iloc[i]['timestamp'].strftime('%Y-%m-%d')}: R$ {df_pred.iloc[i]['bid']:.4f}"))

        lbl_status.value = "✅ Atualizado com sucesso!"
        page.client_storage.set("last_df", df.to_json(date_format="iso", orient="split"))
        page.update()

    def gerar_excel(e):
        df_json = page.client_storage.get("last_df")
        if not df_json:
            lbl_status.value = "⚠️ Nenhum dado para exportar!"
            page.update()
            return
        df = pd.read_json(df_json, orient="split")
        path = gerar_excel_arquivo(df, moeda_dropdown.value)
        lbl_status.value = f"📊 Excel salvo: {path}"
        page.update()

    def gerar_pdf(e):
        df_json = page.client_storage.get("last_df")
        if not df_json:
            lbl_status.value = "⚠️ Nenhum dado para exportar!"
            page.update()
            return
        df = pd.read_json(df_json, orient="split")
        path = gerar_pdf_arquivo(df, moeda_dropdown.value)
        lbl_status.value = f"📄 PDF salvo: {path}"
        page.update()

    def automacao(e):
        if btn_auto.text.startswith("▶"):
            intervalo = int(intervalo_input.value)
            automator.start(moeda_dropdown.value, int(dias_slider.value), intervalo, atualizar_ui)
            btn_auto.text = "■ Parar automação"
            lbl_status.value = "🔁 Automação iniciada"
        else:
            automator.stop()
            btn_auto.text = "▶ Iniciar automação"
            lbl_status.value = "⏹ Automação parada"
        page.update()

    btn_atualizar.on_click = lambda e: atualizar_ui(moeda_dropdown.value, int(dias_slider.value))
    btn_excel.on_click = gerar_excel
    btn_pdf.on_click = gerar_pdf
    btn_auto.on_click = automacao

    controles = ft.Column([
        moeda_dropdown,
        dias_slider,
        intervalo_input,
        btn_atualizar,
        btn_excel,
        btn_pdf,
        btn_auto,
        lbl_status
    ], spacing=10)

    layout = ft.Row([controles, ft.Column([plot_chart, previsao_list])])
    page.add(layout)

    atualizar_ui(moeda_dropdown.value, int(dias_slider.value))

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
