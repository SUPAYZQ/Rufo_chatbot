# 🦉 RUFO - Asistente para Power BI

Chatbot institucional de OEFA integrado en tableros de Power BI, powered by Claude AI.

## Archivos del proyecto

```
powerbi-chatbot/
├── main.py              # API backend (FastAPI + Claude)
├── chat.html            # Frontend del chatbot (RUFO)
├── requirements.txt     # Dependencias Python
├── render.yaml          # Configuración deploy Render.com
├── .gitignore           # Archivos a ignorar en Git
└── README.md
```

## Deploy en Render.com

1. Subir este repositorio a GitHub
2. Crear cuenta en render.com
3. New → Web Service → conectar repo
4. Agregar variable de entorno: ANTHROPIC_API_KEY
5. Start command: uvicorn main:app --host 0.0.0.0 --port $PORT

## Integración en Power BI

Crear medida DAX:
```
ChatRUFO = "<iframe src='https://TU-APP.onrender.com/chat' width='100%' height='100%' frameborder='0'></iframe>"
```

## Desarrollo local

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
python -m http.server 3000  # para el frontend
```
