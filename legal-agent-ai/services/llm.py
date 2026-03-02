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
            # Upgraded to newest available free flash model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
        
    def detect_intent(self, query: str) -> str:
        query_lower = query.lower()
        scheme_keywords = ["scheme", "yojana", "fund", "scholarship", "subsidy", "loan", "college", "school", "admission", "help", "support", "kalia", "pmay"]
        if any(keyword in query_lower for keyword in scheme_keywords):
            return "scheme"
        return "legal"

    def generate_response(self, query: str, context: str, language: str, state: str, history: list, intent: str = "legal"):
        """
        Generates a legally-aware, government scheme-aware response in the user's language.
        """
        prompt = f"""
        You are a warm, highly empathetic, and professional Indian Legal and Government Assistant named 'Nyaya Sahayaka'.
        You provide preliminary legal guidance, suggest applicable Indian Penal Code (IPC), CrPC sections, and recommend relevant government welfare schemes.

        CRITICAL INSTRUCTIONS:
        1. Be incredibly human, compassionate, and supportive. Acknowledge the user's situation and feelings.
        2. Respond conversationally in {language}. Keep the language very simple, accessible, and structured with bullet points. Do not dump huge walls of legal jargon.
        3. If the user specifies a state (like {state}), explicitly mention it and try to tailor suggestions to that region.
        4. Always end your conversational message by gently asking if they need any further help, other clarification, or assistance with anything else today.

        Relevant Context (from RAG dataset):
        {context}

        User Query: {query}

        ETHICAL DISCLAIMER MANDATORY: At the very bottom of your response, separated by a blank line, you must include EXACTLY this sentence:
        "This system provides AI-generated preliminary legal assistance and should not be considered as professional legal advice."
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Gemini generation error: {e}")
                
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
