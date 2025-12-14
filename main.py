# main.py
import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 1. Setup App
app = FastAPI()

# Allow your Frontend to talk to this Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Define the Request Structure
class QueryRequest(BaseModel):
    query: str

# 3. The Logic
@app.post("/chat")
async def chat(request: QueryRequest):
    # Load keys from Environment Variables (We set these in Render later)
    API_KEY = os.environ.get("GEMINI_API_KEY")
    STORE_ID = os.environ.get("STORE_ID")

    if not API_KEY or not STORE_ID:
        raise HTTPException(status_code=500, detail="Missing API Key or Store ID")

    # The Endpoint for Gemini 1.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-002:generateContent?key={API_KEY}"

    # The Payload (Connecting your specific Knowledge Base)
    payload = {
        "contents": [{
            "parts": [{"text": request.query}]
        }],
        "tools": [{
            "file_search": {
                "retrieval_tool": {
                    "source": {
                        "file_search_store": {"name": STORE_ID}
                    }
                }
            }
        }]
    }

    try:
        # Call Google
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        data = response.json()

        # Extract the Answer
        # (Navigates the JSON tree to find the text)
        try:
            answer = data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            answer = "I couldn't find an answer in the documents."

        return {"answer": answer}

    except Exception as e:
        return {"answer": f"Error contacting Google: {str(e)}"}
