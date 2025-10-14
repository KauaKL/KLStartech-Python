import streamlit as st 
import plotly.express as px
import io
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from data import pegar_dados
from fpdf import FPDF

# A biblioteca streamlit é usada para criar a interface web
# A função pegar_dados é importada do arquivo data.py para buscar os dados das cotações

st.set_page_config(page_title="DASHBORD FINANCEIRO", layout='centered')

st.title("DASHBORD FINANCEIRO")
st.markdown("Visualize as cotações de moedas em tempo real e seus históricos.")

# Escolha da moeda
moeda = st.selectbox("Selecione a moeda:", ["USD", "EUR", "BTC"])
dias = st.slider("Seleccione quantos dias de histórico deseja ver:", min_value=5, max_value=30, value=7)

# Buscar  dados
st.write("Buscando dados, aguarde...")
df = pegar_dados(moeda, dias)
st.success("Dados carregados com sucesso!")
import time
# Simular tempo de espera
time.sleep(3)
placeholder = st.empty()
st.dataframe(df.head())


# Exibir estatísticas
media = df['bid'].mean()
minimo = df['bid'].min()
maximo = df['bid'].max()

st.subheader(f" Estatísticas - {moeda}/BRL")
st.write(f"**Média:** R$ {media:2f}")
st.write(f"**Minimo:** R${minimo:2f}")
st.write(f"**Mximo:**R${maximo:2f}")

# Gráfico interativo
# exibir grafico 
fig = px.line(
    df,
    x='timestamp',
    y='bid',
    title=f"cotação {moeda}/BRL - Últimos {dias} dias",
    labels={'timestamp': 'Data', 'bid': 'valor (R$)'},
    markers=True
)
st.subheader("📈 Previsão de Cotação (Regressão Linear)")

# Preparar os dados
df = df.reset_index(drop=True)
X = np.arange(len(df)).reshape(-1, 1)
y = df['bid'].values

# Treinar o modelo
modelo = LinearRegression()
modelo.fit(X, y)

# Fazer previsão para os próximos 3 dias
dias_futuros = 3
X_futuro = np.arange(len(df), len(df) + dias_futuros).reshape(-1, 1)
y_pred = modelo.predict(X_futuro)

# Exibir previsões
st.write("Previsão para os próximos dias:")
for i in range(dias_futuros):
    st.write(f"Dia {i+1}: R$ {y_pred[i]:.2f}")

# Gráfico com a previsão
fig_pred = px.line(df, x='timestamp', y='bid', title=f"Previsão de Cotação {moeda}/BRL")
fig_pred.add_scatter(x=[df['timestamp'].iloc[-1] + pd.Timedelta(days=i+1) for i in range(dias_futuros)],
                     y=y_pred, mode='lines+markers', name='Previsão')
st.plotly_chart(fig_pred, use_container_width=True)


st.plotly_chart(fig, use_container_width=True)

# Função para gerar Excel
def gerar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Cotações', index=False)
    processed_data = output.getvalue()
    return processed_data

# Botão para baixar Excel
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
    pdf.cell(0, 10, f"cotações {moeda}/BRL", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    
    # Adiciona dados do PDF
    for i in range(len(df)):
        data = df.iloc[i]['timestamp'].strftime('%Y-%m-%d')
        valor= df.iloc[i]['bid']
        pdf.cell(0, 10, f"{data}: R$ {valor:.2f}", ln=True)
        
    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output

# Botão para baixar PDF
pdf_data = gerar_pdf(df,moeda)
st.download_button(
    label="Baixar relatório PDF",
    data=pdf_data,
    file_name=f"{moeda}_cotacoes.pdf",
    mime="application/pdf"
)
st.success(" Dashbord carregado com sucesso!")