"""
Service layer for text processing and AI operations.
Decoupled from HTTP request/response lifecycles and Wagtail admin internals.
"""
import logging
from typing import Optional
from dataclasses import dataclass

from . import ai
from .models import Prompt

logger = logging.getLogger(__name__)


class TextServiceException(Exception):
    """Domain exception raised when text processing fails."""
    pass


@dataclass
class TextCompletionResult:
    result_text: str
    method: str
    model: str


class TextProcessingService:
    """
    Core service responsible for text generation, rewriting, and AI transformations.
    Can be used by DRF Views, WebSockets, Celery tasks, or CLI scripts.
    """

    def __init__(self, backend: Optional[ai.AIBackend] = None):
        self._backend = backend

    @property
    def backend(self) -> ai.AIBackend:
        if self._backend is None:
            self._backend = ai.get_backend()
        return self._backend

    def process_text(
        self,
        *,
        text: str,
        method: str = "replace",
        prompt_obj: Optional[Prompt] = None,
        custom_instruction: Optional[str] = None,
    ) -> TextCompletionResult:
        """
        Main entry point for processing text.
        Either prompt_obj or custom_instruction must be provided.
        """
        if not text or not text.strip():
            raise TextServiceException("Input text cannot be empty.")

        # Determine the instruction (system prompt)
        instruction = self._resolve_instruction(prompt_obj, custom_instruction)

        # Execute appropriate strategy based on method
        if method == Prompt.Method.REPLACE or method == "replace":
            result = self._rewrite_text(text=text, instruction=instruction)
        elif method == Prompt.Method.APPEND or method == "append":
            result = self._complete_text(text=text, instruction=instruction)
        else:
            raise TextServiceException(f"Unsupported method: {method}. Use 'replace' or 'append'.")

        model_name = getattr(self.backend.config, "model_id", "unknown")
        return TextCompletionResult(
            result_text=result,
            method=method,
            model=model_name,
        )

    def _resolve_instruction(
        self, prompt_obj: Optional[Prompt], custom_instruction: Optional[str]
    ) -> str:
        if custom_instruction and custom_instruction.strip():
            return custom_instruction.strip()
        if prompt_obj:
            return prompt_obj.prompt_value
        # Default fallback instruction
        return (
            "You are an expert editor. Improve the following text for clarity, "
            "correctness, and flow while preserving its meaning."
        )

    def _rewrite_text(self, *, text: str, instruction: str) -> str:
        """
        Rewrites/replaces content with AI output.
        Handles text chunking safely for long documents.
        """
        try:
            splitter = self.backend.get_text_splitter()
            chunks = splitter.split_text(text)
        except Exception:
            # Fallback if splitter is unavailable
            chunks = [text]

        if not chunks:
            chunks = [text]

        processed_chunks = []
        for chunk in chunks:
            try:
                response = self.backend.prompt_with_context(
                    pre_prompt=instruction,
                    context=chunk,
                )
                output = response.text().strip()
                processed_chunks.append(output)
            except Exception as e:
                logger.exception("AI backend error during text rewriting")
                raise TextServiceException(f"AI processing failed: {str(e)}") from e

        # Recombine chunks cleanly
        return "\n\n".join(processed_chunks)

    def _complete_text(self, *, text: str, instruction: str) -> str:
        """
        Generates continuation for the provided text.
        """
        try:
            length_calculator = self.backend.get_splitter_length_calculator()
            if length_calculator.get_splitter_length(text) > self.backend.config.token_limit:
                raise TextServiceException("Input text exceeds the allowed token limit.")
        except TextServiceException:
            raise
        except Exception:
            pass  # If calculator not implemented, proceed cautiously

        try:
            response = self.backend.prompt_with_context(
                pre_prompt=instruction,
                context=text,
            )
            return response.text().strip()
        except Exception as e:
            logger.exception("AI backend error during text completion")
            raise TextServiceException(f"AI completion failed: {str(e)}") from e
