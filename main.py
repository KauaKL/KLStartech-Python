import streamlit as st
import matplotlib.pyplot as plt 
from data import pegar_dados

# A biblioteca streamlit é usada para criar a interface web
# A biblioteca matplotlib é usada para criar os gráficos
# A função pegar_dados é importada do arquivo data.py para buscar os dados das cotações

st.set_page_config(page_title="Dashbord Financeiro", layout='centered')

st.title("Dashbord Financeiro")
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

# Exibir gráfico
fig, ax = plt.subplots()
ax.plot(df['timestamp'], df['bid'], marker='o')
ax.set_title(f"Cotação {moeda}/BRL - Últimos {dias} dias")
ax.set_xlabel("Data")
ax.set_ylabel("Valor (R$)")
ax.grid(True)
st.pyplot(fig)

st.success(" Dashbord carregado com sucesso!")