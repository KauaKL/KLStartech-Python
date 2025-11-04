import pandas as pd
import requests
from datetime import datetime, timedelta

def pegar_dados_frankfurter(moeda: str, dias: int) -> pd.DataFrame:
    """
    Pega histórico diário de EUR ou USD contra BRL via Frankfurter API.
    Retorna DataFrame com colunas ['timestamp','bid'].
    """
    moeda = moeda.upper()
    if moeda not in ["EUR", "USD"]:
        return pd.DataFrame(columns=['timestamp','bid'])

    fim = datetime.today()
    inicio = fim - timedelta(days=dias)
    url = f"https://api.frankfurter.app/{inicio.strftime('%Y-%m-%d')}..{fim.strftime('%Y-%m-%d')}?from={moeda}&to=BRL"
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("rates", {})
        if not data:
            return pd.DataFrame(columns=['timestamp','bid'])
        
        df = pd.DataFrame([
            {"timestamp": pd.to_datetime(k), "bid": v["BRL"]}
            for k, v in data.items()
        ])
        df.sort_values("timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception as e:
        print("Erro Frankfurter API:", e)
        return pd.DataFrame(columns=['timestamp','bid'])
