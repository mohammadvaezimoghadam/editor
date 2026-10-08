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
    
    General flexible endpoint to process, rewrite, or complete text via AI.
    Accepts prompt UUID or custom instruction.
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
                {"success": False, "error": f"Internal AI processing error: {e}"},
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


class ProofreadAPIView(APIView):
    """
    POST /api/v1/ai/proofread/
    
    Direct endpoint for proofreading & grammar correction.
    Payload: {"text": "متن مورد نظر"}
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        text = request.data.get("text", "").strip()
        if not text:
            return Response(
                {"success": False, "error": "Field 'text' is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prompt_obj = Prompt.objects.filter(default_prompt_id=1).first()
        service = TextProcessingService()

        try:
            result = service.process_text(
                text=text,
                method="replace",
                prompt_obj=prompt_obj,
            )
            return Response({
                "success": True,
                "result": result.result_text,
                "action": "proofread",
                "model": result.model,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RewriteAPIView(APIView):
    """
    POST /api/v1/ai/rewrite/
    
    Direct endpoint for rewriting and polishing.
    Payload: {"text": "متن", "tone": "polish" | "formal" | "casual"}
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        text = request.data.get("text", "").strip()
        tone = request.data.get("tone", "polish").lower()
        if not text:
            return Response(
                {"success": False, "error": "Field 'text' is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Tone mapping to prompt IDs: 3=polish, 4=formal, 5=casual
        tone_map = {
            "polish": 3,
            "formal": 4,
            "casual": 5,
        }
        prompt_id = tone_map.get(tone, 3)
        prompt_obj = Prompt.objects.filter(default_prompt_id=prompt_id).first()
        service = TextProcessingService()

        try:
            result = service.process_text(
                text=text,
                method="replace",
                prompt_obj=prompt_obj,
            )
            return Response({
                "success": True,
                "result": result.result_text,
                "tone": tone,
                "model": result.model,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SummarizeAPIView(APIView):
    """
    POST /api/v1/ai/summarize/
    
    Direct endpoint for summarization.
    Payload: {"text": "متن مورد نظر برای خلاصه کردن"}
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        text = request.data.get("text", "").strip()
        if not text:
            return Response(
                {"success": False, "error": "Field 'text' is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prompt_obj = Prompt.objects.filter(default_prompt_id=6).first()
        service = TextProcessingService()

        try:
            result = service.process_text(
                text=text,
                method="replace",
                prompt_obj=prompt_obj,
            )
            return Response({
                "success": True,
                "result": result.result_text,
                "action": "summarize",
                "model": result.model,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ContinueWritingAPIView(APIView):
    """
    POST /api/v1/ai/continue/
    
    Direct endpoint for continuing and completing content.
    Payload: {"text": "متن اولیه"}
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        text = request.data.get("text", "").strip()
        if not text:
            return Response(
                {"success": False, "error": "Field 'text' is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prompt_obj = Prompt.objects.filter(default_prompt_id=2).first()
        service = TextProcessingService()

        try:
            result = service.process_text(
                text=text,
                method="append",
                prompt_obj=prompt_obj,
            )
            return Response({
                "success": True,
                "result": result.result_text,
                "action": "continue",
                "model": result.model,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
