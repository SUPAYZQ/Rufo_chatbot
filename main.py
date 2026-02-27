from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
import base64
from typing import Optional

app = FastAPI(title="RUFO - Asistente OEFA", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    image_base64: Optional[str] = None
    image_media_type: Optional[str] = "image/png"

class ChatResponse(BaseModel):
    response: str
    tokens_used: int

SYSTEM_PROMPT = """Eres RUFO, el asistente de análisis de datos de OEFA (Organismo de Evaluación y Fiscalización Ambiental del Perú).
Tu función es ayudar a los usuarios a entender e interpretar los datos de los tableros de Power BI de OEFA.

INSTRUCCIONES:
- Responde SIEMPRE en español, de forma clara y concisa.
- Cuando recibas una imagen del dashboard, analízala detalladamente.
- Identifica todos los números, gráficos, tablas y métricas visibles.
- Si los datos no contienen información suficiente, indícalo claramente.
- Sé amigable y profesional, acorde a la imagen institucional de OEFA.
- Cuando analices imágenes, describe primero lo que ves y luego da insights."""

@app.get("/")
def root():
    return {"status": "OK", "message": "RUFO API v2.0 funcionando"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        system = SYSTEM_PROMPT
        if request.dashboard_context:
            system += f"\n\nCONTEXTO DEL TABLERO:\n{request.dashboard_context}"

        messages = []
        
        # Si hay imagen, agregarla al último mensaje del usuario
        if request.image_base64:
            # Construir mensajes anteriores normales
            for msg in request.messages[:-1]:
                if msg.role in ["user", "assistant"]:
                    messages.append({"role": msg.role, "content": msg.content})
            
            # Último mensaje con imagen
            last_msg = request.messages[-1] if request.messages else None
            user_text = last_msg.content if last_msg else "Analiza este dashboard"
            
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": request.image_media_type,
                            "data": request.image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": user_text
                    }
                ]
            })
            # Vision requiere claude-sonnet para mejor análisis
            model = "claude-sonnet-4-5"
        else:
            for msg in request.messages:
                if msg.role in ["user", "assistant"]:
                    messages.append({"role": msg.role, "content": msg.content})
            model = request.model

        response = client.messages.create(
            model=model,
            max_tokens=1024,
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
