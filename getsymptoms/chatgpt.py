# getsymptoms/chatgpt.py

import os
import openai

# sigue leyendo la clave desde la variable de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

def consulta_chatgpt(prompt: str, contexto: list = None) -> str:
    """
    Envía `prompt` a ChatGPT (vía la API v1.x de openai-python)
    y devuelve la respuesta como texto.
    """
    mensajes = contexto or []
    mensajes.append({"role": "user", "content": prompt})

    # DEBUG logs
    print(f"[DEBUG OpenAI API Key]: {openai.api_key[:10]}...")
    print(f"[DEBUG Prompt]: {prompt}")

    try:
        # ← aquí usamos la nueva ruta del cliente
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=mensajes,
            temperature=0.8,
            max_tokens=500,
        )
        # la respuesta sigue en resp.choices[0].message.content
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR OpenAI]: {e}")
        return "Lo siento, tuve un problema al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde."
