# =====================================================
# 📊 data_utils.py — Módulo Unificado de Dados e Previsões
# by KLStarTech (Kauã Lima) + DeepSeek AI
# Integração com data.py para funcionalidades avançadas
# =====================================================

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from functools import lru_cache

# Importar o sistema avançado de dados
try:
    from data import pegar_dados, get_supported_currencies, get_data_stats, clear_cache
    DATA_MODULE_AVAILABLE = True
    print("✅ Módulo data.py carregado - Sistema de dados avançado ativo")
except ImportError as e:
    print(f"⚠️ Módulo data.py não disponível: {e}")
    DATA_MODULE_AVAILABLE = False
    # Fallbacks básicos serão usados

# Tentar importar dependências opcionais
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️ Prophet não disponível - instale: pip install prophet")

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    print("⚠️ FPDF não disponível - instale: pip install fpdf")

try:
    import xlsxwriter
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False
    print("⚠️ xlsxwriter não disponível - instale: pip install xlsxwriter")

# =====================================================
# ⚙️ CONFIGURAÇÃO AVANÇADA
# =====================================================

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KLStarTech_DataUtils")

# =====================================================
# 🔄 SISTEMA DE DADOS HÍBRIDO (data.py + fallbacks)
# =====================================================

@lru_cache(maxsize=32)
def pegar_dados_cache(moeda: str, dias: int) -> pd.DataFrame:
    """
    🎯 FUNÇÃO PRINCIPAL - Sistema híbrido de dados
    
    Usa data.py quando disponível, com fallbacks para APIs originais
    """
    moeda = moeda.upper()
    
    # Prioridade 1: Usar data.py (sistema avançado)
    if DATA_MODULE_AVAILABLE:
        try:
            df = pegar_dados(moeda, dias)
            if not df.empty:
                logger.info(f"✅ Dados obtidos via sistema data.py: {moeda}")
                return df
        except Exception as e:
            logger.warning(f"⚠️ data.py falhou, usando fallback: {e}")
    
    # Prioridade 2: Fallback para sistema original
    return _fallback_pegar_dados(moeda, dias)

def _fallback_pegar_dados(moeda: str, dias: int) -> pd.DataFrame:
    """Sistema de fallback baseado no código original"""
    import requests
    from datetime import datetime, timedelta
    
    moeda = moeda.upper()
    
    # AwesomeAPI (para moedas fiat)
    if moeda in ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY']:
        url = f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/{dias}'
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            dados = response.json()
            
            if isinstance(dados, list) and len(dados) > 0:
                df = pd.DataFrame(dados)
                if 'timestamp' in df and 'bid' in df:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
                    df['bid'] = pd.to_numeric(df['bid'], errors='coerce')
                    df = df[['timestamp', 'bid']].dropna().sort_values('timestamp')
                    
                    # Adicionar colunas padrão para compatibilidade
                    df['volume'] = None
                    df['change_24h'] = None
                    
                    logger.info(f"✅ Fallback: Dados {moeda} via AwesomeAPI")
                    return df.reset_index(drop=True)
                    
        except Exception as e:
            logger.warning(f"❌ Fallback AwesomeAPI falhou: {e}")
    
    # CoinGecko (para criptomoedas)
    crypto_map = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'ADA': 'cardano'}
    if moeda in crypto_map:
        coin_id = crypto_map[moeda]
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=brl&days={dias}&interval=daily'
        
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            if 'prices' in data:
                records = []
                for [timestamp, price] in data['prices']:
                    records.append({
                        "timestamp": pd.to_datetime(timestamp, unit='ms'),
                        "bid": float(price),
                        "volume": None,
                        "change_24h": None
                    })
                
                if records:
                    df = pd.DataFrame(records)
                    logger.info(f"✅ Fallback: Dados {moeda} via CoinGecko")
                    return df.sort_values('timestamp').reset_index(drop=True)
                    
        except Exception as e:
            logger.warning(f"❌ Fallback CoinGecko falhou: {e}")
    
    logger.error(f"❌ Todos os sistemas falharam para {moeda}")
    return pd.DataFrame(columns=['timestamp', 'bid', 'volume', 'change_24h'])

# =====================================================
# 📈 SISTEMA DE ANÁLISE TÉCNICA AVANÇADA
# =====================================================

