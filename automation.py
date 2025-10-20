import os
import time
from data import pegar_dados
from fpdf import FPDF
import pandas as pd
import io
import numpy as np
from sklearn.linear_model import LinearRegression

# Função para gerar previsão
def gerar_previsao(df, dias_futuros=3):
    df = df.reset_index(drop=True)
    x = np.arange(len(df)).reshape(-1,1)
    y = df['bid'].values
    modelo = LinearRegression
    modelo.fit(x,y)
    x_futuro = np.arange(len(df), len(df) + dias_futuros).reshape(-1,1)
    y_pred = modelo.predict(x_futuro)
    # Datas futuros
    datas_futuras =[df['timestamp'].iloc[-1] + pd.Timedelta(days=i+1) for i in range(dias_futuros)]
    df_pred = pd.DataFrame({'timestamp': datas_futuras, 'bid': y_pred})
    return df_pred

 # Pasta onde os relatórios serão salvos
REPORTS_FOLDER = "reports"
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# Função de geração de relatório (igual ao main.py)
def gerar_excel(df, moeda):
    df_pred = gerar_previsao(df)
    df_completo = pd.concat([df, df_pred], ignore_index=True)
    file_path = os.path.join(REPORTS_FOLDER, f"{moeda}_cotacoes.xlsx")
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df_completo.to_excel(writer, index=False, sheet_name='Cotações')
        writer.save()
    print(f"Excel salvo: {file_path}")
def gerar_pdf(df, moeda):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Cotações {moeda}/BRL", In=True, align='C')
    pdf.In(10)
    pdf.set_font("Arial", '', 12)

    # Gerar previsões
    df_pred = gerar_previsao(df)
    
    # Dados históricos
    pdf.cell(0, 10, "Histórico:", In=True)
    for i in range(len(df)):
        data = df.iloc[i]['timestamp'].strftime('%Y-%m-%d')
        valor = df.iloc[i]['bid']
        pdf.cell(0, 10, f"{data}: R$ {valor:.2f}", In=True)
        
    pdf.In(5)
    # Previsão
    pdf.cell(0, 10, "Previsão:", In=True)
    for i in range(len(df_pred)):
        data = df_pred.iloc[i]['timestamp'].strftime('%Y-%m-%d')
        valor = df_pred.iloc[i]['bid']
        pdf.cell(0, 10, f"{data}: R$ {valor:.2f}", In=True)
            
    file_path = os.path.join(REPORTS_FOLDER, f"{moeda}_cotacoes.pdf")
    pdf.output(file_path)
    print(f"PDF salvo: {file_path}")    
    
    for i in range(len(df)):
        data = df.iloc[i]['timestamp'].strftime('%Y-%m-%d')
        valor = df.iloc[i]['bid']
        pdf.cell(0, 10, f"{data}: R$ {valor:2f}", In=True)
    file_path = os.path.join(REPORTS_FOLDER, f"{moeda}_cotacoes.pdf")
    pdf.output(file_path)
    print(f"PDF salvo: {file_path}")
    
    # Função principal da automação
def automatizar(moeda="USD", dias=7, intervalo=3600):
    """"
    Atualiza dados e gera relatórios automaticamente.
    intervalo: tempo em segundos entre cada atualização
    """
    while True:
        print("Buscando dados...")
        df = pegar_dados(moeda, dias)
        gerar_excel(df, moeda)
        gerar_pdf(df, moeda)
        print(f"Relatórios atualizados para {moeda}/BRL. Próxima atualização em {intervalo} segundos")
        time.sleep(intervalo)
        
# Exemplo: rodar a automação para USD, 7 dias de histórico, atualização a cada 1 hora
if __name__ =="__main__":
    automatizar(moeda="USD", dias=7, intervalo=3600)      
    