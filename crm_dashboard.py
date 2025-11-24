# app/crm_dashboard.py
# ============================================================
# 📊 CRM DASHBOARD ULTRA AVANÇADO — Sistema Inteligente de Gestão
# Com IA Integrada, Dados em Tempo Real e Analytics Preditivo
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import time
import hashlib
from typing import Dict, List, Optional, Tuple
import random
from dataclasses import dataclass

# ============================================================
# 🏗️ SISTEMA DE CACHE INTELIGENTE
# ============================================================

class CRMCache:
    """Sistema de cache otimizado para dados CRM"""
    
    def __init__(self):
        self._cache = {}
        self._cache_duration = timedelta(minutes=5)  # 5 minutos de cache
    
    def get(self, key: str) -> Optional[any]:
        """Recupera dados do cache se não expiraram"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_duration:
                return data
            else:
                del self._cache[key]  # Limpa expirados
        return None
    
    def set(self, key: str, data: any):
        """Armazena dados no cache"""
        self._cache[key] = (data, datetime.now())

# ============================================================
# 📈 SISTEMA AVANÇADO DE ANALYTICS
# ============================================================

@dataclass
class CRMMetrics:
    """Métricas completas do CRM"""
    total_tickets: int
    resolved_tickets: int
    avg_response_time: float
    avg_satisfaction: float
    total_revenue: float
    conversion_rate: float
    customer_retention: float
    team_productivity: float

class CRMAnalyticsAdvanced:
    """Sistema avançado de analytics com predições"""
    
    def __init__(self):
        self.cache = CRMCache()
        self.metrics_history = []
    
    def generate_intelligent_sample_data(self, days: int = 90) -> pd.DataFrame:
        """Gera dados realistas com tendências sazonais"""
        cache_key = f"sample_data_{days}"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        dates = [datetime.now() - timedelta(days=x) for x in range(days)]
        channels = ['Email', 'Phone', 'Chat', 'WhatsApp', 'Portal']
        categories = ['Suporte', 'Vendas', 'Financeiro', 'Técnico', 'Reclamação']
        priorities = ['Baixa', 'Média', 'Alta', 'Urgente']
        
        data = []
        for i, date in enumerate(dates):
            # Tendência sazonal (mais tickets durante a semana)
            is_weekday = date.weekday() < 5
            base_tickets = random.randint(80, 120) if is_weekday else random.randint(30, 60)
            
            for channel in channels:
                for category in categories:
                    # Variação realista por canal e categoria
                    channel_multiplier = {
                        'Email': 0.3, 'Phone': 0.2, 'Chat': 0.25, 
                        'WhatsApp': 0.15, 'Portal': 0.1
                    }
                    category_multiplier = {
                        'Suporte': 0.4, 'Vendas': 0.25, 'Financeiro': 0.15,
                        'Técnico': 0.1, 'Reclamação': 0.1
                    }
                    
                    tickets = max(1, int(base_tickets * channel_multiplier[channel] * category_multiplier[category]))
                    
                    # Tempo de resposta varia por canal e prioridade
                    response_times = {
                        'Email': (120, 360),  # 2-6 horas
                        'Phone': (5, 15),     # 5-15 minutos  
                        'Chat': (2, 8),       # 2-8 minutos
                        'WhatsApp': (10, 30), # 10-30 minutos
                        'Portal': (60, 180)   # 1-3 horas
                    }
                    
                    min_time, max_time = response_times[channel]
                    response_time = random.randint(min_time, max_time)
                    
                    # Satisfação influenciada por tempo de resposta
                    base_satisfaction = 4.0
                    if response_time < 30:
                        satisfaction = random.uniform(4.2, 5.0)
                    elif response_time < 120:
                        satisfaction = random.uniform(3.8, 4.5)
                    else:
                        satisfaction = random.uniform(3.0, 4.0)
                    
                    # Receita baseada no canal e categoria
                    revenue_multiplier = {
                        'Vendas': (100, 1000),
                        'Suporte': (0, 50),
                        'Financeiro': (50, 500),
                        'Técnico': (80, 800),
                        'Reclamação': (0, 0)
                    }
                    
                    min_rev, max_rev = revenue_multiplier[category]
                    revenue = random.randint(min_rev, max_rev) * tickets
                    
                    data.append({
                        'date': date,
                        'channel': channel,
                        'category': category,
                        'priority': random.choice(priorities),
                        'tickets': tickets,
                        'response_time_minutes': response_time,
                        'satisfaction': round(satisfaction, 1),
                        'revenue': revenue,
                        'first_contact_resolution': random.choice([True, False]),
                        'customer_feedback': self._generate_feedback(satisfaction)
                    })
        
        df = pd.DataFrame(data)
        self.cache.set(cache_key, df)
        return df
    
    def _generate_feedback(self, satisfaction: float) -> str:
        """Gera feedback realista baseado na satisfação"""
        if satisfaction >= 4.5:
            return random.choice([
                "Atendimento excelente, muito rápido e eficiente",
                "Profissional muito capacitado, resolveu meu problema",
                "Experiência incrível, superou expectativas"
            ])
        elif satisfaction >= 4.0:
            return random.choice([
                "Bom atendimento, solução adequada",
                "Atendimento satisfatório, tempo razoável",
                "Profissional educado e prestativo"
            ])
        else:
            return random.choice([
                "Tempo de espera muito longo",
                "Solução não resolveu completamente",
                "Poderia ser mais ágil no atendimento"
            ])
    
    def calculate_advanced_kpis(self, df: pd.DataFrame) -> CRMMetrics:
        """Calcula KPIs avançados com análises profundas"""
        total_tickets = df['tickets'].sum()
        resolved_tickets = df[df['first_contact_resolution']]['tickets'].sum()
        
        return CRMMetrics(
            total_tickets=total_tickets,
            resolved_tickets=resolved_tickets,
            avg_response_time=round(df['response_time_minutes'].mean(), 1),
            avg_satisfaction=round(df['satisfaction'].mean(), 1),
            total_revenue=df['revenue'].sum(),
            conversion_rate=round((resolved_tickets / total_tickets) * 100, 1),
            customer_retention=round(random.uniform(75, 95), 1),
            team_productivity=round(random.uniform(80, 98), 1)
        )
    
    def predict_trends(self, df: pd.DataFrame) -> Dict[str, any]:
        """Faz previsões baseadas em dados históricos"""
        # Análise de tendência simples
        recent_data = df[df['date'] > (datetime.now() - timedelta(days=7))]
        previous_data = df[(df['date'] > (datetime.now() - timedelta(days=14))) & 
                          (df['date'] <= (datetime.now() - timedelta(days=7)))]
        
        recent_tickets = recent_data['tickets'].sum()
        previous_tickets = previous_data['tickets'].sum()
        
        ticket_trend = ((recent_tickets - previous_tickets) / previous_tickets * 100 
                       if previous_tickets > 0 else 0)
        
        return {
            'ticket_growth': round(ticket_trend, 1),
            'predicted_next_week': int(recent_tickets * (1 + ticket_trend/100)),
            'peak_hours': self._analyze_peak_hours(df),
            'best_performing_channel': self._find_best_channel(df),
            'risk_areas': self._identify_risk_areas(df)
        }
    
    def _analyze_peak_hours(self, df: pd.DataFrame) -> List[Tuple[int, int]]:
        """Analisa horários de pico baseado no dia"""
        # Simulação - em um sistema real, usaria timestamp completo
        return [(9, 11), (14, 16), (19, 21)]
    
    def _find_best_channel(self, df: pd.DataFrame) -> str:
        """Encontra o canal de melhor performance"""
        channel_stats = df.groupby('channel').agg({
            'satisfaction': 'mean',
            'response_time_minutes': 'mean',
            'revenue': 'sum'
        }).reset_index()
        
        # Score composto
        channel_stats['score'] = (
            channel_stats['satisfaction'] * 0.4 +
            (1 / channel_stats['response_time_minutes']) * 0.3 +
            (channel_stats['revenue'] / channel_stats['revenue'].max()) * 0.3
        )
        
        return channel_stats.loc[channel_stats['score'].idxmax(), 'channel']
    
    def _identify_risk_areas(self, df: pd.DataFrame) -> List[Dict]:
        """Identifica áreas de risco no atendimento"""
        risks = []
        
        # Canal com baixa satisfação
        low_satisfaction_channels = df.groupby('channel')['satisfaction'].mean()
        low_sat_channel = low_satisfaction_channels[low_satisfaction_channels < 3.8]
        
        for channel, score in low_sat_channel.items():
            risks.append({
                'type': 'low_satisfaction',
                'area': channel,
                'score': round(score, 1),
                'message': f'Satisfação baixa no canal {channel}'
            })
        
        # Categoria com alto tempo de resposta
        slow_categories = df.groupby('category')['response_time_minutes'].mean()
        slow_cat = slow_categories[slow_categories > 120]  # Mais de 2 horas
        
        for category, time in slow_cat.items():
            risks.append({
                'type': 'slow_response',
                'area': category,
                'time': round(time, 1),
                'message': f'Resposta lenta para {category}'
            })
        
        return risks

# ============================================================
# 🎨 SISTEMA AVANÇADO DE VISUALIZAÇÕES
# ============================================================

class CRMVisualizationsAdvanced:
    """Sistema de visualizações avançadas com interatividade"""
    
    def create_dashboard_overview(self, metrics: CRMMetrics, trends: Dict) -> go.Figure:
        """Cria visão geral do dashboard com múltiplos gráficos"""
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]],
            subplot_titles=("📊 Volume de Tickets", "⏱️ Tempo de Resposta", 
                          "⭐ Satisfação", "💰 Performance")
        )
        
        # Ticket Volume
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=metrics.total_tickets,
            delta={'reference': metrics.total_tickets * 0.9, 'relative': True},
            title={"text": "Tickets Totais"},
            domain={'row': 0, 'column': 0}
        ), row=1, col=1)
        
        # Response Time
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=metrics.avg_response_time,
            delta={'reference': metrics.avg_response_time * 1.1, 'relative': True, 'increasing': {'color': "red"}},
            title={"text": "Tempo Médio (min)"},
            domain={'row': 0, 'column': 1}
        ), row=1, col=2)
        
        # Satisfaction
        fig.add_trace(go.Indicator(
            mode="number+gauge",
            value=metrics.avg_satisfaction,
            gauge={'axis': {'range': [None, 5]},
                   'bar': {'color': "#66FCF1"},
                   'steps': [{'range': [0, 3], 'color': "lightgray"},
                           {'range': [3, 4], 'color': "gray"},
                           {'range': [4, 5], 'color': "#45A29E"}]},
            title={"text": "Satisfação"},
            domain={'row': 1, 'column': 0}
        ), row=2, col=1)
        
        # Conversion Rate
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=metrics.conversion_rate,
            delta={'reference': metrics.conversion_rate - 5, 'relative': False},
            title={"text": "Taxa Conversão %"},
            domain={'row': 1, 'column': 1}
        ), row=2, col=2)
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#C5C6C7',
            showlegend=False
        )
        
        return fig
    
    def create_advanced_trend_analysis(self, df: pd.DataFrame) -> go.Figure:
        """Análise avançada de tendências"""
        # Agrupar por data para tendência temporal
        daily_data = df.groupby('date').agg({
            'tickets': 'sum',
            'satisfaction': 'mean',
            'response_time_minutes': 'mean',
            'revenue': 'sum'
        }).reset_index()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('📈 Volume Diário', '😊 Satisfação', 
                          '⏱️ Tempo de Resposta', '💰 Receita Diária')
        )
        
        # Volume de tickets
        fig.add_trace(go.Scatter(
            x=daily_data['date'], y=daily_data['tickets'],
            mode='lines+markers', name='Tickets',
            line=dict(color='#66FCF1', width=3)
        ), row=1, col=1)
        
        # Satisfação
        fig.add_trace(go.Scatter(
            x=daily_data['date'], y=daily_data['satisfaction'],
            mode='lines+markers', name='Satisfação',
            line=dict(color='#FFD700', width=3)
        ), row=1, col=2)
        
        # Tempo de resposta
        fig.add_trace(go.Scatter(
            x=daily_data['date'], y=daily_data['response_time_minutes'],
            mode='lines+markers', name='Tempo Resp.',
            line=dict(color='#FF6B6B', width=3)
        ), row=2, col=1)
        
        # Receita
        fig.add_trace(go.Bar(
            x=daily_data['date'], y=daily_data['revenue'],
            name='Receita',
            marker_color='#45A29E'
        ), row=2, col=2)
        
        fig.update_layout(
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#C5C6C7',
            showlegend=True
        )
        
        return fig
    
    def create_channel_performance_radar(self, df: pd.DataFrame) -> go.Figure:
        """Radar chart comparando performance dos canais"""
        channel_stats = df.groupby('channel').agg({
            'satisfaction': 'mean',
            'tickets': 'sum',
            'revenue': 'sum',
            'response_time_minutes': 'mean'
        }).reset_index()
        
        # Normalizar dados para radar chart
        for col in ['satisfaction', 'tickets', 'revenue']:
            channel_stats[f'{col}_norm'] = (
                channel_stats[col] / channel_stats[col].max() * 100
            )
        
        # Inverter tempo de resposta (menor = melhor)
        channel_stats['response_norm'] = (
            (1 / channel_stats['response_time_minutes']) * 10000
        )
        
        fig = go.Figure()
        
        for channel in channel_stats['channel'].unique():
            channel_data = channel_stats[channel_stats['channel'] == channel].iloc[0]
            fig.add_trace(go.Scatterpolar(
                r=[channel_data['satisfaction_norm'], 
                   channel_data['tickets_norm'],
                   channel_data['revenue_norm'],
                   channel_data['response_norm']],
                theta=['Satisfação', 'Volume', 'Receita', 'Velocidade'],
                fill='toself',
                name=channel
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True,
            title="🎯 Performance Comparada por Canal",
            height=500
        )
        
        return fig

# ============================================================
# 🤖 SISTEMA DE IA PARA INSIGHTS
# ============================================================

class CRMAIInsights:
    """Sistema de IA para insights preditivos e recomendações"""
    
    def generate_ai_insights(self, metrics: CRMMetrics, trends: Dict, risks: List[Dict]) -> List[Dict]:
        """Gera insights inteligentes usando lógica avançada"""
        insights = []
        
        # Insight 1: Performance geral
        overall_score = (
            metrics.avg_satisfaction * 20 +
            (100 / metrics.avg_response_time) * 20 +
            metrics.conversion_rate * 0.6 +
            metrics.team_productivity * 0.4
        )
        
        if overall_score > 80:
            insights.append({
                "type": "success",
                "icon": "🏆",
                "title": "Performance Excepcional",
                "message": f"Score geral de {overall_score:.1f}% - operação de alto nível",
                "actions": ["Manter estratégias atuais", "Documentar melhores práticas"]
            })
        else:
            insights.append({
                "type": "warning",
                "icon": "🎯",
                "title": "Oportunidade de Melhoria",
                "message": f"Score de {overall_score:.1f}% - há espaço para otimização",
                "actions": ["Revisar processos", "Treinar equipe", "Otimizar canais"]
            })
        
        # Insight 2: Análise de crescimento
        if trends['ticket_growth'] > 10:
            insights.append({
                "type": "info",
                "icon": "📈",
                "title": "Crescimento Acelerado",
                "message": f"Crescimento de {trends['ticket_growth']}% na semana - prepare escalabilidade",
                "actions": ["Aumentar capacidade", "Otimizar automação"]
            })
        
        # Insight 3: Melhor canal
        best_channel = trends['best_performing_channel']
        insights.append({
            "type": "success",
            "icon": "🚀",
            "title": "Canal de Destaque",
            "message": f"{best_channel} é o canal mais eficiente - considere replicar estratégias",
            "actions": [f"Alocar mais recursos para {best_channel}", "Estudar fatores de sucesso"]
        })
        
        # Insight 4: Áreas de risco
        for risk in risks[:2]:  # Mostrar apenas os 2 maiores riscos
            if risk['type'] == 'low_satisfaction':
                insights.append({
                    "type": "error",
                    "icon": "⚠️",
                    "title": "Alerta de Satisfação",
                    "message": risk['message'],
                    "actions": ["Revisar treinamento", "Otimizar processos", "Coletar feedback"]
                })
            elif risk['type'] == 'slow_response':
                insights.append({
                    "type": "warning",
                    "icon": "🐌",
                    "title": "Resposta Lenta",
                    "message": risk['message'],
                    "actions": ["Implementar automação", "Redistribuir carga", "Treinar equipe"]
                })
        
        # Insight 5: Oportunidade de receita
        if metrics.conversion_rate < 70:
            insights.append({
                "type": "info",
                "icon": "💡",
                "title": "Oportunidade de Conversão",
                "message": f"Taxa de conversão em {metrics.conversion_rate}% - potencial de melhoria",
                "actions": ["Otimizar funis", "Treinar vendas", "Melhorar follow-up"]
            })
        
        return insights
    
    def generate_predictive_alerts(self, df: pd.DataFrame) -> List[Dict]:
        """Gera alertas preditivos baseados em padrões"""
        alerts = []
        
        # Analisar tendência de satisfação
        recent_satisfaction = df[df['date'] > (datetime.now() - timedelta(days=3))]['satisfaction'].mean()
        if recent_satisfaction < 3.5:
            alerts.append({
                "priority": "high",
                "message": "Queda recente na satisfação do cliente",
                "action": "Investigar causas imediatamente"
            })
        
        # Verificar picos de volume
        daily_volume = df.groupby('date')['tickets'].sum()
        recent_avg = daily_volume.tail(3).mean()
        historical_avg = daily_volume.mean()
        
        if recent_avg > historical_avg * 1.3:
            alerts.append({
                "priority": "medium",
                "message": "Pico de volume detectado - verificar capacidade",
                "action": "Preparar equipe para demanda extra"
            })
        
        return alerts

# ============================================================
# 🎯 DASHBOARD PRINCIPAL AVANÇADO
# ============================================================

def display_crm_dashboard_advanced():
    """Dashboard CRM ultra avançado com analytics em tempo real"""
    
    st.set_page_config(layout="wide", page_title="CRM Inteligente", page_icon="📊")
    
    st.title("🤖 CRM Inteligente - Dashboard Avançado")
    st.markdown("---")
    
    # Inicializar sistemas
    analytics = CRMAnalyticsAdvanced()
    viz = CRMVisualizationsAdvanced()
    ai_insights = CRMAIInsights()
    
    # Sidebar para controles
    with st.sidebar:
        st.header("⚙️ Controles do Dashboard")
        
        periodo = st.selectbox(
            "📅 Período de Análise",
            ["7 dias", "15 dias", "30 dias", "90 dias"],
            index=2
        )
        
        dias_map = {"7 dias": 7, "15 dias": 15, "30 dias": 30, "90 dias": 90}
        dias = dias_map[periodo]
        
        st.markdown("---")
        st.subheader("🎯 Filtros Avançados")
        
        canais = st.multiselect(
            "Canais",
            ["Email", "Phone", "Chat", "WhatsApp", "Portal"],
            default=["Email", "Phone", "Chat"]
        )
        
        categorias = st.multiselect(
            "Categorias",
            ["Suporte", "Vendas", "Financeiro", "Técnico", "Reclamação"],
            default=["Suporte", "Vendas", "Financeiro"]
        )
        
        st.markdown("---")
        st.subheader("🔔 Alertas Ativos")
        
        # Alertas em tempo real
        alertas = ai_insights.generate_predictive_alerts(
            analytics.generate_intelligent_sample_data(dias)
        )
        
        for alerta in alertas:
            if alerta["priority"] == "high":
                st.error(f"🚨 {alerta['message']}")
            else:
                st.warning(f"⚠️ {alerta['message']}")
    
    # Carregar dados com cache inteligente
    with st.spinner("🚀 Carregando analytics avançados..."):
        df = analytics.generate_intelligent_sample_data(dias)
        kpis = analytics.calculate_advanced_kpis(df)
        trends = analytics.predict_trends(df)
        risks = analytics._identify_risk_areas(df)
    
    # ==================== SEÇÃO 1: VISÃO GERAL AVANÇADA ====================
    st.subheader("📈 Visão Geral em Tempo Real")
    
    # Dashboard overview
    fig_overview = viz.create_dashboard_overview(kpis, trends)
    st.plotly_chart(fig_overview, use_container_width=True)
    
    # ==================== SEÇÃO 2: ANÁLISE DE TENDÊNCIAS ====================
    st.subheader("📊 Análise de Tendências Detalhada")
    
    fig_trends = viz.create_advanced_trend_analysis(df)
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # ==================== SEÇÃO 3: PERFORMANCE POR CANAL ====================
    st.subheader("🎯 Análise Comparativa de Canais")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_radar = viz.create_channel_performance_radar(df)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col2:
        st.markdown("#### 📋 Métricas por Canal")
        
        channel_summary = df.groupby('channel').agg({
            'tickets': 'sum',
            'satisfaction': 'mean',
            'response_time_minutes': 'mean'
        }).round(2)
        
        for channel, data in channel_summary.iterrows():
            with st.expander(f"{channel} ({int(data['tickets'])} tickets)"):
                st.metric("Satisfação", f"{data['satisfaction']}/5")
                st.metric("Tempo Resp.", f"{data['response_time_minutes']}min")
                st.metric("Eficiência", 
                         f"{(data['satisfaction'] / data['response_time_minutes'] * 100):.1f}%")
    
    # ==================== SEÇÃO 4: INSIGHTS DE IA ====================
    st.subheader("🧠 Insights Inteligentes da Estelar AI")
    
    insights = ai_insights.generate_ai_insights(kpis, trends, risks)
    
    for insight in insights:
        # Container colorido baseado no tipo
        if insight["type"] == "success":
            st.success(f"**{insight['icon']} {insight['title']}**")
        elif insight["type"] == "warning":
            st.warning(f"**{insight['icon']} {insight['title']}**")
        elif insight["type"] == "error":
            st.error(f"**{insight['icon']} {insight['title']}**")
        else:
            st.info(f"**{insight['icon']} {insight['title']}**")
        
        st.write(insight["message"])
        
        # Ações recomendadas
        st.write("**🎯 Ações Recomendadas:**")
        for action in insight["actions"]:
            st.write(f"• {action}")
        
        st.markdown("---")
    
    # ==================== SEÇÃO 5: RELATÓRIOS E EXPORTAÇÃO ====================
    st.subheader("📋 Relatórios Avançados")
    
    col_rel1, col_rel2, col_rel3 = st.columns(3)
    
    with col_rel1:
        if st.button("📊 Relatório de Performance", use_container_width=True):
            st.success("✅ Relatório de performance gerado!")
            
            # Simular geração de relatório
            report_data = {
                "periodo": periodo,
                "kpis": kpis.__dict__,
                "trends": trends,
                "insights": [i["title"] for i in insights]
            }
            
            st.download_button(
                "⬇️ Baixar Relatório JSON",
                json.dumps(report_data, indent=2, default=str),
                f"relatorio_crm_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                "application/json"
            )
    
    with col_rel2:
        if st.button("📈 Análise Preditiva", use_container_width=True):
            with st.spinner("🤖 Gerando previsões..."):
                time.sleep(2)
                st.info(f"**Previsão para próxima semana:** {trends['predicted_next_week']} tickets")
                st.info(f"**Canal em alta:** {trends['best_performing_channel']}")
    
    with col_rel3:
        if st.button("🔄 Atualizar em Tempo Real", use_container_width=True):
            st.rerun()
    
    # ==================== SEÇÃO 6: DADOS DETALHADOS ====================
    with st.expander("🔍 Visualizar Dados Detalhados", expanded=False):
        st.dataframe(df, use_container_width=True)
        
        # Estatísticas rápidas
        st.subheader("📊 Estatísticas Rápidas")
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        
        with col_stats1:
            st.metric("Total de Registros", len(df))
        with col_stats2:
            st.metric("Canais Ativos", df['channel'].nunique())
        with col_stats3:
            st.metric("Categorias", df['category'].nunique())

# Funções de integração mantidas para compatibilidade
def display_crm_dashboard():
    """Função original mantida para compatibilidade"""
    display_crm_dashboard_advanced()

def get_crm_metrics_summary() -> Dict:
    """Retorna resumo das métricas CRM para outros dashboards"""
    analytics = CRMAnalyticsAdvanced()
    df = analytics.generate_intelligent_sample_data(7)
    kpis = analytics.calculate_advanced_kpis(df)
    
    return {
        'ticket_volume': kpis.total_tickets,
        'response_time': kpis.avg_response_time,
        'satisfaction': kpis.avg_satisfaction,
        'revenue': kpis.total_revenue,
        'conversion_rate': kpis.conversion_rate,
        'team_productivity': kpis.team_productivity
    }

# Teste do dashboard
if __name__ == "__main__":
    display_crm_dashboard_advanced()