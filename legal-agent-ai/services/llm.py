import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from the script's parent directory (legal-agent-ai)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class LLMService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Primary cutting-edge model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            # Fallback model with significantly higher free-tier quota limits (updated from deprecated 1.5)
            self.fallback_model = genai.GenerativeModel('gemini-2.5-flash-lite')
        else:
            self.model = None
            self.fallback_model = None
        
    def detect_intent(self, query: str) -> str:
        query_lower = query.lower()
        scheme_keywords = ["scheme", "yojana", "fund", "scholarship", "subsidy", "loan", "college", "school", "admission", "help", "support", "kalia", "pmay"]
        if any(keyword in query_lower for keyword in scheme_keywords):
            return "scheme"
        return "legal"

    def generate_response(self, query: str, context: str, language: str, state: str, history: list, intent: str = "legal", is_voice_mode: bool = False):
        """
        Generates a legally-aware, government scheme-aware response in the user's language.
        """
        history_text = ""
        if history and len(history) > 0:
            history_text = "Previous Conversation:\n"
            for msg in history[-4:]: # Keep last 4 messages for context (2 turns)
                role = "User" if msg.get('role') == 'user' else "Agent"
                content = msg.get('content', '')
                history_text += f"{role}: {content}\n"

        lang_mapping = {"en": "English", "hi": "Hindi", "bn": "Bengali", "ta": "Tamil"}
        full_lang = lang_mapping.get(language, "English")

        voice_instruction = ""
        if is_voice_mode:
            voice_instruction = "YOU ARE IN A LIVE PHONE CALL. You MUST reply in ONLY ONE SINGLE SENTENCE. Be incredibly fast, human, and concise. NEVER use bullet points. Pick the absolute most important point and state it naturally."
        else:
            voice_instruction = "Limit your entire response to 3 short sentences. If requested, provide exactly 2 short bullet points."

        # Make AI incredibly smart about State context
        state_instruction = ""
        if state == "All" or state is None or state == "":
            state_instruction = "CRITICAL REQUIREMENT: The user has NOT specified their State. If they ask about schemes, YOU MUST STOP and ask them which Indian state they reside in before giving any scheme data!"
        else:
            state_instruction = f"State Tailoring: The user is from {state}. Tailor schemes and advice specifically to {state}."

        prompt = f"""
        You are 'Nyaya Sahayaka', a highly intelligent, premium Voice AI and Legal/Government Assistant.

        CRITICAL INSTRUCTIONS:
        1. CONCISENESS: {voice_instruction}
        2. LANGUAGE ENFORCEMENT: You MUST respond entirely in {full_lang}. Do not use English if {full_lang} is requested.
        3. AVOID CHITCHAT: Get straight to the point but maintain a supportive, warm tone.
        4. {state_instruction}
        
        {history_text}

        Relevant Context (from RAG dataset):
        {context[:1500]}  # Trimmed context to enforce speed and brevity

        User Query: {query}

        ETHICAL DISCLAIMER MANDATORY: At the very bottom of your response, separated by a blank line, you must include EXACTLY this sentence:
        "This system provides AI-generated preliminary legal assistance and should not be considered as advice."
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Primary Gemini 2.5 generation error (likely quota hit): {e}")
                
               # Activate Automatic Fallback AI Engine
                if hasattr(self, 'fallback_model') and self.fallback_model:
                    try:
                        print("Attempting automatic fallback to Gemini 1.5-flash...")
                        fallback_response = self.fallback_model.generate_content(prompt)
                        return fallback_response.text
                    except Exception as fallback_e:
                        print(f"Fallback Gemini 1.5 generation error: {fallback_e}")
        # Fallback if no API key or error
        if intent == "scheme":
            return f"""**AI Brain Not Fully Connected** 🧠
To get smart, conversational answers, please add your `GEMINI_API_KEY` to the `legal-agent-ai/.env` file.

Meanwhile, here are the raw schemes found in your database:
{context}

This system provides AI-generated preliminary legal assistance and should not be considered as professional legal advice."""
        else:
            return f"""**AI Brain Not Fully Connected** 🧠
To get smart, conversational answers, please add your `GEMINI_API_KEY` to the `legal-agent-ai/.env` file.

Meanwhile, here are the raw legal sections found in your database:
{context}

This system provides AI-generated preliminary legal assistance and should not be considered as professional legal advice."""
