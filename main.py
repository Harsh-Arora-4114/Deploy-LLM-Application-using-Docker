from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from llama_cpp import Llama
import os

app = FastAPI()

llm = Llama(
    model_path="./tinyllama-ecommerce-q4.gguf",
    n_ctx=512,
    n_threads=4,
    verbose=False
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/health")
def health():
    return {"status": "Aria is running"}

@app.post("/chat")
def chat(request: ChatRequest):
    prompt = f"<|system|>You are a helpful e-commerce customer support assistant.</s><|user|>{request.message}</s><|assistant|>"
    output = llm(
        prompt,
        max_tokens=256,
        stop=["</s>", "<|user|>"],
        echo=False
    )
    response_text = output["choices"][0]["text"].strip()
    return ChatResponse(response=response_text)

# Explicit root route — serves index.html directly, avoiding mount conflicts
@app.get("/")
def root():
    return FileResponse("static/index.html")

# Mount static assets (CSS, JS, images) under /static
# NOT at "/" — that would conflict with the routes above
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)