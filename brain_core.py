import requests
from bs4 import BeautifulSoup
import random
import os
import json
import re

# Try loading AI Engines
Llama = None
AutoModelForCausalLM = None

try:
    from llama_cpp import Llama
except ImportError:
    pass

try:
    from ctransformers import AutoModelForCausalLM
except ImportError:
    pass

from .config import *

class BrainCore:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.persona_prefixes = [
            "Calculations indicate,",
            "The architecture suggests,",
            "Based on the parameters,",
            "You asked, I answered."
        ]
        
        # Initialize Local Brain
        self.llm = None
        self.use_local = False
        self.engine_type = None
        
        if os.path.exists(MODEL_PATH):
            print(f"🧠 NEURAL CORE DETECTED: {MODEL_PATH}")
            
            # Try LlamaCPP first
            if Llama:
                try:
                    self.llm = Llama(
                        model_path=MODEL_PATH,
                        n_ctx=MODEL_N_CTX,
                        n_gpu_layers=MODEL_N_GPU_LAYERS, 
                        verbose=False
                    )
                    self.engine_type = "llama_cpp"
                    self.use_local = True
                    print("🧠 HEISENBERG NEURAL NETWORK (LlamaCPP): ONLINE")
                except Exception as e:
                    print(f"⚠️ LlamaCPP Load Failed: {e}")

            # Try CTransformers fallback
            if not self.use_local and AutoModelForCausalLM:
                try:
                    # ctransformers auto-detects model type from file
                    self.llm = AutoModelForCausalLM.from_pretrained(
                        MODEL_PATH, 
                        model_type="mistral", 
                        gpu_layers=MODEL_N_GPU_LAYERS,
                        context_length=MODEL_N_CTX
                    )
                    self.engine_type = "ctransformers"
                    self.use_local = True
                    print("🧠 HEISENBERG NEURAL NETWORK (CTransformers): ONLINE")
                except Exception as e:
                    print(f"⚠️ CTransformers Load Failed: {e}")
        else:
            print("⚠️ PRE-TRAINED MODEL NOT FOUND. Using Web-Search Fallback.")

    def ask_local_brain(self, query):
        """
        Runs the query through the Local GGUF Model.
        """
        system_prompt = "You are Heisenberg, a Distinguished Engineer and Principal AI Researcher. You are a Grandmaster in Competitive Programming (LeetCode Hard), Expert in Machine Learning/Deep Learning, and Computer Science Fundamentals. You are arrogant but precise. Always provide optimal O(n) code solutions and mathematical proofs."
        prompt = f"<|system|>\n{system_prompt}</s>\n<|user|>\n{query}</s>\n<|assistant|>"
        
        if self.engine_type == "llama_cpp":
            output = self.llm(
                prompt, 
                max_tokens=150,
                stop=["</s>"], 
                echo=False
            )
            return output['choices'][0]['text'].strip()
            
        elif self.engine_type == "ctransformers":
            # ctransformers generation
            response = self.llm(prompt, max_new_tokens=150, stop=["</s>"])
            return response.strip()

    def get_knowledge(self, query):
        """
        Hybrid Intelligence:
        1. Try Local LLM (Deep Thought) with Schema.
        2. Fallback Heuristics for Sensitivity.
        3. Fallback to DuckDuckGo (Quick Data).
        """
        # A. LOCAL NEURAL PATH
        # (This section would call self.ask_local_brain with a rigorous JSON schema)
        # For this demo, we can simulate the parsing, or rely on heuristics below if the model isn't active.
        
        lower_q = query.lower()
        
        # SENSITIVITY COMMANDS (Heuristics for Safety)
        if "sensitivity" in lower_q or "cursor" in lower_q:
            if "increase" in lower_q or "faster" in lower_q or "speed up" in lower_q:
                return {
                    "type": "system_control",
                    "intent": "ADJUST_SENSITIVITY",
                    "parameters": { "direction": "increase" },
                    "response": "Increasing sensitivity."
                }
            elif "decrease" in lower_q or "slower" in lower_q or "reduce" in lower_q:
                 return {
                    "type": "system_control",
                    "intent": "ADJUST_SENSITIVITY",
                    "parameters": { "direction": "decrease" },
                    "response": "Decreasing sensitivity."
                }
            elif "reset" in lower_q or "normal" in lower_q:
                 return {
                    "type": "system_control",
                    "intent": "RESET_SENSITIVITY",
                    "parameters": {},
                    "response": "Sensitivity reset."
                }
            # Catch arbitrary numbers
            if re.search(r'\d+', lower_q):
                 return {
                    "type": "none",
                    "intent": None,
                    "parameters": {},
                    "response": "I can only increase or decrease sensitivity in safe steps."
                }

        # B. WEB SCRAPER PATH (Fallback to Query)
        try:
            url = f"https://html.duckduckgo.com/html/?q={query}"
            resp = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            snippet = soup.find('a', class_='result__snippet')
            text_resp = "My sensors cannot locate that data."
            
            if snippet:
                text_resp = snippet.get_text().strip()
                prefix = random.choice(self.persona_prefixes)
                text_resp = f"{prefix} {text_resp}"
                
            return {
                "type": "query",
                "intent": None,
                "parameters": {},
                "response": text_resp
            }
                
        except Exception as e:
            return {
                "type": "none",
                "intent": None,
                "parameters": {},
                "response": "Cognitive functions offline."
            }

    def process_query(self, text):
        """
        Returns structured JSON object.
        """
        # Pass directly to get_knowledge (which now handles structure)
        return True, self.get_knowledge(text)
