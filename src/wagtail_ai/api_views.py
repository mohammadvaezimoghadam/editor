"""
REST API Views for Wagtail AI.
Built with Django REST Framework (DRF) following Clean Architecture principles.
Decoupled controllers that delegate business logic to the Service Layer.
"""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Prompt
from .serializers import (
    PromptSerializer,
    TextCompletionRequestSerializer,
    TextCompletionResponseSerializer,
)
from .services import TextProcessingService, TextServiceException

logger = logging.getLogger(__name__)


class TextCompletionAPIView(APIView):
    """
    POST /api/v1/ai/text/complete/
    
    Accepts JSON payload to generate, rewrite, or complete text via AI.
    
    Payload example:
    {
        "text": "Django is a high-level Python web framework.",
        "method": "replace",
        "custom_instruction": "Summarize this into Persian in one sentence."
    }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = TextCompletionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data
        service = TextProcessingService()

        try:
            result = service.process_text(
                text=validated_data["text"],
                method=validated_data["method"],
                prompt_obj=validated_data.get("prompt_obj"),
                custom_instruction=validated_data.get("custom_instruction"),
            )
        except TextServiceException as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception("Unexpected error in TextCompletionAPIView")
            return Response(
                {"success": False, "error": "Internal AI processing error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_data = {
            "success": True,
            "result": result.result_text,
            "method": result.method,
            "model": result.model,
        }
        output_serializer = TextCompletionResponseSerializer(response_data)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class PromptListAPIView(ListAPIView):
    """
    GET /api/v1/ai/prompts/
    
    Returns a list of all predefined system and custom prompts.
    """
    permission_classes = [AllowAny]
    queryset = Prompt.objects.all().order_by("id")
    serializer_class = PromptSerializer