def calcular_indicadores_tecnicos(df: pd.DataFrame) -> Dict:
    """Calcula indicadores técnicos avançados com métricas enriquecidas"""
    if df.empty or len(df) < 2:
        return {}
    
    try:
        prices = df["bid"].values
        current_price = prices[-1]
        
        # Indicadores de tendência
        if len(prices) >= 2:
            change_1d = ((prices[-1] - prices[-2]) / prices[-2]) * 100
        else:
            change_1d = 0
        
        # Médias móveis
        ma_7 = np.mean(prices[-7:]) if len(prices) >= 7 else current_price
        ma_30 = np.mean(prices[-30:]) if len(prices) >= 30 else current_price
        
        # Suportes e resistências
        resistance = np.max(prices[-10:]) if len(prices) >= 10 else current_price
        support = np.min(prices[-10:]) if len(prices) >= 10 else current_price
        
        # Volatilidade
        volatility = np.std(prices[-7:]) / ma_7 * 100 if len(prices) >= 7 else 0
        
        # RSI (14 períodos)
        rsi = _calcular_rsi(prices) if len(prices) >= 15 else 50
        
        # MACD simples
        macd_signal = "COMPRA" if ma_7 > ma_30 else "VENDA"
        
        # Força da tendência
        if abs(change_1d) > 5:
            trend_strength = "FORTE"
        elif abs(change_1d) > 2:
            trend_strength = "MODERADA"
        else:
            trend_strength = "FRACA"
        
        # Recomendação baseada em múltiplos indicadores
        recommendation = _gerar_recomendacao(rsi, change_1d, ma_7, ma_30)
        
        return {
            # Preços e variações
            "preco_atual": round(current_price, 4),
            "variacao_1d": round(change_1d, 2),
            "variacao_7d": round(((current_price - prices[-7]) / prices[-7]) * 100, 2) if len(prices) >= 8 else round(change_1d, 2),
            
            # Médias móveis
            "media_7d": round(ma_7, 4),
            "media_30d": round(ma_30, 4),
            "tendencia_media": "ALTA" if ma_7 > ma_30 else "BAIXA",
            
            # Suporte e resistência
            "resistencia": round(resistance, 4),
            "suporte": round(support, 4),
            "faixa_negociacao": round(resistance - support, 4),
            
            # Volatilidade e momentum
            "volatilidade": round(volatility, 2),
            "rsi": round(rsi, 2),
            "sinal_rsi": "SOBREVENDIDO" if rsi < 30 else "SOBRECOMPRADO" if rsi > 70 else "NEUTRO",
            
            # Análise técnica
            "forca_tendencia": trend_strength,
            "sinal_macd": macd_signal,
            "recomendacao": recommendation,
            
            # Metadados
            "timestamp_analise": datetime.now().isoformat(),
            "amostras_analisadas": len(prices)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao calcular indicadores: {e}")
        return {}

def _calcular_rsi(prices: np.ndarray, period: int = 14) -> float:
    """Calcula o RSI (Relative Strength Index)"""
    if len(prices) < period + 1:
        return 50
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gains = np.convolve(gains, np.ones(period)/period, mode='valid')
    avg_losses = np.convolve(losses, np.ones(period)/period, mode='valid')
    
    # Evitar divisão por zero
    avg_losses = np.where(avg_losses == 0, 1e-10, avg_losses)
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi[-1]) if len(rsi) > 0 else 50

def _gerar_recomendacao(rsi: float, change_1d: float, ma_7: float, ma_30: float) -> str:
    """Gera recomendação baseada em múltiplos indicadores"""
    signals = []
    
    # Sinal RSI
    if rsi < 30:
        signals.append("RSI oversold")
    elif rsi > 70:
        signals.append("RSI overbought")
    
    # Sinal tendência
    if ma_7 > ma_30 and change_1d > 0:
        signals.append("Tendência de alta")
    elif ma_7 < ma_30 and change_1d < 0:
        signals.append("Tendência de baixa")
    
    # Lógica de decisão
    if len(signals) == 0:
        return "MANTER"
    elif "RSI oversold" in signals and "Tendência de alta" in signals:
        return "COMPRA FORTE"
    elif "RSI overbought" in signals and "Tendência de baixa" in signals:
        return "VENDA FORTE"
    elif "RSI oversold" in signals:
        return "COMPRA MODERADA"
    elif "RSI overbought" in signals:
        return "VENDA MODERADA"
    else:
        return "MANTER"

# =====================================================
# 🔮 SISTEMA DE PREVISÃO AVANÇADO
# =====================================================

