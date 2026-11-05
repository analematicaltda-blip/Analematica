from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .services.ai_manager.ai_manager import ai_manager
from .services.sanitizers import sanitize_plain_text
from infrastructure.models import AIInteraction, Tenant

class ChatCompletionView(APIView):
    """
    Endpoint para gestionar conversaciones de chatbot.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        history = request.data.get('history', [])
        if not history:
            return Response({"error": "El campo 'history' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        # El último mensaje es el del usuario
        user_prompt = history[-1]['parts'][0]['text']

        # Podríamos añadir un prompt de sistema para dar contexto al chatbot
        system_prompt = "Eres un asistente de marketing. Responde de forma breve y útil."
        full_prompt = f"{system_prompt}\n\nHistorial:\n{history}\n\nUsuario: {user_prompt}"

        try:
            model = request.data.get('model', 'default-text-model')
            raw_text, provider_name = ai_manager.execute_text_generation(prompt=full_prompt, model=model)
            sanitized_text = sanitize_plain_text(raw_text)

            AIInteraction.objects.create(
                tenant=request.user.tenant,
                user=request.user,
                proveedor_usado=provider_name,
                prompt_original=full_prompt,
                resultado=sanitized_text,
                costo_estimado=0.0
            )

            return Response({"response": sanitized_text}, status=status.HTTP_200_OK)
        except RuntimeError as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TextGenerationView(APIView):
    """
    Endpoint para la generación de texto simple.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt')
        model = request.data.get('model', 'default-text-model') # El frontend puede especificar un modelo

        if not prompt:
            return Response(
                {"error": "El 'prompt' es un campo requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tenant = request.user.tenant
            if not tenant:
                 return Response({"error": "El usuario no tiene un tenant asociado."}, status=status.HTTP_400_BAD_REQUEST)


            # 1. Ejecutar la generación de texto a través del AIManager
            raw_text, provider_name = ai_manager.execute_text_generation(prompt=prompt, model=model)

            # 2. Sanitizar la respuesta de la IA
            sanitized_text = sanitize_plain_text(raw_text)

            # 3. Persistir la interacción con el resultado ya sanitizado
            AIInteraction.objects.create(
                tenant=tenant,
                user=request.user,
                proveedor_usado=provider_name,
                prompt_original=prompt,
                resultado=sanitized_text, # Guardar el texto limpio
                costo_estimado=0.0 # TODO: Calcular costo real
            )

            return Response({"generated_text": sanitized_text}, status=status.HTTP_200_OK)

        except RuntimeError as e:
            # Error si no hay proveedor disponible
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            # Captura de otros errores inesperados
            return Response(
                {"error": f"Ocurrió un error inesperado: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
