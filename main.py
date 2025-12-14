import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 1. CORS Setup (Allows your frontend to talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Input Structure
class QueryRequest(BaseModel):
    query: str

# 3. Home Route (To check if server is running)
@app.get("/")
def home():
    return {"status": "Alive", "message": "RAG Backend is running"}

# 4. Chat Route
@app.post("/chat")
async def chat(request: QueryRequest):
    # Load keys (Ensure these are set in your Render Dashboard)
    API_KEY = os.environ.get("GEMINI_API_KEY")
    STORE_ID = os.environ.get("STORE_ID")

    if not API_KEY or not STORE_ID:
        raise HTTPException(status_code=500, detail="Missing Keys on Server")

    # API Endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    # ✅ FIXED PAYLOAD
    payload = {
        "contents": [{
            "parts": [{"text": request.query}]
        }],
        "tools": [{
            "file_search": {
                "file_search_store_names": [STORE_ID]
            }
        }]
    }

    try:
        # Send Request to Google
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        # Check for non-200 errors
        if response.status_code != 200:
            return {"answer": f"Google Error ({response.status_code}): {response.text}"}

        data = response.json()

        # Extract Answer safely
        try:
            answer = data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError, TypeError):
            answer = "I couldn't find an answer in the documents. (Check if the PDF has relevant info)"

        return {"answer": answer}

    except Exception as e:
        return {"answer": f"Server Error: {str(e)}"}