def gerar_previsao_prophet(df: pd.DataFrame, dias_previsao: int) -> pd.DataFrame:
    """Sistema de previsão com Prophet e fallbacks inteligentes"""
    if df.empty or len(df) < 5:
        logger.warning("⚠️ Dados insuficientes para previsão")
        return pd.DataFrame(columns=["timestamp", "bid", "lower_bound", "upper_bound", "confidence"])
    
    # Prioridade 1: Usar Prophet se disponível
    if PROPHET_AVAILABLE:
        try:
            return _prever_com_prophet_avancado(df, dias_previsao)
        except Exception as e:
            logger.warning(f"⚠️ Prophet falhou, usando fallback: {e}")
    
    # Prioridade 2: Fallback para método estatístico
    return _prever_com_metodo_estatistico(df, dias_previsao)

def _prever_com_prophet_avancado(df: pd.DataFrame, dias_previsao: int) -> pd.DataFrame:
    """Previsão avançada com Facebook Prophet"""
    df_prophet = df[["timestamp", "bid"]].rename(columns={"timestamp": "ds", "bid": "y"})
    
    modelo = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False,
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10.0,
        interval_width=0.95  # Intervalo de confiança de 95%
    )
    
    modelo.fit(df_prophet)
    
    futuro = modelo.make_future_dataframe(periods=dias_previsao, include_history=False)
    forecast = modelo.predict(futuro)
    
    resultado = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(dias_previsao)
    resultado.rename(columns={
        "ds": "timestamp",
        "yhat": "bid", 
        "yhat_lower": "lower_bound",
        "yhat_upper": "upper_bound"
    }, inplace=True)
    
    # Calcular confiança baseada na amplitude do intervalo
    amplitude_relativa = (resultado["upper_bound"] - resultado["lower_bound"]) / resultado["bid"]
    resultado["confidence"] = np.clip(1 - amplitude_relativa, 0.1, 0.95)
    
    logger.info(f"✅ Previsão Prophet gerada para {dias_previsao} dias")
    return resultado

def _prever_com_metodo_estatistico(df: pd.DataFrame, dias_previsao: int) -> pd.DataFrame:
    """Método estatístico fallback com análise de tendência"""
    try:
        # Análise de tendência com regressão linear
        x = np.arange(len(df))
        y = df["bid"].values
        
        if len(y) < 2:
            return pd.DataFrame(columns=["timestamp", "bid", "lower_bound", "upper_bound", "confidence"])
        
        # Regressão linear para tendência
        coef = np.polyfit(x, y, 1)
        tendencia = coef[0]
        
        # Volatilidade histórica para intervalos de confiança
        returns = np.diff(y) / y[:-1]
        volatilidade = np.std(returns) if len(returns) > 0 else 0.1
        
        # Gerar previsões
        ultima_data = df["timestamp"].iloc[-1]
        ultimo_valor = y[-1]
        
        previsoes = []
        for i in range(1, dias_previsao + 1):
            data_previsao = ultima_data + timedelta(days=i)
            valor_previsto = ultimo_valor + (tendencia * i)
            
            # Intervalo de confiança baseado na volatilidade
            margem_erro = valor_previsto * volatilidade * np.sqrt(i)
            
            previsoes.append({
                "timestamp": data_previsao,
                "bid": max(valor_previsto, 0.01),  # Evitar valores negativos
                "lower_bound": max(valor_previsto - margem_erro, 0.01),
                "upper_bound": valor_previsto + margem_erro,
                "confidence": max(0.7 - (volatilidade * 10), 0.3)  # Confiança adaptativa
            })
        
        logger.info(f"✅ Previsão estatística gerada para {dias_previsao} dias")
        return pd.DataFrame(previsoes)
        
    except Exception as e:
        logger.error(f"❌ Erro na previsão estatística: {e}")
        return pd.DataFrame(columns=["timestamp", "bid", "lower_bound", "upper_bound", "confidence"])

# =====================================================
# 📊 SISTEMA DE RELATÓRIOS INTELIGENTES
# =====================================================

def gerar_relatorio_completo(df: pd.DataFrame, df_pred: pd.DataFrame, 
                           moeda: str, indicadores: Dict) -> Dict[str, bytes]:
    """Gera múltiplos formatos de relatório com análise inteligente"""
    relatorios = {}
    
    # Análise consolidadada
    analise_consolidada = _gerar_analise_consolidada(df, df_pred, moeda, indicadores)
    
    # PDF Avançado
    if FPDF_AVAILABLE:
        try:
            relatorios["pdf"] = _gerar_pdf_avancado(df, df_pred, moeda, indicadores, analise_consolidada)
        except Exception as e:
            logger.error(f"❌ Erro ao gerar PDF: {e}")
    
    # Excel com Análise
    if XLSX_AVAILABLE:
        try:
            relatorios["excel"] = _gerar_excel_com_analise(df, df_pred, moeda, indicadores, analise_consolidada)
        except Exception as e:
            logger.error(f"❌ Erro ao gerar Excel: {e}")
    
    # JSON para APIs
    try:
        relatorios["json"] = _gerar_json_analitico(df, df_pred, moeda, indicadores, analise_consolidada)
    except Exception as e:
        logger.error(f"❌ Erro ao gerar JSON: {e}")
    
    logger.info(f"📊 Relatórios gerados: {list(relatorios.keys())}")
    return relatorios

