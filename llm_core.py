# ============================
#  llm_core.py – Motor Avançado de LLM para Estelar PRIME
#  Autor: KLStarTech / Kauã
#  Versão: 2.0 - Com Cache, Retry e Métricas
# ============================

import os
import json
import requests
import time
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_core")

# ============================
# ⚙️ CONFIGURAÇÃO AVANÇADA
# ============================

# BACKEND PRINCIPAL (pode ser override pelo Estelar.py)
BACKEND = os.getenv("LLM_BACKEND", "local").lower()

# ====== KEYS =======
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

# ====== CONFIGURAÇÕES AVANÇADAS =======
CACHE_DURATION = int(os.getenv("LLM_CACHE_MINUTES", "10"))  # Cache em minutos
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
REQUEST_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))
ENABLE_METRICS = os.getenv("LLM_ENABLE_METRICS", "true").lower() == "true"

# ============================
# 🗂️ SISTEMA DE CACHE AVANÇADO
# ============================

class LLMCache:
    """Sistema de cache em memória para respostas LLM"""
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, prompt: str, system_prompt: str, model: str) -> str:
        """Gera chave única para cache"""
        content = f"{model}:{system_prompt}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, system_prompt: str, model: str) -> Optional[Dict]:
        """Recupera do cache se existir e não estiver expirado"""
        with self._lock:
            key = self._generate_key(prompt, system_prompt, model)
            if key in self._cache:
                cached_data = self._cache[key]
                if datetime.now() < cached_data['expires_at']:
                    self.hits += 1
                    logger.info(f"✅ Cache HIT para {model}")
                    return cached_data['response']
                else:
                    # Expirou, remover
                    del self._cache[key]
            
            self.misses += 1
            return None
    
    def set(self, prompt: str, system_prompt: str, model: str, response: Dict):
        """Armazena no cache com timestamp de expiração"""
        with self._lock:
            key = self._generate_key(prompt, system_prompt, model)
            self._cache[key] = {
                'response': response,
                'expires_at': datetime.now() + timedelta(minutes=CACHE_DURATION),
                'created_at': datetime.now()
            }
            logger.info(f"💾 Cache SET para {model}")

# Instância global do cache
llm_cache = LLMCache()

# ============================
# 📊 SISTEMA DE MÉTRICAS
# ============================

