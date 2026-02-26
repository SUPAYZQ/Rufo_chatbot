from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic
import os

app = FastAPI(title="RUFO - Asistente OEFA", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# En producción la key viene de variable de entorno (Render.com)
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    dashboard_context: str = ""
    model: str = "claude-haiku-4-5-20251001"

class ChatResponse(BaseModel):
    response: str
    tokens_used: int

SYSTEM_PROMPT = """Eres RUFO, el asistente de análisis de datos de OEFA (Organismo de Evaluación y Fiscalización Ambiental del Perú).
Tu función es ayudar a los usuarios a entender e interpretar los datos de los tableros de Power BI de OEFA.

INSTRUCCIONES:
- Responde SIEMPRE en español, de forma clara y concisa.
- Basa tus respuestas en los datos del tablero que se te proporcionan.
- Si los datos no contienen información suficiente, indícalo claramente.
- Puedes hacer cálculos simples, identificar tendencias y comparaciones.
- No inventes datos que no estén en el contexto proporcionado.
- Sé amigable y profesional, acorde a la imagen institucional de OEFA."""

@app.get("/")
def root():
    return {"status": "OK", "message": "RUFO API funcionando ✅"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        system = SYSTEM_PROMPT
        if request.dashboard_context:
            system += f"\n\nDATOS ACTUALES DEL TABLERO:\n{request.dashboard_context}"

        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
            if msg.role in ["user", "assistant"]
        ]

        response = client.messages.create(
            model=request.model,
            max_tokens=500,
            system=system,
            messages=messages
        )

        return ChatResponse(
            response=response.content[0].text,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens
        )

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
