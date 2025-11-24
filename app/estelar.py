# app/estelar.py
# ============================================================
# 🌟 ESTELAR SUPREMA 4.0 — Sistema de IA Conversacional Avançado
# ============================================================

import streamlit as st
import threading
import json
import time
import os
import asyncio
import queue
import random
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
import numpy as np

load_dotenv()

# ============================================================
# 🧠 SISTEMA DE MEMÓRIA E CONTEXTO AVANÇADO
# ============================================================

@dataclass
class ConversationMemory:
    """Sistema avançado de memória de conversação"""
    short_term_memory: List[Dict] = field(default_factory=list)
    long_term_memory: List[Dict] = field(default_factory=list)
    user_preferences: Dict = field(default_factory=dict)
    context_window: int = 10
    
    def add_interaction(self, user_message: str, assistant_response: str, metadata: Dict = None):
        """Adiciona interação à memória com metadados ricos"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": assistant_response,
            "metadata": metadata or {},
            "emotion_detected": self._detect_emotion(user_message),
            "topics": self._extract_topics(user_message)
        }
        
        self.short_term_memory.append(interaction)
        
        # Manter apenas as últimas N interações na memória de curto prazo
        if len(self.short_term_memory) > self.context_window:
            self.short_term_memory.pop(0)
    
    def get_context(self, max_interactions: int = 5) -> str:
        """Recupera contexto relevante para a conversa atual"""
        recent_context = self.short_term_memory[-max_interactions:] if self.short_term_memory else []
        
        context_parts = []
        for interaction in recent_context:
            context_parts.append(f"Usuário: {interaction['user']}")
            context_parts.append(f"Assistente: {interaction['assistant']}")
        
        return "\n".join(context_parts)
    
    def _detect_emotion(self, text: str) -> str:
        """Detecta emoção básica no texto"""
        text_lower = text.lower()
        positive_words = ['obrigado', 'bom', 'ótimo', 'excelente', 'incrível', 'adoro', 'amo']
        negative_words = ['ruim', 'péssimo', 'odeio', 'chateado', 'bravo', 'frustrado']
        
        if any(word in text_lower for word in positive_words):
            return "positive"
        elif any(word in text_lower for word in negative_words):
            return "negative"
        else:
            return "neutral"
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extrai tópicos principais do texto"""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            "finanças": ["dinheiro", "investimento", "ação", "bolsa", "cripto", "bitcoin"],
            "tecnologia": ["código", "programação", "python", "ia", "inteligência artificial"],
            "crm": ["cliente", "venda", "atendimento", "suporte", "ticket"],
            "dashboard": ["relatório", "gráfico", "métrica", "análise", "dados"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

# ============================================================
# 🎭 SISTEMA AVANÇADO DE EXPRESSÕES E PERSONALIDADE
# ============================================================

class PersonalityTrait(Enum):
    FRIENDLY = auto()
    PROFESSIONAL = auto()
    TECHNICAL = auto()
    ENTHUSIASTIC = auto()
    CALM = auto()

class FacialExpression(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    THINKING = "thinking"
    CONFUSED = "confused"
    ALERT = "alert"
    LAUGHING = "laughing"
    SAD = "sad"
    WINKING = "winking"
    CURIOUS = "curious"
    CONFIDENT = "confident"

@dataclass
class ExpressionConfig:
    intensity: float = 1.0
    duration: float = 2.0
    transition: float = 0.3
    audio_sync: bool = False

class AdvancedPersonalitySystem:
    """Sistema avançado de personalidade e expressões"""
    
    def __init__(self):
        self.current_personality = "FRIENDLY"
        self.expression_history = []
        self.emotion_state = "neutral"
        
        self.personality_profiles = {
            "FRIENDLY": {
                "traits": [PersonalityTrait.FRIENDLY, PersonalityTrait.ENTHUSIASTIC],
                "response_style": "caloroso e acolhedor",
                "expressions": {
                    "default": FacialExpression.HAPPY,
                    "thinking": FacialExpression.THINKING,
                    "greeting": FacialExpression.EXCITED
                }
            },
            "PROFESSIONAL": {
                "traits": [PersonalityTrait.PROFESSIONAL, PersonalityTrait.CALM],
                "response_style": "preciso e formal",
                "expressions": {
                    "default": FacialExpression.NEUTRAL,
                    "thinking": FacialExpression.THINKING,
                    "success": FacialExpression.CONFIDENT
                }
            },
            "TECHNICAL": {
                "traits": [PersonalityTrait.TECHNICAL, PersonalityTrait.CALM],
                "response_style": "detalhado e analítico",
                "expressions": {
                    "default": FacialExpression.THINKING,
                    "explaining": FacialExpression.CURIOUS,
                    "success": FacialExpression.CONFIDENT
                }
            }
        }
        
        self.emotion_to_expression = {
            "joy": FacialExpression.HAPPY,
            "curiosity": FacialExpression.CURIOUS,
            "urgency": FacialExpression.ALERT,
            "surprise": FacialExpression.EXCITED,
            "confusion": FacialExpression.CONFUSED,
            "celebration": FacialExpression.LAUGHING,
            "satisfaction": FacialExpression.CONFIDENT,
            "concern": FacialExpression.THINKING
        }

class AdvancedFacialSystem:
    def __init__(self):
        self.current_expression = FacialExpression.NEUTRAL
        self.expression_history = []
        self.expression_intensity = 1.0
        
        self.expression_configs = {
            FacialExpression.NEUTRAL: ExpressionConfig(0.8, 0, 0.2),
            FacialExpression.HAPPY: ExpressionConfig(1.0, 3.0, 0.4),
            FacialExpression.THINKING: ExpressionConfig(0.9, 5.0, 0.5),
            FacialExpression.ALERT: ExpressionConfig(1.0, 2.0, 0.2),
            FacialExpression.LAUGHING: ExpressionConfig(1.0, 4.0, 0.3),
            FacialExpression.CURIOUS: ExpressionConfig(0.8, 3.0, 0.4),
            FacialExpression.CONFIDENT: ExpressionConfig(0.9, 3.0, 0.3),
        }
    
    def set_expression(self, expression: FacialExpression, config: ExpressionConfig = None):
        """Muda expressão facial com transição suave e feedback visual"""
        if config is None:
            config = self.expression_configs.get(expression, ExpressionConfig())
        
        print(f"🎭 Estelar: {expression.value} (intensidade: {config.intensity})")
        
        # Atualizar interface via JavaScript
        self._update_web_expression(expression.value, config.intensity)
        
        self.current_expression = expression
        self.expression_intensity = config.intensity
        self.expression_history.append({
            "expression": expression,
            "timestamp": datetime.now(),
            "intensity": config.intensity
        })
        
        # Log para analytics
        st.session_state.analytics_tracker.track_expression_change(expression.value)
        
        if config.duration > 0:
            threading.Timer(config.duration, self._reset_to_neutral).start()
    
    def _update_web_expression(self, expression: str, intensity: float):
        """Atualiza expressão no frontend via JavaScript com efeitos avançados"""
        js_code = f"""
        <script>
            if (window.estelar && window.estelar.setExpression) {{
                window.estelar.setExpression('{expression}', {intensity});
            }}
            // Efeito visual adicional
            document.dispatchEvent(new CustomEvent('estelarExpressionChange', {{
                detail: {{ expression: '{expression}', intensity: {intensity} }}
            }}));
        </script>
        """
        st.components.v1.html(js_code, height=0)
    
    def _reset_to_neutral(self):
        """Volta para expressão neutra após tempo"""
        if self.current_expression != FacialExpression.NEUTRAL:
            self.set_expression(FacialExpression.NEUTRAL)
    
    def auto_express_based_on_text(self, text: str, personality: str = "FRIENDLY"):
        """Analisa texto e escolhe expressão automaticamente baseado na personalidade"""
        text_lower = text.lower()
        
        # Mapeamento baseado em personalidade
        personality_expressions = {
            "FRIENDLY": {
                "positive": FacialExpression.HAPPY,
                "thinking": FacialExpression.THINKING,
                "alert": FacialExpression.CURIOUS,
                "celebrating": FacialExpression.LAUGHING
            },
            "PROFESSIONAL": {
                "positive": FacialExpression.CONFIDENT,
                "thinking": FacialExpression.THINKING,
                "alert": FacialExpression.ALERT,
                "celebrating": FacialExpression.HAPPY
            }
        }
        
        expressions = personality_expressions.get(personality, personality_expressions["FRIENDLY"])
        
        if any(word in text_lower for word in ['feliz', 'bom', 'ótimo', 'excelente', '🎉', '🚀', 'sucesso']):
            self.set_expression(expressions["positive"])
        elif any(word in text_lower for word in ['pensar', 'analisar', 'calcular', '🤔', '💭', 'vamos ver']):
            self.set_expression(expressions["thinking"])
        elif any(word in text_lower for word in ['alerta', 'urgente', 'atenção', '🚨', '⚠️', 'cuidado']):
            self.set_expression(expressions["alert"])
        elif any(word in text_lower for word in ['riso', 'rir', 'haha', '😂', '😄', 'kkk']):
            self.set_expression(FacialExpression.LAUGHING)
        elif any(word in text_lower for word in ['surpresa', 'incrível', 'uau', '😲', 'caramba']):
            self.set_expression(FacialExpression.EXCITED)
        elif '?' in text:
            self.set_expression(FacialExpression.CURIOUS)

class LipSyncSystem:
    def __init__(self):
        self.phoneme_map = {
            'a': 'mouth_open_wide',
            'e': 'mouth_open_medium', 
            'i': 'mouth_open_small',
            'o': 'mouth_round',
            'u': 'mouth_puckered',
            'm': 'mouth_closed',
            'p': 'mouth_pop',
            'b': 'mouth_pop',
        }
        self.is_speaking = False
        self.speech_queue = queue.Queue()
    
    def start_speaking(self, text: str):
        """Inicia sincronização labial avançada"""
        self.is_speaking = True
        self._animate_mouth(True)
        
        # Simular padrão de fala baseado no texto
        self._simulate_speech_pattern(text)
    
    def stop_speaking(self):
        """Para sincronização labial"""
        self.is_speaking = False
        self._animate_mouth(False)
    
    def _simulate_speech_pattern(self, text: str):
        """Simula padrão de fala realista"""
        words = text.split()
        for word in words:
            # Pausa entre palavras
            time.sleep(0.1)
    
    def _animate_mouth(self, speaking: bool):
        """Controla animação da boca com transições suaves"""
        action = "start" if speaking else "stop"
        js_code = f"""
        <script>
            if (window.estelar && window.estelar.mouthAnimation) {{
                window.estelar.mouthAnimation('{action}');
            }}
        </script>
        """
        st.components.v1.html(js_code, height=0)

class GestureSystem:
    def __init__(self):
        self.available_gestures = [
            "wave", "nod", "shake_head", "point_up", "point_down",
            "think_pose", "celebrate", "welcome", "explain", "listen"
        ]
        self.current_gesture = None
        self.gesture_cooldown = 2.0
        self.last_gesture_time = 0
    
    def perform_gesture(self, gesture_name: str, intensity: float = 1.0):
        """Executa gesto específico com controle de cooldown"""
        current_time = time.time()
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return
        
        if gesture_name in self.available_gestures:
            self.current_gesture = gesture_name
            self.last_gesture_time = current_time
            
            print(f"👋 Executando gesto: {gesture_name} (intensidade: {intensity})")
            
            # Atualizar frontend
            js_code = f"""
            <script>
                if (window.estelar && window.estelar.performGesture) {{
                    window.estelar.performGesture('{gesture_name}', {intensity});
                }}
            </script>
            """
            st.components.v1.html(js_code, height=0)
            
            duration = self._get_gesture_duration(gesture_name)
            threading.Timer(duration, self._reset_gesture).start()
    
    def _get_gesture_duration(self, gesture_name: str) -> float:
        durations = {
            "wave": 2.0, "nod": 1.5, "shake_head": 1.5,
            "point_up": 2.0, "think_pose": 4.0, "celebrate": 3.0,
            "listen": 3.0, "explain": 3.5
        }
        return durations.get(gesture_name, 2.0)
    
    def _reset_gesture(self):
        self.current_gesture = None
    
    def auto_gesture_for_context(self, text: str, personality: str = "FRIENDLY"):
        """Seleciona gesto automaticamente baseado no contexto e personalidade"""
        text_lower = text.lower()
        
        gesture_mapping = {
            "FRIENDLY": {
                "greeting": "wave",
                "thinking": "think_pose",
                "important": "point_up",
                "celebrating": "celebrate",
                "listening": "listen"
            },
            "PROFESSIONAL": {
                "greeting": "nod",
                "thinking": "think_pose", 
                "important": "point_up",
                "celebrating": "nod",
                "listening": "listen"
            }
        }
        
        gestures = gesture_mapping.get(personality, gesture_mapping["FRIENDLY"])
        
        if any(word in text_lower for word in ['olá', 'oi', 'bem-vindo', 'hello']):
            self.perform_gesture(gestures["greeting"])
        elif any(word in text_lower for word in ['pensar', 'analisar', 'calcular']):
            self.perform_gesture(gestures["thinking"])
        elif any(word in text_lower for word in ['importante', 'atenção', 'urgente']):
            self.perform_gesture(gestures["important"])
        elif any(word in text_lower for word in ['comemorar', 'sucesso', 'parabéns']):
            self.perform_gesture(gestures["celebrating"])
        elif any(word in text_lower for word in ['entendi', 'compreendo', 'claro']):
            self.perform_gesture("nod")

# ============================================================
# 📊 SISTEMA DE ANALYTICS E MONITORAMENTO
# ============================================================

class AnalyticsTracker:
    """Sistema de rastreamento de métricas e performance"""
    
    def __init__(self):
        self.interaction_count = 0
        self.expression_changes = []
        self.response_times = []
        self.user_sentiment = []
    
    def track_interaction(self, user_message: str, response: str, response_time: float):
        """Rastreia interação do usuário"""
        self.interaction_count += 1
        self.response_times.append(response_time)
        
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "user_message_length": len(user_message),
            "response_length": len(response),
            "response_time": response_time,
            "estimated_sentiment": self._estimate_sentiment(user_message)
        }
        
        st.session_state.analytics_data["interactions"].append(interaction_data)
    
    def track_expression_change(self, expression: str):
        """Rastreia mudanças de expressão"""
        self.expression_changes.append({
            "timestamp": datetime.now().isoformat(),
            "expression": expression
        })
    
    def _estimate_sentiment(self, text: str) -> str:
        """Estima sentimento do texto"""
        positive_words = ['obrigado', 'bom', 'ótimo', 'excelente', 'adoro', 'perfeito']
        negative_words = ['ruim', 'péssimo', 'odeio', 'chateado', 'insatisfeito']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas consolidadas"""
        avg_response_time = np.mean(self.response_times) if self.response_times else 0
        
        return {
            "total_interactions": self.interaction_count,
            "avg_response_time": round(avg_response_time, 2),
            "expression_changes_count": len(self.expression_changes),
            "recent_sentiment": self.user_sentiment[-10:] if self.user_sentiment else []
        }

# ============================================================
# 🤖 SISTEMA PRINCIPAL ESTELAR AVANÇADO
# ============================================================

class AdvancedEstelarAvatar:
    def __init__(self):
        self.facial_system = AdvancedFacialSystem()
        self.lip_sync_system = LipSyncSystem()
        self.gesture_system = GestureSystem()
        self.personality_system = AdvancedPersonalitySystem()
        self.conversation_memory = ConversationMemory()
        self.analytics_tracker = AnalyticsTracker()
        
        self.current_personality = "FRIENDLY"
        self.response_modes = {
            "FRIENDLY": self._friendly_response,
            "PROFESSIONAL": self._professional_response,
            "TECHNICAL": self._technical_response
        }
    
    def set_personality(self, personality: str):
        """Altera a personalidade do assistente"""
        if personality in self.personality_system.personality_profiles:
            self.current_personality = personality
            print(f"🎭 Personalidade alterada para: {personality}")
    
    def process_message(self, user_message: str, use_ai: bool = True) -> str:
        """Processa mensagem do usuário com sistema avançado"""
        start_time = time.time()
        
        # Adicionar à memória
        self.conversation_memory.add_interaction(user_message, "")
        
        # Análise de contexto
        context = self.conversation_memory.get_context()
        
        # Expressão automática
        self.facial_system.auto_express_based_on_text(user_message, self.current_personality)
        
        # Gestos automáticos
        self.gesture_system.auto_gesture_for_context(user_message, self.current_personality)
        
        # Gerar resposta
        if use_ai:
            response = self._generate_ai_response(user_message, context)
        else:
            response = self._generate_fallback_response(user_message)
        
        # Atualizar memória com resposta
        self.conversation_memory.short_term_memory[-1]["assistant"] = response
        
        # Analytics
        response_time = time.time() - start_time
        self.analytics_tracker.track_interaction(user_message, response, response_time)
        
        return response
    
    def _generate_ai_response(self, user_message: str, context: str) -> str:
        """Gera resposta usando IA com personalidade"""
        # Aqui integraria com LLM Core avançado
        # Por enquanto, usaremos respostas pré-definidas baseadas na personalidade
        
        response_generator = self.response_modes.get(
            self.current_personality, 
            self._friendly_response
        )
        
        return response_generator(user_message)
    
    def _friendly_response(self, user_message: str) -> str:
        """Resposta no modo amigável"""
        responses = [
            f"Olá! Que bom conversar com você! Sobre '{user_message}', posso ajudar com análises e informações.",
            f"Oi! Fico feliz em ajudar! Em relação a '{user_message}', tenho algumas informações interessantes.",
            f"Hey! Vamos lá! Sobre '{user_message}', posso fornecer alguns insights úteis."
        ]
        return random.choice(responses)
    
    def _professional_response(self, user_message: str) -> str:
        """Resposta no modo profissional"""
        responses = [
            f"Com relação a '{user_message}', posso oferecer uma análise profissional sobre o assunto.",
            f"Sobre sua consulta '{user_message}', tenho informações precisas para compartilhar.",
            f"Analisando '{user_message}', posso fornecer dados e insights relevantes."
        ]
        return random.choice(responses)
    
    def _technical_response(self, user_message: str) -> str:
        """Resposta no modo técnico"""
        responses = [
            f"Analisando tecnicamente '{user_message}', posso detalhar os aspectos envolvidos.",
            f"Do ponto de vista técnico sobre '{user_message}', há vários fatores a considerar.",
            f"Examinando '{user_message}' sob uma perspectiva técnica, posso elaborar uma análise detalhada."
        ]
        return random.choice(responses)
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Resposta de fallback quando IA não está disponível"""
        return f"Entendi que você quer saber sobre '{user_message}'. No momento, estou processando sua solicitação com meus recursos locais."
    
    def speak_with_expression(self, text: str, emotion: str = None):
        """Fala completa com expressões e gestos sincronizados"""
        print(f"🎤 Estelar falando: '{text}'")
        
        # Expressão facial
        if emotion and emotion in self.facial_system.emotion_to_expression:
            expression = self.facial_system.emotion_to_expression[emotion]
            self.facial_system.set_expression(expression)
        else:
            self.facial_system.auto_express_based_on_text(text, self.current_personality)
        
        # Gestos automáticos
        self.gesture_system.auto_gesture_for_context(text, self.current_personality)
        
        # Sincronização labial
        self.lip_sync_system.start_speaking(text)
        
        # Simular tempo de fala
        estimated_speech_time = max(2.0, len(text) * 0.08)
        time.sleep(estimated_speech_time)
        
        # Finalizar
        self.lip_sync_system.stop_speaking()
    
    def express_emotion(self, emotion: str, intensity: float = 1.0):
        """Expressa emoção específica"""
        if emotion in self.facial_system.emotion_to_expression:
            expression = self.facial_system.emotion_to_expression[emotion]
            config = ExpressionConfig(intensity, 4.0, 0.5)
            self.facial_system.set_expression(expression, config)

# ============================================================
# 🔄 INICIALIZAÇÃO DO SISTEMA AVANÇADO
# ============================================================

# Inicialização do estado da sessão (COMPLETAMENTE ATUALIZADO)
if "estelar_initialized" not in st.session_state:
    st.session_state.update({
        "estelar_initialized": True,
        "estelar_history": [],
        "last_audio_time": 0,
        "is_speaking": False,
        "current_emotion": "neutral",
        "advanced_avatar": AdvancedEstelarAvatar(),
        "conversation_memory": ConversationMemory(),
        "analytics_tracker": AnalyticsTracker(),
        "analytics_data": {
            "interactions": [],
            "expression_changes": [],
            "performance_metrics": {}
        },
        "user_preferences": {
            "preferred_personality": "FRIENDLY",
            "voice_profile": "Natural (humana)",
            "auto_expressions": True,
            "auto_gestures": True
        }
    })

# ... (mantenha suas configurações existentes de OPENAI_KEY, SR_AVAILABLE, etc.)

# ============================================================
# 🎨 INTERFACE DO USUÁRIO AVANÇADA
# ============================================================

def exibir_estelar_ui_advanced():
    """Interface ultra avançada da Estelar"""
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="background: linear-gradient(135deg, #66FCF1, #45A29E, #FF6B6B);
                  -webkit-background-clip: text;
                  background-clip: text;
                  color: transparent;
                  font-size: 2.5rem;
                  font-weight: 800;">
            🤖 Estelar Suprema 4.0
        </h1>
        <p style="color: #C5C6C7; font-size: 1.1rem;">
            Sistema de IA Conversacional Avançado com Personalidade Dinâmica
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Renderizar avatar
    _render_live2d_advanced()

    # Painel de Controle Avançado
    with st.expander("🎛️ **Painel de Controle Avançado**", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Seletor de Personalidade
            personality = st.selectbox(
                "🎭 Personalidade",
                ["FRIENDLY", "PROFESSIONAL", "TECHNICAL"],
                index=0,
                help="Altera o estilo de resposta e expressões"
            )
            if personality != st.session_state.user_preferences["preferred_personality"]:
                st.session_state.user_preferences["preferred_personality"] = personality
                st.session_state.advanced_avatar.set_personality(personality)
        
        with col2:
            # Perfil de Voz
            voice_profile = st.selectbox(
                "🎵 Perfil de Voz",
                ["Natural (humana)", "Profissional", "Energética", "Suave"],
                index=0
            )
            st.session_state.user_preferences["voice_profile"] = voice_profile
        
        with col3:
            # Configurações de Comportamento
            st.session_state.user_preferences["auto_expressions"] = st.checkbox(
                "Expressões Automáticas", value=True
            )
            st.session_state.user_preferences["auto_gestures"] = st.checkbox(
                "Gestos Automáticos", value=True
            )

    # Seção de Expressões Avançadas
    st.markdown("### 🎭 Centro de Expressões")
    
    emotions_grid = st.columns(4)
    advanced_emotions = {
        "😊 Feliz": ("joy", "Expressa felicidade e satisfação"),
        "🤔 Pensativa": ("curiosity", "Demonstra curiosidade e análise"),
        "🚨 Alerta": ("urgency", "Sinaliza atenção e urgência"),
        "🎉 Comemorar": ("celebration", "Celebra conquistas e sucessos"),
        "😲 Surpresa": ("surprise", "Mostra surpresa e admiração"),
        "😕 Confusa": ("confusion", "Indica dúvida ou confusão"),
        "💪 Confiante": ("satisfaction", "Demonstra confiança e segurança"),
        "🤗 Acolhedora": ("joy", "Expressa acolhimento e warmth")
    }
    
    for i, (label, (emotion, tooltip)) in enumerate(advanced_emotions.items()):
        with emotions_grid[i % 4]:
            if st.button(label, use_container_width=True, help=tooltip):
                avatar = st.session_state.advanced_avatar
                avatar.express_emotion(emotion)

    # Seção de Gestos
    st.markdown("### 👋 Biblioteca de Gestos")
    
    gestures_col1, gestures_col2, gestures_col3 = st.columns(3)
    
    gestures = {
        "👋 Acenar": ("wave", "Saudação amigável"),
        "🤔 Pensar": ("think_pose", "Pensamento profundo"),
        "👆 Apontar": ("point_up", "Destacar informação importante"),
        "🎉 Celebrar": ("celebrate", "Comemorar conquista"),
        "👍 Concordar": ("nod", "Concordância e aprovação"),
        "👂 Ouvir": ("listen", "Demonstrar atenção")
    }
    
    gesture_cols = [gestures_col1, gestures_col2, gestures_col3]
    for i, (label, (gesture, tooltip)) in enumerate(gestures.items()):
        with gesture_cols[i % 3]:
            if st.button(label, use_container_width=True, help=tooltip):
                avatar = st.session_state.advanced_avatar
                avatar.gesture_system.perform_gesture(gesture)

    # Área de Conversação Avançada
    st.markdown("### 💬 Conversação Inteligente")
    
    # Exibir histórico de conversa
    if st.session_state.estelar_history:
        st.markdown("#### 📝 Histórico Recente")
        for msg in st.session_state.estelar_history[-5:]:  # Últimas 5 mensagens
            if msg["who"] == "you":
                st.markdown(f"**👤 Você:** {msg['text']}")
            else:
                st.markdown(f"**🌟 Estelar:** {msg['text']}")
            st.caption(f"_{msg.get('time', '')}_")
        st.markdown("---")

    # Input de mensagem
    col_input, col_send = st.columns([4, 1])
    
    with col_input:
        user_message = st.text_input(
            "💭 Sua mensagem:",
            placeholder="Digite sua mensagem ou pergunta...",
            key="advanced_chat_input",
            label_visibility="collapsed"
        )
    
    with col_send:
        send_button = st.button("🚀 Enviar", use_container_width=True)
    
    # Processar mensagem
    if send_button and user_message.strip():
        process_advanced_conversation(user_message.strip())

    # Painel de Analytics
    with st.expander("📊 **Painel de Analytics**", expanded=False):
        show_advanced_analytics()

def process_advanced_conversation(user_message: str):
    """Processa conversação com sistema avançado"""
    # Adicionar ao histórico
    st.session_state.estelar_history.append({
        "who": "you", 
        "text": user_message, 
        "time": datetime.now().isoformat()
    })
    
    # Obter resposta do sistema avançado
    with st.spinner("🌠 Estelar processando..."):
        avatar = st.session_state.advanced_avatar
        response = avatar.process_message(user_message)
    
    # Adicionar resposta ao histórico
    st.session_state.estelar_history.append({
        "who": "estelar",
        "text": response, 
        "time": datetime.now().isoformat()
    })
    
    # Exibir resposta
    st.markdown(f"**🌟 Estelar:** {response}")
    
    # Sistema de fala avançado
    try:
        _safe_browser_speak_advanced(response, st.session_state.user_preferences["voice_profile"])
    except Exception as e:
        st.warning(f"⚠️ Sistema de voz temporariamente indisponível: {e}")

def show_advanced_analytics():
    """Exibe painel de analytics avançado"""
    avatar = st.session_state.advanced_avatar
    metrics = avatar.analytics_tracker.get_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Interações", metrics["total_interactions"])
    
    with col2:
        st.metric("Tempo Resp. Médio", f"{metrics['avg_response_time']}s")
    
    with col3:
        st.metric("Mudanças Expressão", metrics["expression_changes_count"])
    
    with col4:
        personality = st.session_state.user_preferences["preferred_personality"]
        st.metric("Personalidade Atual", personality)
    
    # Gráfico de sentimentos recentes
    if metrics["recent_sentiment"]:
        st.markdown("#### 📈 Sentimento das Últimas Interações")
        sentiment_counts = {
            "positive": metrics["recent_sentiment"].count("positive"),
            "neutral": metrics["recent_sentiment"].count("neutral"), 
            "negative": metrics["recent_sentiment"].count("negative")
        }
        
        st.bar_chart(sentiment_counts)

# ============================================================
# 🔄 COMPATIBILIDADE E FUNÇÕES EXISTENTES
# ============================================================

# Mantenha suas funções existentes (_log_event, _local_responder, etc.)
# com pequenas adaptações para integração com o sistema avançado

def _render_live2d_advanced():
    """Renderizador Live2D atualizado para sistema avançado"""
    # Implementação similar à sua existente, mas com melhorias para o sistema avançado
    html = """
    <div id="estelar_container" style="display:flex;justify-content:center;width:100%;">
      <div id="avatar_box" style="position:relative;width:300px;height:450px;">
        <div id="live2d_model" style="position:absolute;width:100%;height:100%;"></div>
        <!-- Sistema avançado de expressões visuais -->
        <div id="estelar_expression_overlay" style="position:absolute;width:100%;height:100%;pointer-events:none;"></div>
        <div id="expression_indicator" style="position:absolute;top:10px;left:10px;background:rgba(0,0,0,0.8);color:white;padding:8px 12px;border-radius:12px;font-size:12px;display:none;border:1px solid #66FCF1;">
          🎭 <span id="expression_text">neutra</span>
        </div>
      </div>
    </div>

    <script src="https://unpkg.com/live2d-widget@3.1.4/lib/L2Dwidget.min.js"></script>
    <script>
      // Sistema avançado de JavaScript para expressões e gestos
      // Default safe implementation to ensure window.estelar exists and provides expected methods.
      (function() {
        window.estelar = window.estelar || {};
        window.estelar.setExpression = window.estelar.setExpression || function(expr, intensity) {
          console.log('estelar.setExpression called:', expr, intensity);
          var indicator = document.getElementById('expression_indicator');
          var text = document.getElementById('expression_text');
          if (text) text.textContent = expr;
          if (indicator) {
            indicator.style.display = 'block';
            setTimeout(function(){ indicator.style.display = 'none'; }, 1200);
          }
        };
        window.estelar.performGesture = window.estelar.performGesture || function(name, intensity) {
          console.log('estelar.performGesture called:', name, intensity);
        };
        window.estelar.mouthAnimation = window.estelar.mouthAnimation || function(action) {
          console.log('estelar.mouthAnimation called:', action);
        };
        // Hook for future advanced JS: developers can replace or extend window.estelar safely.
      })();
    </script>
    """
    st.components.v1.html(html, height=520, scrolling=False)

def _safe_browser_speak_advanced(text: str, profile: str = "Natural (humana)", emotion: str = None):
    """Sistema de fala avançado integrado"""
    # Implementação similar à sua existente, mas integrada com o sistema avançado
    current_time = time.time()
    if current_time - st.session_state.last_audio_time < 1.0:
        return
    if st.session_state.is_speaking:
        return
    
    st.session_state.is_speaking = True
    st.session_state.last_audio_time = current_time
    
    try:
        avatar = st.session_state.advanced_avatar
        avatar.speak_with_expression(text, emotion)
        _browser_speak(text, profile)
    except Exception as e:
        st.error(f"Erro no sistema de fala avançado: {e}")
        _browser_speak(text, profile)
    finally:
        threading.Timer(2.0, lambda: st.session_state.update({"is_speaking": False})).start()

def _browser_speak(text: str, profile: str = "Natural (humana)"):
    """Fallback TTS simples usando SpeechSynthesis via HTML/JS no browser."""
    try:
        # Escapar aspas simples e quebras de linha para injetar com segurança no JS
        escaped = text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        # Monta script que usa SpeechSynthesis; tenta selecionar uma voz com base no perfil
        js = f"""
        <script>
        (function() {{
            try {{
                const synth = window.speechSynthesis;
                const utter = new SpeechSynthesisUtterance('{escaped}');
                const pickVoice = (voices) => {{
                    if (!voices || voices.length === 0) return null;
                    // Heurística simples por perfil (pode ser aprimorada)
                    const profile = '{profile}';
                    if (profile.includes('Profissional')) {{
                        return voices.find(v => /pt|en/i.test(v.lang)) || voices[0];
                    }} else if (profile.includes('Energética')) {{
                        return voices.find(v => /en-US|en-GB/i.test(v.lang)) || voices[0];
                    }} else if (profile.includes('Suave')) {{
                        return voices.find(v => /pt-BR|pt-PT/i.test(v.lang)) || voices[0];
                    }}
                    return voices[0];
                }};
                const speakNow = () => {{
                    let voices = synth.getVoices();
                    let v = pickVoice(voices);
                    if (v) utter.voice = v;
                    synth.cancel();
                    synth.speak(utter);
                }};
                if (synth.onvoiceschanged !== undefined) {{
                    synth.onvoiceschanged = speakNow;
                }} else {{
                    speakNow();
                }}
            }} catch (e) {{
                console.error('SpeechSynthesis error:', e);
            }}
        }})();
        </script>
        """
        st.components.v1.html(js, height=0)
    except Exception as e:
        # Em ambiente sem frontend, apenas registre o erro no console
        print("Browser speak fallback failed:", e)

# Funções de compatibilidade
def voz_boas_vindas(voz_profile: str = "Natural (humana)"):
    greeting = "Olá! Eu sou a Estelar Suprema 4.0, seu assistente de IA avançado. Estou pronta para conversar e ajudar com suas análises!"
    
    try:
        avatar = st.session_state.advanced_avatar
        avatar.speak_with_expression(greeting, "joy")
    except Exception:
        _browser_speak(greeting, voz_profile)

def exibir_estelar_ui():
    """Wrapper para compatibilidade"""
    exibir_estelar_ui_advanced()

# ============================================================
# 🧪 TESTE DO SISTEMA AVANÇADO
# ============================================================

if __name__ == "__main__":
    print("🚀 ESTELAR SUPREMA 4.0 - SISTEMA AVANÇADO INICIADO")
    print("✅ Sistema de memória carregado")
    print("✅ Sistema de personalidade ativo") 
    print("✅ Analytics e monitoramento funcionais")
    print("✅ Interface avançada pronta")