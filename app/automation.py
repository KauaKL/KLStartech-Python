# =====================================================
# 🤖 automation.py — Sistema de Automação Inteligente Avançado
# by KLStarTech (Kauã Lima) + DeepSeek AI
# Versão: 4.0 - Com IA Integrada e Workflows Adaptativos
# =====================================================

import os
import sys
import time
import threading
import schedule
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
import logging
import traceback
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import queue
import hashlib
from contextlib import contextmanager
import warnings

# Configura path para import seguro
BASE_DIR = Path(__file__).parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Importações com fallback robusto avançado
try:
    from app.data_utils import (
        pegar_dados_avancado as pegar_dados_cache,
        gerar_previsao_avancada as gerar_previsao_prophet,
        calcular_indicadores_tecnicos,
        gerar_relatorio_completo,
        DataProcessor
    )
    DATA_UTILS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ data_utils não disponível: {e}")
    DATA_UTILS_AVAILABLE = False

try:
    from app.email_utils import (
        send_email_with_attachments, 
        send_financial_report,
        EmailNotifier,
        EmailTemplateManager
    )
    EMAIL_UTILS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ email_utils não disponível: {e}")
    EMAIL_UTILS_AVAILABLE = False

try:
    from app.estelar import AdvancedEstelarAvatar
    from app.llm.core import ask as llm_ask
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Módulos de IA não disponíveis: {e}")
    AI_AVAILABLE = False

# =====================================================
# ⚙️ CONFIGURAÇÃO AVANÇADA EXPANDIDA
# =====================================================

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class AutomationMode(Enum):
    STANDARD = "standard"
    INTELLIGENT = "intelligent"
    ADAPTIVE = "adaptive"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"

class MarketCondition(Enum):
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    CRASH = "crash"
    RALLY = "rally"

@dataclass
class AutomationConfig:
    """Configuração centralizada avançada da automação"""
    # Configurações básicas
    moeda_padrao: str = "USD"
    dias_historico: int = 30
    dias_previsao: int = 7
    
    # Intervalos dinâmicos
    intervalo_verificacao_base: int = 300  # 5 minutos
    intervalo_relatorios_base: int = 3600  # 1 hora
    cooldown_alerta_base: int = 3600  # 1 hora
    
    # Destinos
    email_destino: Optional[str] = None
    webhook_urls: List[str] = field(default_factory=list)
    
    # Modos operacionais
    modo_operacao: AutomationMode = AutomationMode.INTELLIGENT
    alertas_ativos: bool = True
    relatorios_ativos: bool = True
    ia_ativa: bool = True
    
    # Limites e thresholds
    max_alertas_por_hora: int = 5
    limite_volatilidade: float = 0.15
    limite_variacao_diaria: float = 0.05
    
    # Configurações avançadas
    learning_enabled: bool = True
    adaptive_scheduling: bool = True
    risk_management: bool = True

@dataclass
class PerformanceMetrics:
    """Métricas detalhadas de performance"""
    alertas_enviados: int = 0
    relatorios_gerados: int = 0
    erros: int = 0
    uptime: float = 0
    cache_hits: int = 0
    ai_decisions: int = 0
    adaptive_adjustments: int = 0
    response_time_avg: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}

# =====================================================
# 🧠 SISTEMA DE APRENDIZADO E ADAPTAÇÃO
# =====================================================

class LearningSystem:
    """Sistema de aprendizado e adaptação baseado em padrões"""
    
    def __init__(self):
        self.pattern_database = {}
        self.performance_history = []
        self.adaptive_rules = {}
        self.learning_rate = 0.1
        
    def analyze_pattern(self, market_data: pd.DataFrame, alert_data: Dict) -> Dict:
        """Analisa padrões de mercado e eficácia de alertas"""
        if market_data.empty:
            return {}
            
        try:
            # Análise de padrões temporais
            patterns = {
                "volatility_clusters": self._detect_volatility_clusters(market_data),
                "time_of_day_effect": self._analyze_time_of_day_patterns(market_data),
                "alert_effectiveness": self._calculate_alert_effectiveness(alert_data),
                "optimal_timing": self._find_optimal_timing(market_data)
            }
            
            # Aprender com padrões
            self._update_learning_rules(patterns)
            
            return patterns
            
        except Exception as e:
            logging.error(f"❌ Erro na análise de padrões: {e}")
            return {}
    
    def _detect_volatility_clusters(self, df: pd.DataFrame) -> Dict:
        """Detecta clusters de volatilidade"""
        if len(df) < 10:
            return {}
            
        returns = np.diff(df['bid'].values) / df['bid'].values[:-1]
        volatility = np.std(returns) * 100
        
        return {
            "current_volatility": volatility,
            "volatility_regime": "high" if volatility > 2 else "low",
            "cluster_detected": len([r for r in returns if abs(r) > 0.02]) > 3
        }
    
    def _analyze_time_of_day_patterns(self, df: pd.DataFrame) -> Dict:
        """Analisa padrões por horário do dia"""
        if 'timestamp' not in df.columns:
            return {}
            
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_volatility = df.groupby('hour')['bid'].std() / df.groupby('hour')['bid'].mean()
        
        return {
            "high_volatility_hours": hourly_volatility.nlargest(3).index.tolist(),
            "low_volatility_hours": hourly_volatility.nsmallest(3).index.tolist()
        }
    
    def _calculate_alert_effectiveness(self, alert_data: Dict) -> float:
        """Calcula eficácia histórica dos alertas"""
        if not alert_data:
            return 0.5
            
        successful_alerts = len([a for a in alert_data if a.get('successful', False)])
        total_alerts = len(alert_data)
        
        return successful_alerts / total_alerts if total_alerts > 0 else 0.5
    
    def _find_optimal_timing(self, df: pd.DataFrame) -> Dict:
        """Encontra timing ótimo para operações"""
        if len(df) < 20:
            return {}
            
        # Análise simplificada de timing
        returns = np.diff(df['bid'].values) / df['bid'].values[:-1]
        best_hours = []
        
        return {
            "suggested_check_interval": 300,  # 5 minutos
            "best_hours": best_hours,
            "avoid_hours": []
        }
    
    def _update_learning_rules(self, patterns: Dict):
        """Atualiza regras de aprendizado"""
        # Implementação simplificada de reinforcement learning
        if "alert_effectiveness" in patterns:
            effectiveness = patterns["alert_effectiveness"]
            self.learning_rate = max(0.01, min(0.5, effectiveness))

