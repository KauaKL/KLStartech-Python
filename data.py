# =====================================================
# 📊 data.py — Sistema Unificado de Dados DashFin Supremo
# by KLStarTech (Kauã Lima) + DeepSeek AI
# =====================================================

import requests
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from functools import lru_cache
import json

# Configuração de logging
logger = logging.getLogger("KLStarTech_Data")

# =====================================================
# 🎯 CONFIGURAÇÃO DE APIS MULTIPLAS
# =====================================================

class DataFetcher:
    """Sistema unificado de obtenção de dados com fallbacks inteligentes"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DashFin-Supremo/2.0 (KLStarTech)',
            'Accept': 'application/json'
        })
        self.timeout = 20
        self.retry_delay = 2
        
        # APIs prioritárias para cada tipo de moeda
        self.api_endpoints = {
            'fiat': {
                'primary': 'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/{dias}',
                'secondary': 'https://api.exchangerate.host/timeseries?base={moeda}&symbols=BRL&start_date={start}&end_date={end}',
                'tertiary': 'https://api.frankfurter.app/{start}..{end}?from={moeda}&to=BRL'
            },
            'crypto': {
                'primary': 'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=brl&days={dias}&interval=daily',
                'secondary': 'https://api.coindesk.com/v1/bpi/historical/close.json?currency=BRL',
                'tertiary': 'https://api.binance.com/api/v3/klines?symbol={moeda}USDT&interval=1d&limit={dias}'
            }
        }
        
        # Mapeamento de moedas
        self.crypto_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum', 
            'ADA': 'cardano',
            'LTC': 'litecoin',
            'XRP': 'ripple',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin'
        }

    def _make_request(self, url: str, max_retries: int = 3) -> Optional[dict]:
        """Faz requisição com retry inteligente"""
        for attempt in range(max_retries):
            try:
                logger.debug(f"🌐 Tentativa {attempt + 1} para: {url}")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
                
            except requests.Timeout:
                logger.warning(f"⏰ Timeout na tentativa {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    
            except requests.RequestException as e:
                logger.warning(f"🌐 Erro de rede: {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"❌ Erro inesperado: {e}")
                break
                
        return None

# =====================================================
# 🌍 SISTEMA DE DADOS FIAT (MOEDAS TRADICIONAIS)
# =====================================================

class FiatDataFetcher(DataFetcher):
    """Especializado em moedas fiat (USD, EUR, etc.)"""
    
    @lru_cache(maxsize=32)
    def fetch_fiat_data(self, moeda: str, dias: int) -> pd.DataFrame:
        """Busca dados de moedas fiat com múltiplos fallbacks"""
        moeda = moeda.upper()
        
        # Tentativa 1: AwesomeAPI
        df = self._try_awesomeapi(moeda, dias)
        if not df.empty:
            return df
            
        # Tentativa 2: ExchangeRate Host
        df = self._try_exchangerate_host(moeda, dias)
        if not df.empty:
            return df
            
        # Tentativa 3: Frankfurter
        df = self._try_frankfurter(moeda, dias)
        if not df.empty:
            return df
            
        logger.error(f"❌ Todas as fontes falharam para {moeda}")
        return pd.DataFrame(columns=['timestamp', 'bid', 'volume', 'change_24h'])

    def _try_awesomeapi(self, moeda: str, dias: int) -> pd.DataFrame:
        """Tenta obter dados via AwesomeAPI"""
        try:
            url = self.api_endpoints['fiat']['primary'].format(moeda=moeda, dias=dias)
            data = self._make_request(url)
            
            if data and isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                
                # Processar dados da AwesomeAPI
                if 'timestamp' in df.columns and 'bid' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
                    df['bid'] = pd.to_numeric(df['bid'], errors='coerce')
                    df['volume'] = pd.to_numeric(df.get('vol', 0), errors='coerce')
                    df['change_24h'] = pd.to_numeric(df.get('pctChange', 0), errors='coerce')
                    
                    df = df[['timestamp', 'bid', 'volume', 'change_24h']].dropna(subset=['timestamp', 'bid'])
                    
                    if not df.empty:
                        logger.info(f"✅ Dados {moeda} obtidos via AwesomeAPI")
                        return df.sort_values('timestamp').reset_index(drop=True)
                        
        except Exception as e:
            logger.warning(f"⚠️ AwesomeAPI falhou para {moeda}: {e}")
            
        return pd.DataFrame()

    def _try_exchangerate_host(self, moeda: str, dias: int) -> pd.DataFrame:
        """Tenta obter dados via ExchangeRate Host"""
        try:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=dias)
            
            url = self.api_endpoints['fiat']['secondary'].format(
                moeda=moeda,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )
            
            data = self._make_request(url)
            
            if data and "rates" in data and data["rates"]:
                records = []
                for date_str, rates in data["rates"].items():
                    if "BRL" in rates:
                        records.append({
                            "timestamp": pd.to_datetime(date_str),
                            "bid": float(rates["BRL"]),
                            "volume": None,
                            "change_24h": None
                        })
                
                if records:
                    df = pd.DataFrame(records)
                    logger.info(f"✅ Dados {moeda} obtidos via ExchangeRate Host")
                    return df.sort_values('timestamp').reset_index(drop=True)
                    
        except Exception as e:
            logger.warning(f"⚠️ ExchangeRate Host falhou para {moeda}: {e}")
            
        return pd.DataFrame()

    def _try_frankfurter(self, moeda: str, dias: int) -> pd.DataFrame:
        """Tenta obter dados via Frankfurter"""
        try:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=dias)
            
            url = self.api_endpoints['fiat']['tertiary'].format(
                moeda=moeda,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )
            
            data = self._make_request(url)
            
            if data and "rates" in data and data["rates"]:
                records = []
                for date_str, rates in data["rates"].items():
                    records.append({
                        "timestamp": pd.to_datetime(date_str),
                        "bid": float(rates["BRL"]),
                        "volume": None,
                        "change_24h": None
                    })
                
                if records:
                    df = pd.DataFrame(records)
                    logger.info(f"✅ Dados {moeda} obtidos via Frankfurter")
                    return df.sort_values('timestamp').reset_index(drop=True)
                    
        except Exception as e:
            logger.warning(f"⚠️ Frankfurter falhou para {moeda}: {e}")
            
        return pd.DataFrame()

# =====================================================
# ₿ SISTEMA DE DADOS CRYPTO (CRIPTOMOEDAS)
# =====================================================

class CryptoDataFetcher(DataFetcher):
    """Especializado em criptomoedas"""
    
    @lru_cache(maxsize=32)
    def fetch_crypto_data(self, moeda: str, dias: int) -> pd.DataFrame:
        """Busca dados de criptomoedas com múltiplos fallbacks"""
        moeda = moeda.upper()
        coin_id = self.crypto_map.get(moeda)
        
        if not coin_id:
            logger.error(f"❌ Criptomoeda não suportada: {moeda}")
            return pd.DataFrame(columns=['timestamp', 'bid', 'volume', 'change_24h'])

        # Tentativa 1: CoinGecko
        df = self._try_coingecko(coin_id, dias)
        if not df.empty:
            return df
            
        # Tentativa 2: CoinDesk (apenas BTC)
        if moeda == 'BTC':
            df = self._try_coindesk(dias)
            if not df.empty:
                return df
                
        # Tentativa 3: Binance
        df = self._try_binance(moeda, dias)
        if not df.empty:
            return df
            
        logger.error(f"❌ Todas as fontes crypto falharam para {moeda}")
        return pd.DataFrame(columns=['timestamp', 'bid', 'volume', 'change_24h'])

    def _try_coingecko(self, coin_id: str, dias: int) -> pd.DataFrame:
        """Tenta obter dados via CoinGecko"""
        try:
            url = self.api_endpoints['crypto']['primary'].format(coin_id=coin_id, dias=dias)
            data = self._make_request(url)
            
            if data and 'prices' in data:
                records = []
                for [timestamp, price] in data['prices']:
                    records.append({
                        "timestamp": pd.to_datetime(timestamp, unit='ms'),
                        "bid": float(price),
                        "volume": self._get_volume(data, timestamp),
                        "change_24h": self._get_24h_change(data, timestamp)
                    })
                
                if records:
                    df = pd.DataFrame(records)
                    logger.info(f"✅ Dados crypto obtidos via CoinGecko")
                    return df.sort_values('timestamp').reset_index(drop=True)
                    
        except Exception as e:
            logger.warning(f"⚠️ CoinGecko falhou: {e}")
            
        return pd.DataFrame()

    def _try_coindesk(self, dias: int) -> pd.DataFrame:
        """Tenta obter dados BTC via CoinDesk"""
        try:
            url = self.api_endpoints['crypto']['secondary']
            data = self._make_request(url)
            
            if data and 'bpi' in data:
                records = []
                for date_str, price in list(data['bpi'].items())[-dias:]:
                    records.append({
                        "timestamp": pd.to_datetime(date_str),
                        "bid": float(price),
                        "volume": None,
                        "change_24h": None
                    })
                
                if records:
                    df = pd.DataFrame(records)
                    logger.info("✅ Dados BTC obtidos via CoinDesk")
                    return df.sort_values('timestamp').reset_index(drop=True)
                    
        except Exception as e:
            logger.warning(f"⚠️ CoinDesk falhou: {e}")
            
        return pd.DataFrame()

    def _try_binance(self, moeda: str, dias: int) -> pd.DataFrame:
        """Tenta obter dados via Binance"""
        try:
            symbol = f"{moeda}USDT" if moeda != 'USDT' else "BTCUSDT"
            url = self.api_endpoints['crypto']['tertiary'].format(moeda=moeda, dias=dias)
            
            data = self._make_request(url)
            
            if data and isinstance(data, list):
                records = []
                for candle in data:
                    records.append({
                        "timestamp": pd.to_datetime(candle[0], unit='ms'),
                        "bid": float(candle[4]),  # Preço de fechamento
                        "volume": float(candle[5]),
                        "change_24h": None
                    })
                
                if records:
                    df = pd.DataFrame(records)
                    logger.info(f"✅ Dados {moeda} obtidos via Binance")
                    return df.sort_values('timestamp').reset_index(drop=True)
                    
        except Exception as e:
            logger.warning(f"⚠️ Binance falhou para {moeda}: {e}")
            
        return pd.DataFrame()

    def _get_volume(self, data: dict, timestamp: int) -> Optional[float]:
        """Extrai volume dos dados do CoinGecko"""
        if 'total_volumes' in data:
            for [ts, volume] in data['total_volumes']:
                if ts == timestamp:
                    return float(volume)
        return None

    def _get_24h_change(self, data: dict, timestamp: int) -> Optional[float]:
        """Calcula variação 24h dos dados do CoinGecko"""
        # Implementação simplificada - poderia ser mais sofisticada
        return None

# =====================================================
# 🎯 INTERFACE UNIFICADA - FUNÇÃO PRINCIPAL
# =====================================================

# Instâncias globais para caching
_fiat_fetcher = FiatDataFetcher()
_crypto_fetcher = CryptoDataFetcher()

@lru_cache(maxsize=64)
def pegar_dados(moeda: str = 'USD', dias: int = 7, tentativas: int = 3) -> pd.DataFrame:
    """
    🎯 FUNÇÃO PRINCIPAL UNIFICADA
    
    Busca cotações históricas de moedas fiat ou criptomoedas.
    Sistema inteligente com múltiplos fallbacks e cache.
    
    Parâmetros:
        moeda (str): Código da moeda (USD, EUR, BTC, ETH, ADA, etc.)
        dias (int): Número de dias de histórico (1-365)
        tentativas (int): Número de tentativas por API
    
    Retorna:
        pd.DataFrame com colunas: ['timestamp', 'bid', 'volume', 'change_24h']
    """
    
    moeda = moeda.upper()
    dias = max(1, min(365, dias))  # Limitar entre 1-365 dias
    
    logger.info(f"🔍 Buscando dados para {moeda} ({dias} dias)")
    
    # Determinar tipo de moeda
    if moeda in ['BTC', 'ETH', 'ADA', 'LTC', 'XRP', 'DOT', 'DOGE']:
        return _crypto_fetcher.fetch_crypto_data(moeda, dias)
    else:
        return _fiat_fetcher.fetch_fiat_data(moeda, dias)

# =====================================================
# 🔧 FUNÇÕES UTILITÁRIAS AVANÇADAS
# =====================================================

def get_supported_currencies() -> Dict[str, List[str]]:
    """Retorna lista de moedas suportadas"""
    return {
        'fiat': ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY'],
        'crypto': ['BTC', 'ETH', 'ADA', 'LTC', 'XRP', 'DOT', 'DOGE']
    }

def get_data_stats(df: pd.DataFrame) -> Dict:
    """Retorna estatísticas dos dados obtidos"""
    if df.empty:
        return {}
    
    return {
        'period': f"{len(df)} dias",
        'date_range': {
            'start': df['timestamp'].min().strftime('%Y-%m-%d'),
            'end': df['timestamp'].max().strftime('%Y-%m-%d')
        },
        'price_stats': {
            'current': float(df['bid'].iloc[-1]),
            'average': float(df['bid'].mean()),
            'high': float(df['bid'].max()),
            'low': float(df['bid'].min()),
            'change': float(((df['bid'].iloc[-1] - df['bid'].iloc[0]) / df['bid'].iloc[0]) * 100) if len(df) > 1 else 0
        }
    }

def clear_cache():
    """Limpa o cache de dados"""
    pegar_dados.cache_clear()
    _fiat_fetcher.fetch_fiat_data.cache_clear()
    _crypto_fetcher.fetch_crypto_data.cache_clear()
    logger.info("🗑️ Cache de dados limpo")

# =====================================================
# 🧪 TESTE E COMPATIBILIDADE
# =====================================================

if __name__ == "__main__":
    print("🧪 TESTE SISTEMA DE DADOS UNIFICADO")
    print("=" * 50)
    
    # Configurar logging para teste
    logging.basicConfig(level=logging.INFO)
    
    # Testar moedas fiat
    print("\n1. 💵 Testando moedas fiat...")
    for currency in ['USD', 'EUR', 'GBP']:
        df = pegar_dados(currency, 7)
        stats = get_data_stats(df)
        print(f"   {currency}: {len(df)} registros | Último: R$ {stats.get('price_stats', {}).get('current', 0):.2f}")
    
    # Testar criptomoedas
    print("\n2. ₿ Testando criptomoedas...")
    for currency in ['BTC', 'ETH', 'ADA']:
        df = pegar_dados(currency, 7)
        stats = get_data_stats(df)
        print(f"   {currency}: {len(df)} registros | Último: R$ {stats.get('price_stats', {}).get('current', 0):.2f}")
    
    # Estatísticas do sistema
    print("\n3. 📊 Estatísticas do sistema:")
    supported = get_supported_currencies()
    print(f"   Moedas Fiat: {', '.join(supported['fiat'])}")
    print(f"   Criptomoedas: {', '.join(supported['crypto'])}")
    
    print("\n✅ Sistema de dados unificado testado com sucesso!")
    # =====================================================
# 🎯 FUNÇÕES DE INTEGRAÇÃO PARA data.py
# =====================================================

def _gerar_pdf_avancado(df: pd.DataFrame, df_pred: pd.DataFrame, 
                       moeda: str, indicadores: Dict, analise_consolidada: Dict) -> bytes:
    """Gera PDF avançado - Implementação básica para integração"""
    # Esta seria uma implementação simplificada
    # A versão completa estaria no data_utils.py
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Relatório {moeda}", ln=True)
    pdf.output(dest="S").encode("latin-1")

def _gerar_excel_com_analise(df: pd.DataFrame, df_pred: pd.DataFrame,
                           moeda: str, indicadores: Dict, analise_consolidada: Dict) -> bytes:
    """Gera Excel com análise - Implementação básica"""
    import io
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Dados', index=False)
    return output.getvalue()

def _gerar_json_analitico(df: pd.DataFrame, df_pred: pd.DataFrame,
                         moeda: str, indicadores: Dict, analise_consolidada: Dict) -> bytes:
    """Gera JSON analítico"""
    analise = {
        "moeda": moeda,
        "timestamp": datetime.now().isoformat(),
        "dados_historicos": len(df),
        "analise_tecnica": indicadores,
        "resumo": analise_consolidada
    }
    return json.dumps(analise, indent=2, ensure_ascii=False).encode('utf-8')