import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

# Local imports
from services.rag import RAGService
from services.llm import LLMService

app = FastAPI(
    title="Multilingual AI Legal & Government Scheme Assistance",
    description="AI Microservice for Legal Assistance and Document Generation",
    version="1.0.0"
)

# Allow CORS for the Next.js frontend
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "https://nayaya-sahayaka.netlify.app,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
rag_service = RAGService()
llm_service = LLMService()

class ChatRequest(BaseModel):
    query: str
    language: str = "en"
    state: Optional[str] = None
    gender: Optional[str] = "All"
    caste: Optional[str] = "All"
    is_voice_mode: bool = False
    chat_history: Optional[List[dict]] = []

class DocumentRequest(BaseModel):
    document_type: str
    details: dict
    language: str = "en"

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Legal AI Microservice is running."}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Detect Intent
        intent = llm_service.detect_intent(request.query)

        # Basic state extraction if not provided explicitly by frontend
        detected_state = request.state
        if not detected_state:
            states = ["andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal", "delhi"]
            for s in states:
                if s in request.query.lower():
                    detected_state = s.title()
                    break

        # 2. Retrieve relevant legal sections and schemes
        # Schemes are diverse and regional Kaggle data might lack proper "state" tags.
        # We leverage Gemini 1 Million token context window by pulling top_k=60 for schemes.
        top_k = 60 if intent == "scheme" else 8
        
        # Optimize the vector search query by explicitly injecting profile parameters
        search_query = request.query
        if intent == "scheme":
            if detected_state:
                search_query += f" for {detected_state} state"
            if request.gender and request.gender != "All":
                search_query += f" specifically for {request.gender}"
            if request.caste and request.caste != "All":
                search_query += f" category {request.caste}"
            
        context = rag_service.retrieve(search_query, top_k=top_k, intent=intent)
        
        # Provide strict filtering instructions to LLM
        profile_instructions = ""
        if intent == "scheme":
            profile_instructions = f"\n\n[CRITICAL FILTERING]: The user's profile is State: {detected_state}, Gender: {request.gender}, Caste/Category: {request.caste}. You MUST filter out any schemes in your context that contradict these demographics."
            if not request.is_voice_mode:
                 profile_instructions += "\n\n[RESPONSE FORMAT]: End your response with a 'Next Steps' section formatted strictly as a Markdown Task List (e.g., `- [ ] Gather Aadhaar Card`)."
        
        # 3. Generate response using LLM with context
        response_text = llm_service.generate_response(
            query=request.query + profile_instructions,
            context=context,
            language=request.language,
            state=detected_state,
            history=request.chat_history,
            intent=intent,
            is_voice_mode=request.is_voice_mode
        )
        
        return {
            "response": response_text,
            "context_used": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-document")
async def generate_document(request: DocumentRequest):
    # Stub for document generation logic
    try:
        # Generate the document content via LLM and convert to PDF
        return {"status": "success", "download_url": "stub_url"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