@dataclass
class LLMMetrics:
    """Métricas de performance dos LLMs"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_response_time: float = 0
    backend_usage: Dict[str, int] = None
    
    def __post_init__(self):
        if self.backend_usage is None:
            self.backend_usage = {}
    
    def record_request(self, backend: str, success: bool, tokens: int = 0, response_time: float = 0):
        """Registra uma requisição"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            self.total_tokens += tokens
            self.total_response_time += response_time
        else:
            self.failed_requests += 1
        
        self.backend_usage[backend] = self.backend_usage.get(backend, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas atuais"""
        avg_response_time = (self.total_response_time / self.successful_requests 
                           if self.successful_requests > 0 else 0)
        
        return {
            "total_requests": self.total_requests,
            "success_rate": (self.successful_requests / self.total_requests * 100 
                           if self.total_requests > 0 else 0),
            "avg_response_time": round(avg_response_time, 2),
            "total_tokens": self.total_tokens,
            "backend_usage": self.backend_usage,
            "cache_hits": llm_cache.hits,
            "cache_misses": llm_cache.misses,
            "cache_hit_rate": (llm_cache.hits / (llm_cache.hits + llm_cache.misses) * 100 
                             if (llm_cache.hits + llm_cache.misses) > 0 else 0)
        }

# Métricas globais
llm_metrics = LLMMetrics()

# ============================
# 🔥 FUNÇÃO PRINCIPAL MELHORADA
# ============================

def ask(prompt: str, 
        system_prompt: str = None, 
        model: str = None, 
        timeout: int = None,
        use_cache: bool = True,
        max_retries: int = None) -> Dict[str, Any]:
    """
    Função principal melhorada com cache, retry e métricas
    
    Args:
        prompt: Texto do usuário
        system_prompt: Prompt do sistema
        model: Backend a ser usado
        timeout: Timeout personalizado
        use_cache: Usar cache (default True)
        max_retries: Número máximo de tentativas
    
    Returns:
        Dict com text, usage, metrics e metadata
    """
    
    start_time = time.time()
    backend = (model or BACKEND).lower()
    timeout = timeout or REQUEST_TIMEOUT
    max_retries = max_retries or MAX_RETRIES
    
    # Verificar cache primeiro
    if use_cache:
        cached_response = llm_cache.get(prompt, system_prompt, backend)
        if cached_response:
            return {
                **cached_response,
                "cached": True,
                "cache_hit": True,
                "timestamp": datetime.now().isoformat()
            }
    
    # Sistema de retry com fallback
    last_error = None
    for attempt in range(max_retries):
        try:
            logger.info(f"🚀 Tentativa {attempt + 1} para {backend}")
            
            # Selecionar backend
            if backend == "openai":
                response = _openai_chat_avancado(prompt, system_prompt, timeout)
            elif backend == "gemini":
                response = _gemini_chat_avancado(prompt, system_prompt, timeout)
            elif backend == "deepseek":
                response = _deepseek_chat_avancado(prompt, system_prompt, timeout)
            elif backend == "blackbox":
                response = _blackbox_avancado(prompt, system_prompt)
            else:
                response = _local_avancado(prompt, system_prompt)
            
            # Calcular tempo de resposta
            response_time = time.time() - start_time
            
            # Registrar métricas
            tokens = response.get('usage', {}).get('total_tokens', 0)
            llm_metrics.record_request(
                backend=backend,
                success=True,
                tokens=tokens,
                response_time=response_time
            )
            
            # Adicionar metadata
            enhanced_response = {
                **response,
                "backend": backend,
                "response_time": round(response_time, 2),
                "timestamp": datetime.now().isoformat(),
                "cached": False,
                "attempt": attempt + 1
            }
            
            # Armazenar no cache se bem-sucedido
            if use_cache and response.get('text'):
                llm_cache.set(prompt, system_prompt, backend, enhanced_response)
            
            logger.info(f"✅ {backend} respondendo em {response_time:.2f}s")
            return enhanced_response
            
        except Exception as e:
            last_error = str(e)
            logger.warning(f"⚠️ Tentativa {attempt + 1} falhou: {last_error}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"⏳ Aguardando {wait_time}s antes de retry...")
                time.sleep(wait_time)
    
    # Todas as tentativas falharam
    llm_metrics.record_request(backend=backend, success=False)
    
    fallback_response = _local_avancado(prompt, system_prompt)
    return {
        **fallback_response,
        "backend": "local_fallback",
        "error": last_error,
        "response_time": round(time.time() - start_time, 2),
        "timestamp": datetime.now().isoformat(),
        "cached": False,
        "attempt_failed": True
    }

# ============================
# 🧠 BACKENDS AVANÇADOS
# ============================

def _openai_chat_avancado(prompt: str, system_prompt: str, timeout: int) -> Dict:
    """OpenAI com tratamento avançado de erros"""
    if not OPENAI_KEY:
        raise ValueError("OpenAI API não configurada")
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt or "Você é Estelar, um assistente IA inteligente e útil."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        
        text = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})
        
        return {
            "text": text,
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            },
            "model": result.get("model", "gpt-4o-mini")
        }
        
    except requests.exceptions.Timeout:
        raise Exception("OpenAI timeout - servidor não respondeu")
    except requests.exceptions.RequestException as e:
        raise Exception(f"OpenAI erro de rede: {e}")
    except KeyError as e:
        raise Exception(f"OpenAI resposta inválida: {e}")

def _gemini_chat_avancado(prompt: str, system_prompt: str, timeout: int) -> Dict:
    """Gemini com tratamento avançado"""
    if not GEMINI_KEY:
        raise ValueError("Gemini API não configurada")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
    
    full_prompt = f"{system_prompt or 'Você é Estelar.'}\n\nUsuário: {prompt}"
    
    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000,
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        # Extrair texto de forma segura
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                text = candidate["content"]["parts"][0]["text"]
            else:
                raise KeyError("Estrutura de resposta Gemini inválida")
        else:
            raise KeyError("Nenhum candidato na resposta Gemini")
        
        return {
            "text": text,
            "usage": {
                "prompt_tokens": data.get("usageMetadata", {}).get("promptTokenCount", 0),
                "completion_tokens": data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                "total_tokens": data.get("usageMetadata", {}).get("totalTokenCount", 0)
            },
            "model": "gemini-pro"
        }
        
    except requests.exceptions.Timeout:
        raise Exception("Gemini timeout")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Gemini erro de rede: {e}")

def _deepseek_chat_avancado(prompt: str, system_prompt: str, timeout: int) -> Dict:
    """DeepSeek com tratamento avançado"""
    if not DEEPSEEK_KEY:
        raise ValueError("DeepSeek API não configurada")
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt or "Você é Estelar."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        
        text = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})
        
        return {
            "text": text,
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            },
            "model": result.get("model", "deepseek-chat")
        }
        
    except requests.exceptions.Timeout:
        raise Exception("DeepSeek timeout")
    except requests.exceptions.RequestException as e:
        raise Exception(f"DeepSeek erro de rede: {e}")

def _blackbox_avancado(prompt: str, system_prompt: str) -> Dict:
    """Blackbox com resposta mais inteligente"""
    responses = [
        f"🔮 **Estelar Blackbox**\n\nBaseado no seu prompt: '{prompt}'\n\n"
        f"Em um sistema completo, eu analisaria isso considerando: "
        f"contexto histórico, padrões similares e tendências atuais. "
        f"Recomendo configurar uma API real para respostas mais precisas.",
        
        f"🤖 **Modo Simulado**\n\nPara: '{prompt}'\n\n"
        f"Se estivesse conectado a um backend real, forneceria uma análise "
        f"detalhada com dados em tempo real. Configure OPENAI_API_KEY ou "
        f"GEMINI_API_KEY no .env para respostas completas.",
        
        f"💡 **Insight Simulado**\n\nSobre: '{prompt}'\n\n"
        f"Esta é uma demonstração do sistema Estelar. Com uma API configurada, "
        f"eu poderia oferecer análises profundas, sugestões específicas e "
        f"respostas contextualizadas."
    ]
    
    import random
    return {
        "text": random.choice(responses),
        "usage": {
            "prompt_tokens": len(prompt),
            "completion_tokens": 50,
            "total_tokens": len(prompt) + 50
        },
        "model": "blackbox-simulated"
    }

def _local_avancado(prompt: str, system_prompt: str) -> Dict:
    """Fallback local inteligente"""
    responses = [
        f"🌙 **Estelar Local**\n\nVocê disse: '{prompt}'\n\n"
        f"Estou operando no modo offline. Para respostas completas com IA, "
        f"configure uma chave de API no arquivo .env:\n\n"
        f"• OPENAI_API_KEY=sua_chave_openai\n"
        f"• GEMINI_API_KEY=sua_chave_gemini\n"
        f"• DEEPSEEK_API_KEY=sua_chave_deepseek\n\n"
        f"Mesmo offline, posso ajudar com funcionalidades básicas do sistema!",
        
        f"🔧 **Modo Autônomo**\n\nEntendi: '{prompt}'\n\n"
        f"No momento, estou sem conexão com serviços de IA. "
        f"Enquanto isso, posso ajudar com:\n\n"
        f"• 📊 Visualização de dados existentes\n"
        f"• 💾 Operações locais do sistema\n"
        f"• 📋 Processos automatizados\n"
        f"• 🎯 Análises básicas\n\n"
        f"Configure uma API para recursos avançados de IA!"
    ]
    
    import random
    return {
        "text": random.choice(responses),
        "usage": {
            "prompt_tokens": len(prompt),
            "completion_tokens": 80,
            "total_tokens": len(prompt) + 80
        },
        "model": "local-fallback"
    }

# ============================
# 🛠️ FUNÇÕES UTILITÁRIAS
# ============================

def get_metrics() -> Dict[str, Any]:
    """Retorna métricas atuais do sistema LLM"""
    return llm_metrics.get_stats()

def clear_cache():
    """Limpa o cache de respostas"""
    llm_cache._cache.clear()
    llm_cache.hits = 0
    llm_cache.misses = 0
    logger.info("🗑️ Cache limpo")

def get_active_backends() -> List[str]:
    """Retorna backends disponíveis baseados na configuração"""
    backends = []
    
    if OPENAI_KEY:
        backends.append("openai")
    if GEMINI_KEY:
        backends.append("gemini")
    if DEEPSEEK_KEY:
        backends.append("deepseek")
    
    # Sempre incluir fallbacks
    backends.extend(["blackbox", "local"])
    
    return backends

def health_check() -> Dict[str, Any]:
    """Verifica saúde dos backends configurados"""
    health = {
        "timestamp": datetime.now().isoformat(),
        "cache_status": {
            "entries": len(llm_cache._cache),
            "hits": llm_cache.hits,
            "misses": llm_cache.misses
        },
        "backends": {}
    }
    
    # Testar backends configurados
    test_prompt = "Teste de saúde - responda apenas 'OK'"
    
    for backend in get_active_backends():
        if backend not in ["blackbox", "local"]:  # Não testar fallbacks
            try:
                start = time.time()
                response = ask(test_prompt, "Você é um assistente.", backend, use_cache=False)
                response_time = time.time() - start
                
                health["backends"][backend] = {
                    "status": "healthy" if response.get("text") else "unhealthy",
                    "response_time": round(response_time, 2),
                    "cached": response.get("cached", False)
                }
            except Exception as e:
                health["backends"][backend] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            health["backends"][backend] = {
                "status": "simulated",
                "response_time": 0.01
            }
    
    return health

# ============================
# 🎯 INICIALIZAÇÃO
# ============================

def initialize_llm_system():
    """Inicializa o sistema LLM e loga status"""
    active_backends = get_active_backends()
    configured_backends = [b for b in active_backends if b not in ["blackbox", "local"]]
    
    logger.info("🚀 Inicializando Sistema LLM Avançado")
    logger.info(f"📡 Backends configurados: {configured_backends}")
    logger.info(f"🔄 Backends ativos: {active_backends}")
    logger.info(f"💾 Cache ativo: {CACHE_DURATION}min")
    logger.info(f"🛡️ Máximo de retries: {MAX_RETRIES}")
    
    if not configured_backends:
        logger.warning("⚠️ Nenhuma API externa configurada - usando modo local")

# Inicializar ao importar
initialize_llm_system()