class AdaptiveScheduler:
    """Sistema de agendamento adaptativo baseado em condições"""
    
    def __init__(self, learning_system: LearningSystem):
        self.learning_system = learning_system
        self.current_intervals = {}
        self.market_conditions = MarketCondition.SIDEWAYS
        
    def calculate_optimal_interval(self, base_interval: int, market_condition: MarketCondition) -> int:
        """Calcula intervalo ótimo baseado nas condições"""
        multipliers = {
            MarketCondition.HIGH_VOLATILITY: 0.5,    # Verificar mais frequentemente
            MarketCondition.LOW_VOLATILITY: 2.0,     # Verificar menos frequentemente
            MarketCondition.CRASH: 0.25,             # Verificar muito frequentemente
            MarketCondition.RALLY: 0.75,             # Verificar frequentemente
            MarketCondition.SIDEWAYS: 1.5,           # Verificar menos
            MarketCondition.BULL_MARKET: 1.0,
            MarketCondition.BEAR_MARKET: 1.0
        }
        
        multiplier = multipliers.get(market_condition, 1.0)
        optimal_interval = int(base_interval * multiplier)
        
        # Limites mínimos e máximos
        return max(60, min(3600, optimal_interval))
    
    def adjust_schedule_based_on_learning(self, patterns: Dict) -> Dict[str, int]:
        """Ajusta agendamento baseado em aprendizado"""
        adjustments = {}
        
        if "optimal_timing" in patterns:
            timing = patterns["optimal_timing"]
            adjustments['check_interval'] = timing.get('suggested_check_interval', 300)
        
        if "volatility_clusters" in patterns:
            volatility_data = patterns["volatility_clusters"]
            if volatility_data.get('volatility_regime') == 'high':
                adjustments['check_interval'] = 120  # 2 minutos em alta volatilidade
        
        return adjustments

# =====================================================
# 🤖 SISTEMA DE IA INTEGRADO
# =====================================================

