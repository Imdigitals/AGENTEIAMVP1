from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
import traceback

from .models import Cita
from .chatgpt import consulta_chatgpt

def index(request):
    """
    Vista para renderizar la página principal del chatbot.
    """
    return render(request, 'getsymptoms/index.html')

@csrf_exempt
def webhook(request):
    """
    Endpoint de fulfillment para Dialogflow.
    - Si el usuario indica fecha y hora, guarda la cita y confirma con un cierre profesional.
    - En cualquier otro caso, ChatGPT se encarga de precalificar el lead y guiar la conversación.
    """
    if request.method != 'POST':
        return JsonResponse({'fulfillmentText': 'Método no permitido.'}, status=405)

    try:
        data = json.loads(request.body)
        qr = data.get('queryResult', {})
        params = qr.get('parameters', {})
        user_text = qr.get('queryText', '')
    except json.JSONDecodeError:
        return JsonResponse({'fulfillmentText': 'Error al procesar la solicitud.'}, status=400)

    # Intent de agendar cita: cuando detectamos fecha y hora en los parámetros
    fecha = params.get('fecha')
    hora  = params.get('Hora') or params.get('hora')
    if fecha and hora:
        especialidad = params.get('especialidad') or params.get('location', {}).get('business-name', '')
        contacto     = params.get('contacto', '')

        # Parseo estricto de fecha y hora con formatos conocidos
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date() if isinstance(fecha, str) else fecha
        except Exception:
            fecha_obj = None
        try:
            hora_obj  = datetime.strptime(hora, "%H:%M").time() if isinstance(hora, str) else hora
        except Exception:
            hora_obj = None

        if fecha_obj and hora_obj:
            # Guardar cita en la base de datos
            Cita.objects.create(
                fecha=fecha_obj,
                hora=hora_obj,
                especialidad=especialidad,
                contacto=contacto
            )
            # Confirmación profesional con ChatGPT
            system_prompt = (
                "Eres un asistente médico profesional y amable. "
                "Confirma la cita con un cierre humano y profesional."
            )
            prompt = (
                f"Tu cita en {especialidad} ha sido agendada para el {fecha_obj.strftime('%d/%m/%Y')} "
                f"a las {hora_obj.strftime('%H:%M')}. Te contactaremos al {contacto}. "
                "¡Gracias por confiar en nosotros! ¿Hay algo más en lo que pueda ayudarte hoy?"
            )
            try:
                respuesta = consulta_chatgpt(
                    prompt=prompt,
                    contexto=[{'role': 'system', 'content': system_prompt}]
                )
            except Exception as e:
                traceback.print_exc()
                return JsonResponse({'fulfillmentText': f"Error con OpenAI: {e}"}, status=500)
        else:
            respuesta = (
                "Lo siento, no pude interpretar la fecha u hora que proporcionaste. "
                "Por favor indícame nuevamente cuándo te gustaría agendar tu cita."
            )
        return JsonResponse({'fulfillmentText': respuesta})

    # Fallback: toda otra interacción la maneja ChatGPT para precalificar el lead
    system_prompt = (
        "Eres un asistente de salud muy humano y conversacional. "
        "Tu tarea es precalificar al cliente: averiguar sus necesidades, objetivos y presupuesto, "
        "y cuando esté listo, guiarlo a indicar fecha y hora para agendar. Mantén un tono profesional y empático."
    )
    try:
        respuesta = consulta_chatgpt(
            prompt=user_text,
            contexto=[{'role': 'system', 'content': system_prompt}]
        )
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'fulfillmentText': f"Error con OpenAI: {e}"}, status=500)

    return JsonResponse({'fulfillmentText': respuesta})
