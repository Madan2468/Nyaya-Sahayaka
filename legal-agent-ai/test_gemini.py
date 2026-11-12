import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=key)

try:
    model1 = genai.GenerativeModel('gemini-2.5-flash-lite')
    response1 = model1.generate_content("Testing 2.5 flash lite...")
    print("SUCCESS 2.5-flash-lite:", response1.text[:50])
except Exception as e:
    print(f"ERROR 2.5-flash-lite: {e}")