def _gerar_pdf_avancado(df: pd.DataFrame, df_pred: pd.DataFrame, moeda: str, 
                        indicadores: Dict, analise_consolidada: Dict) -> bytes:
    """Gera PDF avançado com análise técnica e previsões"""
    from io import BytesIO
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Análise Técnica - {moeda}", ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"Data: {analise_consolidada.get('data_geracao', 'N/A')}", ln=True)
    pdf.ln(5)
    
    # Seção de Preço Atual
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Preço Atual", ln=True)
    pdf.set_font("Arial", "", 10)
    preco_atual = analise_consolidada.get('preco_atual', 'N/A')
    variacao = analise_consolidada.get('variacao_periodo', 0)
    pdf.cell(0, 5, f"Preço: R$ {preco_atual} | Variação: {variacao:.2f}%", ln=True)
    pdf.ln(3)
    
    # Seção de Indicadores Técnicos
    if indicadores:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Indicadores Técnicos", ln=True)
        pdf.set_font("Arial", "", 9)
        
        pdf.cell(0, 4, f"RSI: {indicadores.get('rsi', 'N/A')}", ln=True)
        pdf.cell(0, 4, f"Volatilidade: {indicadores.get('volatilidade', 'N/A')}%", ln=True)
        pdf.cell(0, 4, f"Tendência: {indicadores.get('tendencia_media', 'N/A')}", ln=True)
        pdf.cell(0, 4, f"Recomendação: {indicadores.get('recomendacao', 'N/A')}", ln=True)
        pdf.ln(3)
    
    # Seção de Previsão
    if not df_pred.empty:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Previsão (Próximos Dias)", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 4, f"Preço Médio Previsto: R$ {df_pred['bid'].mean():.4f}", ln=True)
        pdf.cell(0, 4, f"Confiança Média: {df_pred['confidence'].mean():.2%}", ln=True)
    
    output = BytesIO()
    pdf_bytes = pdf.output()
    return pdf_bytes if isinstance(pdf_bytes, bytes) else pdf_bytes.encode()

def _gerar_excel_com_analise(df: pd.DataFrame, df_pred: pd.DataFrame, moeda: str,
                             indicadores: Dict, analise_consolidada: Dict) -> bytes:
    """Gera Excel com dados históricos, previsões e análise técnica"""
    from io import BytesIO
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # Aba de dados históricos
    df_export = df.copy()
    df_export['timestamp'] = df_export['timestamp'].astype(str)
    df_export.to_excel(writer, sheet_name='Histórico', index=False)
    
    # Aba de previsões
    if not df_pred.empty:
        df_pred_export = df_pred.copy()
        df_pred_export['timestamp'] = df_pred_export['timestamp'].astype(str)
        df_pred_export.to_excel(writer, sheet_name='Previsões', index=False)
    
    # Aba de análise técnica
    if indicadores:
        indicadores_df = pd.DataFrame([indicadores])
        indicadores_df.to_excel(writer, sheet_name='Análise Técnica', index=False)
    
    # Aba de resumo
    resumo_df = pd.DataFrame([analise_consolidada])
    resumo_df.to_excel(writer, sheet_name='Resumo', index=False)
    
    writer.close()
    output.seek(0)
    return output.getvalue()

def _gerar_json_analitico(df: pd.DataFrame, df_pred: pd.DataFrame, moeda: str,
                          indicadores: Dict, analise_consolidada: Dict) -> bytes:
    """Gera JSON com análise completa para APIs"""
    dados_json = {
        "moeda": moeda,
        "analise_consolidada": analise_consolidada,
        "indicadores_tecnicos": indicadores,
        "dados_historicos": {
            "quantidade": len(df),
            "preco_min": float(df['bid'].min()) if not df.empty else None,
            "preco_max": float(df['bid'].max()) if not df.empty else None,
            "preco_medio": float(df['bid'].mean()) if not df.empty else None
        },
        "previsoes": {
            "quantidade": len(df_pred),
            "previsao_media": float(df_pred['bid'].mean()) if not df_pred.empty else None,
            "confianca_media": float(df_pred['confidence'].mean()) if not df_pred.empty else None
        }
    }
    
    return json.dumps(dados_json, indent=2, ensure_ascii=False).encode('utf-8')

