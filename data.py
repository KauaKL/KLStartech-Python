import requests
import pandas as pd
import time
from datetime import datetime, timedelta

def pegar_dados(moeda='USD', dias=7, tentativas=3):
    """
    Busca cotações históricas de uma moeda em relação ao BRL.
    
    1️⃣ Tenta pela AwesomeAPI.
    2️⃣ Se falhar, usa a ExchangeRate Host como fallback.
    
    Parâmetros:
        moeda (str): Código da moeda (USD, EUR, BTC, etc.)
        dias (int): Número de dias de histórico
        tentativas (int): Número de tentativas antes do fallback
    
    Retorna:
        pd.DataFrame com colunas ['timestamp', 'bid'] ou DataFrame vazio em caso de falha.
    """
    
    # ----- 1️⃣ Tentativa: AwesomeAPI -----
    url1 = f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/{dias}'
    
    for i in range(tentativas):
        try:
            print(f"🔎 Tentando buscar dados da AwesomeAPI ({i+1}/{tentativas})...")
            r = requests.get(url1, timeout=20)
            r.raise_for_status()
            
            try:
                dados = r.json()
            except ValueError:
                print("⚠️ Resposta inválida (não é JSON). Conteúdo recebido:")
                print(r.text)
                continue

            if not isinstance(dados, list) or len(dados) == 0:
                print("⚠️ Nenhum dado retornado pela AwesomeAPI.")
                continue

            df = pd.DataFrame(dados)
            
            # Validando colunas essenciais
            if 'timestamp' not in df or 'bid' not in df:
                print("⚠️ Dados retornados estão incompletos.")
                continue
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
            df['bid'] = pd.to_numeric(df['bid'], errors='coerce')
            df = df.dropna(subset=['timestamp', 'bid'])
            
            if df.empty:
                print("⚠️ DataFrame da AwesomeAPI está vazio após limpeza.")
                continue
            
            df = df[['timestamp', 'bid']].sort_values('timestamp').reset_index(drop=True)
            print(f"✅ Dados carregados da AwesomeAPI ({moeda}) com sucesso!")
            return df

        except requests.Timeout:
            print(f"⏳ Timeout na AwesomeAPI (tentativa {i+1}/{tentativas})")
            time.sleep(2)
        except requests.RequestException as e:
            print(f"❌ Erro na AwesomeAPI: {e}")
            time.sleep(2)

    # ----- 2️⃣ Fallback: ExchangeRate Host -----
    print("⚠️ AwesomeAPI indisponível. Tentando API alternativa (ExchangeRate Host)...")
    
    end_date = datetime.today()
    start_date = end_date - timedelta(days=dias)
    url2 = (
        f"https://api.exchangerate.host/timeseries"
        f"?base={moeda}&symbols=BRL"
        f"&start_date={start_date.strftime('%Y-%m-%d')}"
        f"&end_date={end_date.strftime('%Y-%m-%d')}"
    )
    
    try:
        r2 = requests.get(url2, timeout=20)
        r2.raise_for_status()
        data = r2.json()

        if "rates" not in data or not data["rates"]:
            print("❌ API alternativa não retornou dados válidos.")
            return pd.DataFrame(columns=['timestamp','bid'])

        registros = []
        for dia, valores in data["rates"].items():
            if "BRL" in valores:
                registros.append({
                    "timestamp": pd.to_datetime(dia, errors='coerce'),
                    "bid": pd.to_numeric(valores["BRL"], errors='coerce')
                })
        
        df = pd.DataFrame(registros).dropna(subset=['timestamp','bid']).sort_values("timestamp").reset_index(drop=True)
        
        if df.empty:
            print("⚠️ DataFrame da API alternativa está vazio após limpeza.")
            return pd.DataFrame(columns=['timestamp','bid'])

        print(f"✅ Dados carregados da ExchangeRate Host ({moeda}) com sucesso!")
        return df

    except Exception as e:
        print(f"❌ Falha na API alternativa: {e}")
        return pd.DataFrame(columns=['timestamp','bid'])
