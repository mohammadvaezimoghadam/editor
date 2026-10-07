"""
Serializers for Wagtail AI REST API endpoints.
Provides clean request parsing, validation, and standardized JSON output schemas.
"""
from rest_framework import serializers

from .models import Prompt


class PromptSerializer(serializers.ModelSerializer):
    """Serializer for Prompt instances."""
    is_default = serializers.BooleanField(read_only=True)
    prompt_value = serializers.CharField(read_only=True)

    class Meta:
        model = Prompt
        fields = [
            "uuid",
            "label",
            "description",
            "prompt",
            "method",
            "is_default",
            "prompt_value",
        ]


class TextCompletionRequestSerializer(serializers.Serializer):
    """
    Request serializer for text completion and rewriting operations.
    Supports either a stored prompt (via prompt_uuid) or an ad-hoc custom_instruction.
    """
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="The input text to be processed, rewritten, or completed.",
    )
    method = serializers.ChoiceField(
        choices=["replace", "append"],
        default="replace",
        required=False,
        help_text="'replace' to rewrite/improve content, or 'append' to continue writing.",
    )
    prompt_uuid = serializers.UUIDField(
        required=False,
        allow_null=True,
        default=None,
        help_text="UUID of a predefined Prompt stored in the database.",
    )
    custom_instruction = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Ad-hoc instruction/prompt (e.g. 'Translate to Persian', 'Make tone formal').",
    )

    def validate_prompt_uuid(self, value):
        if value:
            prompt = Prompt.objects.filter(uuid=value).first()
            if not prompt:
                raise serializers.ValidationError(f"Prompt with UUID '{value}' does not exist.")
            return prompt
        return None

    def validate(self, attrs):
        # Attach the resolved prompt object into validated_data
        attrs["prompt_obj"] = attrs.get("prompt_uuid")
        return attrs


class TextCompletionResponseSerializer(serializers.Serializer):
    """
    Standardized response schema for text AI operations.
    """
    success = serializers.BooleanField(default=True)
    result = serializers.CharField()
    method = serializers.CharField()
    model = serializers.CharField()