def _gerar_analise_consolidada(df: pd.DataFrame, df_pred: pd.DataFrame, 
                              moeda: str, indicadores: Dict) -> Dict:
    """Gera análise consolidada para os relatórios"""
    if df.empty:
        return {}
    
    # Estatísticas básicas
    stats = {
        "moeda": moeda,
        "periodo_analisado": f"{len(df)} dias",
        "data_geracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "preco_atual": float(df["bid"].iloc[-1]),
        "variacao_periodo": float(((df["bid"].iloc[-1] - df["bid"].iloc[0]) / df["bid"].iloc[0]) * 100) if len(df) > 1 else 0
    }
    
    # Adicionar indicadores técnicos
    if indicadores:
        stats["analise_tecnica"] = indicadores
    
    # Adicionar insights da previsão
    if not df_pred.empty:
        stats["previsao"] = {
            "dias_futuro": len(df_pred),
            "previsao_media": float(df_pred["bid"].mean()),
            "confianca_media": float(df_pred["confidence"].mean()),
            "tendencia_previsao": "ALTA" if df_pred["bid"].iloc[-1] > df["bid"].iloc[-1] else "BAIXA"
        }
    
    # Score de investimento (simplificado)
    if indicadores:
        rsi = indicadores.get("rsi", 50)
        tendencia = indicadores.get("tendencia_media", "NEUTRA")
        volatilidade = indicadores.get("volatilidade", 0)
        
        # Lógica de score simples
        score = 50  # Neutro
        
        if rsi < 40 and tendencia == "ALTA":
            score += 30
        elif rsi > 60 and tendencia == "BAIXA":
            score -= 30
        
        # Ajustar por volatilidade
        if volatilidade > 10:  # Alta volatilidade
            score -= 10
        
        stats["score_investimento"] = max(0, min(100, score))
        stats["recomendacao"] = "ALTA" if score > 60 else "BAIXA" if score < 40 else "NEUTRA"
    
    return stats

# =====================================================
# 🔄 FUNÇÕES DE COMPATIBILIDADE
# =====================================================

def gerar_pdf_cache(df: pd.DataFrame, df_pred: pd.DataFrame, moeda: str) -> bytes:
    """Função compatível com interface original"""
    indicadores = calcular_indicadores_tecnicos(df)
    relatorios = gerar_relatorio_completo(df, df_pred, moeda, indicadores)
    return relatorios.get("pdf", b"")

def gerar_excel_cache(df: pd.DataFrame, df_pred: pd.DataFrame) -> bytes:
    """Função compatível com interface original"""
    indicadores = calcular_indicadores_tecnicos(df)
    relatorios = gerar_relatorio_completo(df, df_pred, "MOEDA", indicadores)
    return relatorios.get("excel", b"")

# =====================================================
# 🧪 TESTE DO SISTEMA INTEGRADO
# =====================================================

if __name__ == "__main__":
    print("🧪 TESTE SISTEMA data_utils.py INTEGRADO")
    print("=" * 50)
    
    # Teste de dados
    print("1. 📊 Teste de obtenção de dados...")
    df_test = pegar_dados_cache("BTC", 7)
    print(f"   Dados obtidos: {len(df_test)} registros")
    
    # Teste de análise técnica
    print("\n2. 📈 Teste de análise técnica...")
    if not df_test.empty:
        indicadores = calcular_indicadores_tecnicos(df_test)
        print(f"   Indicadores: {list(indicadores.keys())[:5]}...")
        print(f"   Recomendação: {indicadores.get('recomendacao', 'N/A')}")
    
    # Teste de previsão
    print("\n3. 🔮 Teste de previsão...")
    if not df_test.empty:
        previsao = gerar_previsao_prophet(df_test, 5)
        print(f"   Previsão: {len(previsao)} dias | Confiança: {previsao['confidence'].mean():.2f}")
    
    # Teste de relatório
    print("\n4. 📄 Teste de relatório...")
    if not df_test.empty:
        relatorios = gerar_relatorio_completo(df_test, previsao, "BTC", indicadores)
        print(f"   Formatos gerados: {list(relatorios.keys())}")
    
    print("\n✅ Sistema integrado testado com sucesso!")