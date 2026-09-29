"""
CareSim AI - Groq Service Module
Integrates with Groq API using official Groq SDK with automatic retry,
structured prompt handling, and safe demo mode fallback.
"""
import os
import time
import json
import logging
from typing import Dict, Any, List, Optional
import config

logger = logging.getLogger(__name__)

# Try importing groq SDK
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

class GroqService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # Prefer provided key, then environment, then streamlit secrets
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        if not self.api_key:
            # Check Streamlit secrets if running inside streamlit
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                    self.api_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                pass
        
        self.model = model or os.environ.get("GROQ_MODEL", config.GROQ_MODEL)
        self.client = None
        if GROQ_AVAILABLE and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
                self.client = None

    def is_configured(self) -> bool:
        """Returns True if Groq SDK is available and an API key is present."""
        return bool(GROQ_AVAILABLE and self.client and self.api_key)

    def test_connection(self) -> Dict[str, Any]:
        """Performs a lightweight connection test without exposing credentials."""
        if not GROQ_AVAILABLE:
            return {
                "success": False,
                "message": "Groq Python SDK is not installed. Running in Demo Mode.",
                "demo_mode": True
            }
        if not self.api_key:
            return {
                "success": False,
                "message": "GROQ_API_KEY is not configured. Running in Demo Mode.",
                "demo_mode": True
            }
        try:
            # Single lightweight token completion
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
                temperature=0.0
            )
            return {
                "success": True,
                "message": f"Connected successfully to Groq ({self.model}).",
                "demo_mode": False
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Groq API connection error: {str(e)}",
                "demo_mode": True
            }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.6,
        max_tokens: int = 1024,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes a chat completion with retry and error handling.
        Returns dict with keys: 'content', 'is_demo', 'error'.
        """
        if not self.is_configured():
            return {
                "content": "",
                "is_demo": True,
                "error": "Groq API key not configured. Using deterministic simulation mode."
            }

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                if response_format:
                    kwargs["response_format"] = response_format

                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                return {
                    "content": content,
                    "is_demo": False,
                    "error": None
                }
            except Exception as e:
                err_msg = str(e)
                logger.error(f"Groq API Attempt {attempt + 1} failed: {err_msg}")
                if "rate_limit" in err_msg.lower() or "429" in err_msg:
                    time.sleep(1.5 * (attempt + 1))
                elif attempt == max_retries:
                    return {
                        "content": "",
                        "is_demo": True,
                        "error": f"Groq API error after {max_retries + 1} attempts: {err_msg}"
                    }
                else:
                    time.sleep(1.0)
        
        return {"content": "", "is_demo": True, "error": "Unknown error invoking Groq API"}
