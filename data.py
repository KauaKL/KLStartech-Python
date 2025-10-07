import requests
import pandas as pd 

def pegar_dados(moeda='USD', dias=7):
    """"
    Busca as cotações dos últimos dias usando a API a AwesomeAPI
    Moeda: código da moeda (USD, EUR, BTC)
    dias: quantidade de dias de histórico
    """
    url =f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/{dias}'
    r = requests.get(url)
    dados = r.json()
    df =pd.DataFrame(dados)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df['bid'] = df['bid'].astype(float)
    df = df[['timestamp', 'bid']].sort_values('timestamp')
    return df