class AIDecisionEngine:
    """Motor de decisão por IA para automação inteligente"""
    
    def __init__(self):
        self.decision_history = []
        self.confidence_threshold = 0.7
        
    async def analyze_market_situation(self, market_data: Dict, alert_context: Dict) -> Dict:
        """Analisa situação de mercado usando IA"""
        if not AI_AVAILABLE:
            return self._fallback_analysis(market_data, alert_context)
        
        try:
            prompt = self._create_analysis_prompt(market_data, alert_context)
            
            response = llm_ask(
                prompt=prompt,
                system_prompt="Você é um analista financeiro especializado em automação de trading. Analise a situação e recomende ações.",
                model="local"  # Usar modelo local para velocidade
            )
            
            analysis = self._parse_ai_response(response.get('text', ''))
            self.decision_history.append({
                "timestamp": datetime.now(),
                "analysis": analysis,
                "confidence": analysis.get('confidence', 0.5)
            })
            
            return analysis
            
        except Exception as e:
            logging.error(f"❌ Erro na análise por IA: {e}")
            return self._fallback_analysis(market_data, alert_context)
    
    def _create_analysis_prompt(self, market_data: Dict, alert_context: Dict) -> str:
        """Cria prompt para análise de IA"""
        return f"""
        ANALISE DE MERCADO PARA AUTOMAÇÃO
        
        Dados de Mercado:
        - Moeda: {market_data.get('moeda', 'N/A')}
        - Preço Atual: {market_data.get('current_price', 0):.4f}
        - Variação 1D: {market_data.get('change_1d', 0):.2f}%
        - Volatilidade: {market_data.get('volatility_ratio', 1):.2f}x
        - Tendência: {market_data.get('trend', 'neutral')}
        
        Contexto do Alerta:
        - Tipo: {alert_context.get('tipo', 'N/A')}
        - Valor Alvo: {alert_context.get('valor_alvo', 0):.4f}
        - Motivo: {alert_context.get('motivo', 'N/A')}
        
        Perguntas:
        1. Este é um bom momento para enviar alerta?
        2. Qual a confiança desta decisão (0-1)?
        3. Recomenda algum ajuste no timing?
        4. Há riscos significativos?
        
        Responda em formato JSON:
        {{
            "should_alert": true/false,
            "confidence": 0.85,
            "recommended_timing": "immediate|delayed|avoid",
            "risk_level": "low|medium|high",
            "reasoning": "explicação detalhada"
        }}
        """
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parseia resposta da IA"""
        try:
            # Tentar extrair JSON da resposta
            lines = response_text.strip().split('\n')
            json_lines = [line for line in lines if line.strip().startswith('{')]
            
            if json_lines:
                return json.loads(json_lines[0])
            else:
                # Fallback para análise simples
                return {
                    "should_alert": "alerta" in response_text.lower(),
                    "confidence": 0.6,
                    "recommended_timing": "immediate",
                    "risk_level": "medium",
                    "reasoning": "Análise automática"
                }
                
        except Exception:
            return self._create_fallback_analysis()
    
    def _fallback_analysis(self, market_data: Dict, alert_context: Dict) -> Dict:
        """Análise de fallback quando IA não está disponível"""
        volatility = market_data.get('volatility_ratio', 1)
        change_1d = market_data.get('change_1d', 0)
        
        should_alert = volatility < 2 and abs(change_1d) < 10
        confidence = max(0.3, 1 - (volatility / 5))
        
        return {
            "should_alert": should_alert,
            "confidence": confidence,
            "recommended_timing": "immediate" if should_alert else "avoid",
            "risk_level": "high" if volatility > 2 else "medium",
            "reasoning": "Análise baseada em volatilidade e variação diária"
        }
    
    def _create_fallback_analysis(self) -> Dict:
        """Cria análise de fallback genérica"""
        return {
            "should_alert": True,
            "confidence": 0.5,
            "recommended_timing": "immediate",
            "risk_level": "medium",
            "reasoning": "Sistema de fallback ativado"
        }

# =====================================================
# 🔔 SISTEMA DE ALERTAS INTELIGENTE AVANÇADO
# =====================================================

class SmartAlertSystem:
    """Sistema de alertas inteligente com IA integrada"""
    
    def __init__(self, manager: 'AutomationManager'):
        self.manager = manager
        self.alert_rules = {}
        self.learning_system = LearningSystem()
        self.ai_engine = AIDecisionEngine()
        
        # Cache inteligente para decisões
        self.decision_cache = {}
        self.cache_duration = timedelta(minutes=10)
    
    def _alert_key(self, moeda: str, valor_alvo: float, tipo: str) -> str:
        """Gera chave única para cache de alertas"""
        content = f"{moeda.upper()}_{valor_alvo:.6f}_{tipo}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def should_send_alert(self, moeda: str, valor_alvo: float, 
                              motivo: str, contexto: Dict) -> Tuple[bool, float]:
        """Decide se deve enviar alerta usando IA e aprendizado"""
        cache_key = self._alert_key(moeda, valor_alvo, motivo)
        
        # Verificar cache primeiro
        cached_decision = self._get_cached_decision(cache_key)
        if cached_decision is not None:
            self.manager.performance_metrics.cache_hits += 1
            return cached_decision
        
        # Cooldown básico
        if not self._check_cooldown(moeda, valor_alvo):
            return False, 0.0
        
        # Limite de frequência
        if not self._check_frequency_limits(moeda):
            return False, 0.0
        
        # Análise de IA
        market_data = self.analyze_market_conditions(self.manager.get_market_data(moeda), moeda)
        alert_context = {
            "moeda": moeda,
            "valor_alvo": valor_alvo,
            "motivo": motivo,
            "contexto": contexto
        }
        
        ai_analysis = await self.ai_engine.analyze_market_situation(market_data, alert_context)
        
        should_alert = ai_analysis.get("should_alert", False)
        confidence = ai_analysis.get("confidence", 0.5)
        
        # Cache da decisão
        self._cache_decision(cache_key, (should_alert, confidence))
        
        if should_alert:
            self.manager.performance_metrics.ai_decisions += 1
        
        return should_alert, confidence
    
    def _get_cached_decision(self, cache_key: str) -> Optional[Tuple[bool, float]]:
        """Recupera decisão do cache"""
        if cache_key in self.decision_cache:
            decision, timestamp = self.decision_cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return decision
            else:
                del self.decision_cache[cache_key]
        return None
    
    def _cache_decision(self, cache_key: str, decision: Tuple[bool, float]):
        """Armazena decisão no cache"""
        self.decision_cache[cache_key] = (decision, datetime.now())
    
    def _check_cooldown(self, moeda: str, valor_alvo: float) -> bool:
        """Verifica cooldown básico"""
        key = f"{moeda.upper()}__{valor_alvo:.6f}"
        last_time = self.manager.last_alert_times.get(key)
        
        if last_time and (datetime.now() - last_time).total_seconds() < self.manager.config.cooldown_alerta_base:
            return False
        
        return True
    
    def _check_frequency_limits(self, moeda: str) -> bool:
        """Verifica limites de frequência"""
        recent_alerts = [
            alert for alert in self.manager.alert_history 
            if alert["moeda"] == moeda and 
            (datetime.now() - datetime.strptime(alert["data_hora"], "%Y-%m-%d %H:%M:%S")).total_seconds() < 3600
        ]
        
        return len(recent_alerts) < self.manager.config.max_alertas_por_hora
    
    def analyze_market_conditions(self, df: pd.DataFrame, moeda: str) -> Dict:
        """Analisa condições de mercado para alertas inteligentes"""
        if df.empty or len(df) < 2:
            return {}
            
        try:
            current_price = df["bid"].iloc[-1]
            prev_price = df["bid"].iloc[-2] if len(df) >= 2 else current_price
            
            # Calcular métricas avançadas
            change_1d = ((current_price - prev_price) / prev_price) * 100
            
            # Detectar regime de volatilidade
            if len(df) >= 10:
                recent_volatility = df["bid"].tail(10).std() / df["bid"].tail(10).mean() * 100
                avg_volatility = df["bid"].std() / df["bid"].mean() * 100
                volatility_ratio = recent_volatility / avg_volatility if avg_volatility > 0 else 1
                
                # Detectar tendência
                prices = df["bid"].values
                if len(prices) >= 5:
                    sma_5 = np.mean(prices[-5:])
                    sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else sma_5
                    trend = "up" if sma_5 > sma_20 else "down"
                else:
                    trend = "neutral"
            else:
                volatility_ratio = 1
                trend = "neutral"
            
            # Análise de padrões
            patterns = self.learning_system.analyze_pattern(df, self.manager.alert_history)
            
            market_state = {
                "moeda": moeda,
                "current_price": current_price,
                "change_1d": change_1d,
                "volatility_ratio": volatility_ratio,
                "trend": trend,
                "patterns": patterns,
                "last_analysis": datetime.now().isoformat(),
                "market_condition": self._determine_market_condition(volatility_ratio, change_1d)
            }
            
            # Atualizar estado do mercado
            self.manager.market_state[moeda] = market_state
            
            return market_state
            
        except Exception as e:
            self.manager.logger.error(f"❌ Erro na análise de mercado: {e}")
            return {}
    
    def _determine_market_condition(self, volatility_ratio: float, change_1d: float) -> MarketCondition:
        """Determina condição atual do mercado"""
        if volatility_ratio > 3:
            return MarketCondition.CRASH if change_1d < -5 else MarketCondition.RALLY
        elif volatility_ratio > 2:
            return MarketCondition.HIGH_VOLATILITY
        elif volatility_ratio < 0.5:
            return MarketCondition.LOW_VOLATILITY
        elif abs(change_1d) < 1:
            return MarketCondition.SIDEWAYS
        else:
            return MarketCondition.BULL_MARKET if change_1d > 0 else MarketCondition.BEAR_MARKET
    
    def mark_alert_sent(self, moeda: str, valor_alvo: float, 
                       canais: str, priority: AlertPriority = AlertPriority.MEDIUM,
                       confidence: float = 0.5, ai_decision: bool = False):
        """Registra alerta enviado com metadados avançados"""
        key = f"{moeda.upper()}__{valor_alvo:.6f}"
        self.manager.last_alert_times[key] = datetime.now()
        
        log_entry = {
            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "moeda": moeda,
            "valor_alvo": round(valor_alvo, 6),
            "canais": canais,
            "priority": priority.value,
            "confidence": confidence,
            "ai_decision": ai_decision,
            "contexto": self.manager.market_state.get(moeda, {}),
            "successful": confidence > 0.6  # Considerado bem-sucedido se alta confiança
        }
        
        self.manager.alert_history.append(log_entry)
        self.manager.performance_metrics.alertas_enviados += 1
        
        self.manager.logger.info(
            f"🔔 Alerta {priority.value.upper()} (conf: {confidence:.2f}) registrado: "
            f"{moeda} - {valor_alvo:.4f} via {canais}"
        )
    
    def get_alert_history(self, hours: int = 24, min_confidence: float = 0.0) -> List[Dict]:
        """Retorna histórico de alertas filtrado"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.manager.alert_history
            if (datetime.strptime(alert["data_hora"], "%Y-%m-%d %H:%M:%S") >= cutoff_time and
                alert.get("confidence", 1.0) >= min_confidence)
        ]

