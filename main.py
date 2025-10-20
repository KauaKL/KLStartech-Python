import streamlit as st 
import plotly.express as px
import io
import pandas as pd
import numpy as np
import time
from sklearn.linear_model import LinearRegression
from data import pegar_dados
from fpdf import FPDF
import matplotlib.pyplot as plt

# Configuração inicial do Streamlit
st.set_page_config(page_title="DASHBORD FINANCEIRO", layout='centered')
st.title("DASHBORD FINANCEIRO")
st.markdown("Visualize as cotações de moedas em tempo real e seus históricos.")

# Escolha da moeda e intervalo de dias
moeda = st.selectbox("Selecione a moeda:", ["USD", "EUR", "BTC"])
dias = st.slider("Selecione quantos dias de histórico deseja ver:", min_value=5, max_value=30, value=7)

# Buscar dados
st.write("Buscando dados, aguarde...")
df = pegar_dados(moeda, dias)
st.success("Dados carregados com sucesso!")

# Simular tempo de espera para melhor experiência visual
time.sleep(3)
st.dataframe(df.head())

# Exibir estatísticas básicas
media = df['bid'].mean()
minimo = df['bid'].min()
maximo = df['bid'].max()

st.subheader(f"Estatísticas - {moeda}/BRL")
st.write(f"**Média:** R$ {media:.2f}")
st.write(f"**Mínimo:** R$ {minimo:.2f}")
st.write(f"**Máximo:** R$ {maximo:.2f}")

# Gráfico interativo com Plotly
fig = px.line(
    df,
    x='timestamp',
    y='bid',
    title=f"Cotação {moeda}/BRL - Últimos {dias} dias",
    labels={'timestamp': 'Data', 'bid': 'Valor (R$)'},
    markers=True
)
st.plotly_chart(fig, use_container_width=True)

# Previsão de Cotação (Regressão Linear)
st.subheader("Previsão de Cotação (Regressão Linear)")

# Preparar dados para regressão
df = df.reset_index(drop=True)
X = np.arange(len(df)).reshape(-1, 1)
y = df['bid'].values

modelo = LinearRegression()
modelo.fit(X, y)

# Prever o próximo dia
proximo_dia = np.array([[len(df)]])
previsao = modelo.predict(proximo_dia)[0]

# Exibir previsão
st.write(f"Previsão para o próximo dia: **R$ {previsao:.2f}**")

# Previsão para os próximos 3 dias
dias_futuros = 3
X_futuro = np.arange(len(df), len(df) + dias_futuros).reshape(-1, 1)
y_pred = modelo.predict(X_futuro)

st.write("Previsão para os próximos dias:")
for i in range(dias_futuros):
    st.write(f"Dia {i+1}: R$ {y_pred[i]:.2f}")

# Gráfico com Matplotlib da previsão
fig2, ax2 = plt.subplots()
ax2.plot(X.flatten(), df['bid'], label='Histórico', marker='o')
ax2.scatter(len(df), previsao, color='red', label='Previsão', marker='x', s=100)
ax2.set_title(f"Previsão da Cotação {moeda}/BRL")
ax2.set_xlabel("Dias")
ax2.set_ylabel("Valor (R$)")
ax2.legend()
st.pyplot(fig2)

# Função para gerar Excel
def gerar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Cotações', index=False)
    return output.getvalue()

# Botão para download do Excel
excel_data = gerar_excel(df)
st.download_button( 
    label="Baixar relatório Excel",
    data=excel_data,
    file_name=f"{moeda}_cotacoes.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Função para gerar PDF
def gerar_pdf(df, moeda):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Cotações {moeda}/BRL", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    
    for i in range(len(df)):
        data = df.iloc[i]['timestamp'].strftime('%Y-%m-%d')
        valor = df.iloc[i]['bid']
        pdf.cell(0, 10, f"{data}: R$ {valor:.2f}", ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

# Botão para download do PDF
pdf_data = gerar_pdf(df, moeda)
st.download_button(
    label="Baixar relatório PDF",
    data=pdf_data,
    file_name=f"{moeda}_cotacoes.pdf",
    mime="application/pdf"
)

st.success("Dashboard carregado com sucesso!")
