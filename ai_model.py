# ai_model.py
import pandas as pd
import numpy as np

def tendencia_moeda(df: pd.DataFrame) -> str:
    """
    Retorna se a moeda está em tendência 'Alta', 'Baixa' ou 'Neutra'
    usando os últimos 5 dias de histórico.
    """
    if len(df) < 2:
        return "Neutra"
    delta = df['bid'].iloc[-1] - df['bid'].iloc[-5] if len(df) >= 5 else df['bid'].iloc[-1] - df['bid'].iloc[0]
    if delta > 0:
        return "Alta"
    elif delta < 0:
        return "Baixa"
    else:
        return "Neutra"