# =====================================================
# 📊 SISTEMA DE RELATÓRIOS AUTOMÁTICOS AVANÇADO
# =====================================================

class AdvancedReportGenerator:
    """Sistema avançado de geração de relatórios com IA"""
    
    def __init__(self, manager: 'AutomationManager'):
        self.manager = manager
        self.reports_folder = Path("reports")
        self.reports_folder.mkdir(exist_ok=True)
        self.template_manager = self._initialize_templates()
        
    def _initialize_templates(self):
        """Inicializa gerenciador de templates"""
        # Em uma implementação real, carregaria templates de arquivos
        return {
            "daily_report": self._daily_report_template,
            "weekly_analysis": self._weekly_analysis_template,
            "alert_summary": self._alert_summary_template
        }
    
    def gerar_relatorios_avancados(self, moeda: str, dias: int = None, 
                                 report_type: str = "comprehensive") -> Dict[str, bytes]:
        """Gera múltiplos formatos de relatório com análise avançada"""
        if dias is None:
            dias = self.manager.config.dias_historico
            
        if not DATA_UTILS_AVAILABLE:
            self.manager.logger.error("❌ Módulo de dados não disponível")
            return {}
        
        try:
            start_time = time.time()
            
            # Obter dados com cache inteligente
            df = pegar_dados_cache(moeda, dias)
            if df.empty:
                self.manager.logger.warning(f"⚠️ Nenhum dado disponível para {moeda}")
                return {}
            
            # Análise avançada
            market_analysis = self.manager.alert_system.analyze_market_conditions(df, moeda)
            patterns = self.manager.learning_system.analyze_pattern(df, self.manager.alert_history)
            
            # Gerar previsão
            df_pred = gerar_previsao_prophet(df, self.manager.config.dias_previsao)
            
            # Calcular indicadores avançados
            indicadores = calcular_indicadores_tecnicos(df)
            
            # Adicionar análises personalizadas
            indicadores["market_condition"] = market_analysis.get("market_condition", "unknown")
            indicadores["patterns"] = patterns
            
            # Gerar relatórios completos
            relatorios = gerar_relatorio_completo(df, df_pred, moeda, indicadores)
            
            # Gerar relatório com IA se disponível
            if AI_AVAILABLE and self.manager.config.ia_ativa:
                ai_insights = self._generate_ai_insights(df, market_analysis, patterns)
                relatorios["ai_analysis"] = self._format_ai_insights(ai_insights)
            
            # Salvar localmente com versionamento
            self._salvar_relatorios_locais(moeda, relatorios, report_type)
            
            # Métricas de performance
            execution_time = time.time() - start_time
            self.manager.performance_metrics.response_time_avg = (
                self.manager.performance_metrics.response_time_avg * 
                self.manager.performance_metrics.relatorios_gerados + execution_time
            ) / (self.manager.performance_metrics.relatorios_gerados + 1)
            
            self.manager.performance_metrics.relatorios_gerados += 1
            self.manager.logger.info(f"📊 Relatórios avançados gerados para {moeda} em {execution_time:.2f}s")
            
            return relatorios
            
        except Exception as e:
            self.manager.logger.error(f"❌ Erro ao gerar relatórios avançados: {e}")
            return {}
    
    def _generate_ai_insights(self, df: pd.DataFrame, market_analysis: Dict, patterns: Dict) -> Dict:
        """Gera insights usando IA"""
        try:
            prompt = f"""
            Gere insights sobre o mercado baseado nos dados:
            
            Análise de Mercado:
            {json.dumps(market_analysis, indent=2)}
            
            Padrões Detectados:
            {json.dumps(patterns, indent=2)}
            
            Forneça:
            1. Resumo executivo
            2. Recomendações de ação
            3. Riscos identificados
            4. Previsão de curto prazo
            """
            
            response = llm_ask(
                prompt=prompt,
                system_prompt="Você é um analista financeiro especializado em relatórios de mercado.",
                model="local"
            )
            
            return {
                "insights": response.get('text', ''),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.manager.logger.warning(f"⚠️ IA não disponível para insights: {e}")
            return {"insights": "Análise tradicional", "generated_at": datetime.now().isoformat()}
    
    def _format_ai_insights(self, ai_insights: Dict) -> bytes:
        """Formata insights de IA para relatório"""
        insights_text = ai_insights.get("insights", "")
        return f"""
        ANÁLISE AVANÇADA COM IA
        ======================
        
        {insights_text}
        
        Gerado em: {ai_insights.get('generated_at', 'N/A')}
        """.encode()
    
    def _salvar_relatorios_locais(self, moeda: str, relatorios: Dict[str, bytes], report_type: str):
        """Salva relatórios localmente com versionamento avançado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for formato, conteudo in relatorios.items():
            if conteudo:
                filename = f"{moeda}_{report_type}_{timestamp}.{formato}"
                filepath = self.reports_folder / filename
                
                try:
                    with open(filepath, "wb") as f:
                        f.write(conteudo)
                    
                    # Log de sucesso
                    self.manager.logger.debug(f"💾 Relatório {formato} salvo: {filepath}")
                    
                except Exception as e:
                    self.manager.logger.error(f"❌ Erro ao salvar {formato}: {e}")
    
    def _daily_report_template(self, data: Dict) -> str:
        """Template para relatório diário"""
        return f"""
        RELATÓRIO DIÁRIO - {data.get('moeda', 'N/A')}
        =================================
        
        Data: {datetime.now().strftime('%Y-%m-%d')}
        Moeda: {data.get('moeda', 'N/A')}
        
        RESUMO EXECUTIVO:
        - Preço Atual: R$ {data.get('current_price', 0):.4f}
        - Variação 1D: {data.get('change_1d', 0):.2f}%
        - Condição: {data.get('market_condition', 'N/A')}
        
        ANÁLISE TÉCNICA:
        {json.dumps(data.get('indicators', {}), indent=2)}
        
        RECOMENDAÇÕES:
        - Manter monitoramento ativo
        - Ajustar alertas conforme volatilidade
        """
    
    def _weekly_analysis_template(self, data: Dict) -> str:
        """Template para análise semanal"""
        return "Template para análise semanal"
    
    def _alert_summary_template(self, data: Dict) -> str:
        """Template para sumário de alertas"""
        return "Template para sumário de alertas"

# =====================================================
# 📬 SISTEMA DE ENVIO AUTOMÁTICO AVANÇADO
# =====================================================

class AdvancedEmailAutomation:
    """Sistema de automação de e-mails avançado"""
    
    def __init__(self, manager: 'AutomationManager'):
        self.manager = manager
        self.report_generator = AdvancedReportGenerator(manager)
        
    async def enviar_relatorio_inteligente(self, moeda: str = None, dias: int = None):
        """Envia relatório inteligente por e-mail com análise contextual"""
        if not EMAIL_UTILS_AVAILABLE:
            self.manager.logger.error("❌ Módulo de e-mail não disponível")
            return False
            
        moeda = moeda or self.manager.config.moeda_padrao
        email_to = self.manager.config.email_destino
        
        if not email_to:
            self.manager.logger.warning("⚠️ Nenhum e-mail destino configurado")
            return False
        
        try:
            # Análise de mercado para personalização
            market_data = self.manager.get_market_data(moeda)
            market_analysis = self.manager.alert_system.analyze_market_conditions(market_data, moeda)
            
            # Gerar relatórios avançados
            relatorios = self.report_generator.gerar_relatorios_avancados(moeda, dias)
            if not relatorios:
                return False
            
            # Personalizar conteúdo baseado na análise
            subject, body = self._personalize_email_content(moeda, market_analysis)
            
            # Preparar anexos
            attachments = []
            for formato, conteudo in relatorios.items():
                if formato == "pdf" and conteudo:
                    attachments.append(
                        (f"{moeda}_relatorio_avancado.pdf", conteudo, "application/pdf")
                    )
                elif formato == "excel" and conteudo:
                    attachments.append(
                        (f"{moeda}_dados_detalhados.xlsx", conteudo, 
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    )
                elif formato == "ai_analysis" and conteudo:
                    attachments.append(
                        (f"{moeda}_analise_ia.txt", conteudo, "text/plain")
                    )
            
            # Enviar e-mail
            success, message = send_email_with_attachments(
                email_to, subject, body, attachments
            )
            
            if success:
                self.manager.logger.info(f"✅ Relatório inteligente {moeda} enviado para {email_to}")
                return True
            else:
                self.manager.logger.error(f"❌ Falha no envio: {message}")
                return False
                
        except Exception as e:
            self.manager.logger.error(f"❌ Erro no envio inteligente: {e}")
            return False
    
    def _personalize_email_content(self, moeda: str, market_analysis: Dict) -> Tuple[str, str]:
        """Personaliza conteúdo do e-mail baseado na análise"""
        condition = market_analysis.get("market_condition", "unknown")
        change_1d = market_analysis.get("change_1d", 0)
        volatility = market_analysis.get("volatility_ratio", 1)
        
        # Subject personalizado
        if condition == MarketCondition.CRASH.value:
            subject = f"🚨 ALERTA CRÍTICO {moeda} - Queda Acentuada Detectada"
        elif condition == MarketCondition.RALLY.value:
            subject = f"📈 ALTA EXPRESSIVA {moeda} - Oportunidade Identificada"
        elif volatility > 2:
            subject = f"⚡ ALTA VOLATILIDADE {moeda} - Mercado Instável"
        else:
            subject = f"📊 Relatório {moeda} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Body personalizado
        body = f"""
        RELATÓRIO INTELIGENTE — DashFin Supremo AI
        ==========================================
        
        Moeda: {moeda}
        Condição: {condition}
        Variação 1D: {change_1d:.2f}%
        Volatilidade: {volatility:.2f}x normal
        
        ANÁLISE AUTOMÁTICA:
        {self._generate_situation_analysis(market_analysis)}
        
        Este relatório foi gerado automaticamente pelo sistema avançado
        KLStarTech DashFin Supremo com análise de IA integrada.
        
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return subject, body
    
    def _generate_situation_analysis(self, market_analysis: Dict) -> str:
        """Gera análise situacional automática"""
        condition = market_analysis.get("market_condition", "unknown")
        
        analysis_map = {
            MarketCondition.CRASH.value: "❌ Mercado em forte queda - considere medidas defensivas",
            MarketCondition.RALLY.value: "✅ Mercado em alta expressiva - oportunidades de ganho",
            MarketCondition.HIGH_VOLATILITY.value: "⚡ Alta volatilidade - cuidado com operações",
            MarketCondition.LOW_VOLATILITY.value: "😊 Baixa volatilidade - ambiente estável",
            MarketCondition.SIDEWAYS.value: "➡️ Mercado lateral - aguarde definição de tendência",
            MarketCondition.BULL_MARKET.value: "📈 Tendência de alta consolidada",
            MarketCondition.BEAR_MARKET.value: "📉 Tendência de baixa consolidada"
        }
        
        return analysis_map.get(condition, "🔍 Análise em andamento...")
    
    async def enviar_alerta_inteligente(self, moeda: str, valor_atual: float, 
                                      valor_alvo: float, motivo: str, confidence: float = 0.5):
        """Envia alerta inteligente com análise contextual avançada"""
        if not EMAIL_UTILS_AVAILABLE or not self.manager.email_notifier:
            return False
        
        # Análise de mercado para contextualização
        market_data = self.manager.alert_system.market_state.get(moeda, {})
        
        # Determinar prioridade baseada em múltiplos fatores
        priority = self._calculate_alert_priority(market_data, confidence)
        
        # Gerar mensagem contextual avançada
        message = self._generate_contextual_alert_message(moeda, valor_atual, valor_alvo, motivo, market_data, confidence)
        
        title = f"🎯 Alerta {moeda} - {motivo} (Conf: {confidence:.0%})"
        success = self.manager.email_notifier.send_alert(title, message, priority.value)
        
        if success:
            self.manager.alert_system.mark_alert_sent(
                moeda, valor_alvo, "email", priority, confidence, ai_decision=True
            )
        
        return success
    
    def _calculate_alert_priority(self, market_data: Dict, confidence: float) -> AlertPriority:
        """Calcula prioridade do alerta baseada em múltiplos fatores"""
        volatility = market_data.get("volatility_ratio", 1)
        change_1d = market_data.get("change_1d", 0)
        
        if confidence > 0.8 and (volatility > 2 or abs(change_1d) > 5):
            return AlertPriority.CRITICAL
        elif confidence > 0.7 and (volatility > 1.5 or abs(change_1d) > 3):
            return AlertPriority.HIGH
        elif confidence > 0.6:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW
    
    def _generate_contextual_alert_message(self, moeda: str, valor_atual: float, 
                                         valor_alvo: float, motivo: str, 
                                         market_data: Dict, confidence: float) -> str:
        """Gera mensagem de alerta contextual avançada"""
        return f"""
        🚨 ALERTA INTELIGENTE {moeda}/BRL
        ================================
        
        DADOS DO ALERTA:
        - Valor Atual: R$ {valor_atual:.4f}
        - Valor Alvo: R$ {valor_alvo:.4f}
        - Motivo: {motivo}
        - Confiança: {confidence:.0%}
        
        CONTEXTO DE MERCADO:
        - Variação 1D: {market_data.get('change_1d', 0):.2f}%
        - Volatilidade: {market_data.get('volatility_ratio', 1):.2f}x normal
        - Tendência: {market_data.get('trend', 'estável')}
        - Condição: {market_data.get('market_condition', 'N/A')}
        
        ANÁLISE AUTOMÁTICA:
        {self._generate_alert_analysis(market_data, confidence)}
        
        RECOMENDAÇÃO DO SISTEMA:
        {self._generate_alert_recommendation(market_data, confidence)}
        
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Sistema: KLStarTech DashFin Supremo AI v4.0
        """
    
    def _generate_alert_analysis(self, market_data: Dict, confidence: float) -> str:
        """Gera análise automática para o alerta"""
        if confidence > 0.8:
            return "✅ Sinal de alta confiabilidade - ação recomendada"
        elif confidence > 0.6:
            return "⚠️ Sinal moderado - considere ação com cautela"
        else:
            return "🔍 Sinal de baixa confiança - mantenha monitoramento"
    
    def _generate_alert_recommendation(self, market_data: Dict, confidence: float) -> str:
        """Gera recomendação automática para o alerta"""
        condition = market_data.get("market_condition", "unknown")
        
        if condition == MarketCondition.CRASH.value and confidence > 0.7:
            return "🚨 CONSIDERE POSIÇÃO DEFENSIVA - Mercado em queda"
        elif condition == MarketCondition.RALLY.value and confidence > 0.7:
            return "📈 OPORTUNIDADE DE COMPRA - Mercado em alta"
        elif confidence > 0.8:
            return "🎯 AÇÃO RECOMENDADA - Sinal forte identificado"
        else:
            return "🤔 MANTENHA MONITORAMENTO - Aguarde confirmação"

# =====================================================
# ⏱️ SISTEMA DE AGENDAMENTO INTELIGENTE AVANÇADO
# =====================================================

class AdvancedSmartScheduler:
    """Sistema de agendamento inteligente adaptativo"""
    
    def __init__(self, manager: 'AutomationManager'):
        self.manager = manager
        self.learning_system = LearningSystem()
        self.adaptive_scheduler = AdaptiveScheduler(self.learning_system)
        self.jobs = {}
        self.adaptive_intervals = {}
        
    def agendar_tarefa_adaptativa(self, tarefa: Callable, intervalo_base: int, 
                                nome: str, moeda: str = None):
        """Agenda tarefa com intervalos adaptativos"""
        # Calcular intervalo ótimo baseado nas condições
        market_condition = self._get_current_market_condition(moeda)
        intervalo_otimo = self.adaptive_scheduler.calculate_optimal_interval(
            intervalo_base, market_condition
        )
        
        self.jobs[nome] = {
            "tarefa": tarefa,
            "intervalo_base": intervalo_base,
            "intervalo_atual": intervalo_otimo,
            "moeda": moeda,
            "ultima_execucao": None,
            "proxima_execucao": datetime.now() + timedelta(seconds=intervalo_otimo),
            "execution_count": 0,
            "adaptive_enabled": True
        }
        
        self.adaptive_intervals[nome] = intervalo_otimo
        self.manager.performance_metrics.adaptive_adjustments += 1
        
        self.manager.logger.info(
            f"⏰ Tarefa {nome} agendada com intervalo adaptativo: {intervalo_otimo}s "
            f"(condição: {market_condition.value})"
        )
    
    def agendar_tarefa_periodica(self, tarefa: Callable, intervalo: int, nome: str):
        """Agenda tarefa periódica fixa"""
        self.jobs[nome] = {
            "tarefa": tarefa,
            "intervalo_base": intervalo,
            "intervalo_atual": intervalo,
            "moeda": None,
            "ultima_execucao": None,
            "proxima_execucao": datetime.now() + timedelta(seconds=intervalo),
            "execution_count": 0,
            "adaptive_enabled": False
        }
    
    def _get_current_market_condition(self, moeda: str) -> MarketCondition:
        """Obtém condição atual do mercado"""
        if not moeda or moeda not in self.manager.market_state:
            return MarketCondition.SIDEWAYS
            
        market_data = self.manager.market_state[moeda]
        return MarketCondition(market_data.get("market_condition", MarketCondition.SIDEWAYS.value))
    
    def executar_tarefas_pendentes(self):
        """Executa tarefas pendentes com ajustes adaptativos"""
        agora = datetime.now()
        
        for nome, job in self.jobs.items():
            if job["proxima_execucao"] and agora >= job["proxima_execucao"]:
                try:
                    start_time = time.time()
                    
                    self.manager.logger.info(f"⏰ Executando tarefa adaptativa: {nome}")
                    job["tarefa"]()
                    
                    # Atualizar métricas
                    job["ultima_execucao"] = agora
                    job["execution_count"] += 1
                    execution_time = time.time() - start_time
                    
                    # Ajuste adaptativo se habilitado
                    if job["adaptive_enabled"] and job["moeda"]:
                        self._adjust_interval_based_on_performance(nome, job, execution_time)
                    
                    # Recalcular próxima execução
                    job["proxima_execucao"] = agora + timedelta(seconds=job["intervalo_atual"])
                    
                except Exception as e:
                    self.manager.logger.error(f"❌ Erro na tarefa {nome}: {e}")
                    self.manager.performance_metrics.erros += 1
                    
                    # Backoff em caso de erro
                    if job["adaptive_enabled"]:
                        job["intervalo_atual"] = min(job["intervalo_atual"] * 2, 3600)
    
    def _adjust_interval_based_on_performance(self, nome: str, job: Dict, execution_time: float):
        """Ajusta intervalo baseado na performance e condições"""
        if job["moeda"] not in self.manager.market_state:
            return
            
        market_data = self.manager.market_state[job["moeda"]]
        market_condition = MarketCondition(market_data.get("market_condition", MarketCondition.SIDEWAYS.value))
        
        # Recalcular intervalo ótimo
        novo_intervalo = self.adaptive_scheduler.calculate_optimal_interval(
            job["intervalo_base"], market_condition
        )
        
        if novo_intervalo != job["intervalo_atual"]:
            job["intervalo_atual"] = novo_intervalo
            self.adaptive_intervals[nome] = novo_intervalo
            self.manager.performance_metrics.adaptive_adjustments += 1
            
            self.manager.logger.debug(
                f"🔄 Intervalo ajustado para {nome}: {novo_intervalo}s "
                f"(condição: {market_condition.value})"
            )

# =====================================================
# 🎮 CONTROLE PRINCIPAL DE AUTOMAÇÃO AVANÇADO
# =====================================================

class AutomationManager:
    """Sistema centralizado avançado de gestão de automação"""
    
    def __init__(self, config: AutomationConfig = None):
        self.config = config or AutomationConfig()
        self._running = False
        self._threads = []
        
        # Sistemas principais
        self.learning_system = LearningSystem()
        self.alert_system = SmartAlertSystem(self)
        self.report_generator = AdvancedReportGenerator(self)
        self.email_automation = AdvancedEmailAutomation(self)
        self.scheduler = AdvancedSmartScheduler(self)
        
        # Estado e métricas
        self.alert_history = []
        self.last_alert_times = {}
        self.market_state = {}
        self.performance_metrics = PerformanceMetrics()
        self.start_time = datetime.now()
        
        # Sistema de logging
        self.logger = self._setup_logging()
        
        # Notificador de e-mail
        self.email_notifier = EmailNotifier() if EMAIL_UTILS_AVAILABLE else None
        
    def _setup_logging(self):
        """Configura sistema de logging profissional"""
        logger = logging.getLogger("KLStarTech_Automation_Advanced")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_market_data(self, moeda: str) -> pd.DataFrame:
        """Obtém dados de mercado (placeholder para implementação real)"""
        # Em implementação real, buscaria dados atualizados
        return pd.DataFrame()

def criar_sistema_automacao_avancado(config: AutomationConfig = None) -> AutomationManager:
    """Factory function para criar sistema completo de automação avançada"""
    manager = AutomationManager(config)
    
    # Configurações iniciais
    if manager.config.ia_ativa and AI_AVAILABLE:
        manager.logger.info("🧠 Sistema de IA integrado ativado")
    else:
        manager.logger.info("🔧 Sistema operando em modo tradicional")
    
    return manager

async def iniciar_automacao_avancada(manager: AutomationManager):
    """Inicia sistema completo de automação avançada"""
    if manager._running:
        manager.logger.warning("⚠️ Automação já está rodando")
        return
    
    manager._running = True
    manager.start_time = datetime.now()
    
    # Configurar tarefas agendadas adaptativas
    if manager.config.relatorios_ativos:
        manager.scheduler.agendar_tarefa_adaptativa(
            lambda: asyncio.create_task(manager.email_automation.enviar_relatorio_inteligente()),
            manager.config.intervalo_relatorios_base,
            "relatorio_inteligente",
            manager.config.moeda_padrao
        )
    
    # Thread principal de execução
    def loop_principal():
        manager.logger.info("🤖 Sistema de automação AVANÇADO INICIADO")
        
        while manager._running:
            try:
                # Atualizar métricas de performance
                manager.performance_metrics.uptime = (
                    datetime.now() - manager.start_time
                ).total_seconds()
                
                # Executar tarefas agendadas
                manager.scheduler.executar_tarefas_pendentes()
                
                # Intervalo entre verificações (adaptativo)
                intervalo_verificacao = manager.scheduler.adaptive_intervals.get(
                    "verificacao_principal", 
                    manager.config.intervalo_verificacao_base
                )
                
                time.sleep(intervalo_verificacao)
                
            except Exception as e:
                manager.logger.error(f"❌ Erro no loop principal: {e}")
                manager.performance_metrics.erros += 1
                time.sleep(10)  # Backoff em caso de erro
    
    thread = threading.Thread(target=loop_principal, daemon=True)
    manager._threads.append(thread)
    thread.start()
    
    manager.logger.info(
        f"🚀 Automação avançada iniciada para {manager.config.moeda_padrao} "
        f"(modo: {manager.config.modo_operacao.value})"
    )

def parar_automacao_avancada(manager: AutomationManager):
    """Para o sistema de automação avançada"""
    manager._running = False
    manager.logger.info("🛑 Sistema de automação avançada PARADO")
    
    # Aguardar threads finalizarem
    for thread in manager._threads:
        thread.join(timeout=5)
    
    # Log final de métricas
    manager.logger.info(f"📈 Métricas finais: {manager.performance_metrics.to_dict()}")

# =====================================================
# 🔄 FUNÇÕES DE COMPATIBILIDADE (interface original)
# =====================================================

# Instância global para compatibilidade
_global_manager = None

def can_send_alert(moeda: str, valor_alvo: float, cooldown_seconds: int = 3600) -> bool:
    """Função compatível com interface original"""
    global _global_manager
    if _global_manager is None:
        _global_manager = criar_sistema_automacao_avancado()
    
    # Usar versão síncrona simplificada
    return _global_manager.alert_system._check_cooldown(moeda, valor_alvo)

def mark_alert_sent(moeda: str, valor_alvo: float, canais: str):
    """Função compatível com interface original"""
    global _global_manager
    if _global_manager is None:
        _global_manager = criar_sistema_automacao_avancado()
    
    _global_manager.alert_system.mark_alert_sent(moeda, valor_alvo, canais)

def get_alert_history():
    """Função compatível com interface original"""
    global _global_manager
    if _global_manager is None:
        return []
    return _global_manager.alert_system.get_alert_history(24)

def iniciar_automacao(moeda="USD", dias=7, intervalo=3600):
    """Função compatível com interface original"""
    global _global_manager
    
    config = AutomationConfig(
        moeda_padrao=moeda,
        dias_historico=dias,
        intervalo_verificacao_base=60,
        intervalo_relatorios_base=intervalo,
        ia_ativa=False  # Desativar IA para compatibilidade
    )
    
    _global_manager = criar_sistema_automacao_avancado(config)
    
    # Usar versão síncrona para compatibilidade
    def start_sync():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(iniciar_automacao_avancada(_global_manager))
    
    threading.Thread(target=start_sync, daemon=True).start()

def parar_automacao():
    """Função compatível com interface original"""
    global _global_manager
    if _global_manager:
        parar_automacao_avancada(_global_manager)

# =====================================================
# 🧪 TESTE DO SISTEMA AVANÇADO
# =====================================================

async def testar_sistema_avancado():
    """Teste completo do sistema avançado"""
    print("🧪 TESTE SISTEMA AUTOMAÇÃO AVANÇADO KLSTARTECH")
    print("=" * 60)
    
    # Configuração de teste
    config_teste = AutomationConfig(
        moeda_padrao="BTC",
        dias_historico=7,
        intervalo_verificacao_base=10,
        intervalo_relatorios_base=30,
        email_destino=os.getenv("ALERT_EMAIL_TO"),
        modo_operacao=AutomationMode.INTELLIGENT,
        ia_ativa=True
    )
    
    # Criar e iniciar sistema
    manager_teste = criar_sistema_automacao_avancado(config_teste)
    
    try:
        print("1. 🧠 Teste sistema de aprendizado...")
        patterns = manager_teste.learning_system.analyze_pattern(pd.DataFrame(), [])
        print(f"   ✅ Sistema de aprendizado: {len(patterns)} padrões analisados")
        
        print("\n2. 🔔 Teste sistema de alertas inteligentes...")
        should_alert, confidence = await manager_teste.alert_system.should_send_alert(
            "BTC", 50000, "teste", {}
        )
        print(f"   ✅ Decisão de alerta: {should_alert} (conf: {confidence:.2f})")
        
        print("\n3. 📊 Teste geração de relatórios avançados...")
        relatorios = manager_teste.report_generator.gerar_relatorios_avancados("BTC", 7)
        print(f"   ✅ Relatórios avançados gerados: {list(relatorios.keys())}")
        
        print("\n4. ⏰ Teste agendamento adaptativo...")
        manager_teste.scheduler.agendar_tarefa_adaptativa(
            lambda: print("   ✅ Tarefa adaptativa executada"),
            30, "teste_adaptativo", "BTC"
        )
        
        print("\n5. 🤖 Iniciando automação avançada (45 segundos)...")
        await iniciar_automacao_avancada(manager_teste)
        await asyncio.sleep(45)
        
        print("\n6. 📈 Estatísticas do sistema avançado:")
        print(f"   {json.dumps(manager_teste.performance_metrics.to_dict(), indent=2)}")
        
        print("\n7. 🔍 Histórico de alertas inteligentes:")
        alertas = manager_teste.alert_system.get_alert_history(1, 0.5)
        print(f"   {len(alertas)} alertas de alta confiança na última hora")
        
    finally:
        parar_automacao_avancada(manager_teste)
    
    print("✅ Teste do sistema de automação avançado completo!")

if __name__ == "__main__":
    # Executar teste
    asyncio.run(testar_sistema_avancado())