import time
import logging
from django.shortcuts import render
from django.http import JsonResponse
from wagtail_ai.ai import get_backend
from wagtail_ai.models import Prompt, AgentSettings

from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
def ai_playground(request):
    try:
        agent_settings = AgentSettings.load()
    except Exception as e:
        logger.warning(f"Failed to load AgentSettings: {e}")
        agent_settings = None

    try:
        prompts = Prompt.objects.all()
    except Exception as e:
        logger.warning(f"Failed to load Prompts: {e}")
        prompts = []

    result = None
    error = None
    success_message = None
    execution_time = None

    selected_prompt_uuid = request.POST.get("prompt_uuid", "")
    custom_pre_prompt = request.POST.get("custom_pre_prompt", "").strip()
    context_text = request.POST.get("context_text", "").strip()
    test_mode = request.POST.get("test_mode", "prompt")
    action = request.POST.get("action", "run_ai")

    if request.method == "POST":
        if action == "save_provider_settings":
            try:
                if agent_settings is None:
                    agent_settings = AgentSettings()
                agent_settings.ai_provider = request.POST.get("ai_provider", "echo")
                agent_settings.ai_model = request.POST.get("ai_model", "").strip() or "gpt-4o-mini"
                agent_settings.ai_api_key = request.POST.get("ai_api_key", "").strip()
                agent_settings.ai_api_base = request.POST.get("ai_api_base", "").strip().rstrip("/")
                agent_settings.save()
                # Clear cached LLMService so new provider settings take effect
                try:
                    from wagtail_ai.agents.base import get_llm_service
                    get_llm_service.cache_clear()
                except Exception:
                    pass
                success_message = f"تنظیمات پرووایدر ({agent_settings.get_ai_provider_display()}) با موفقیت ذخیره شد."
            except Exception as e:
                error = f"خطا در ذخیره تنظیمات: {e}"

            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("format") == "json":
                return JsonResponse({
                    "success": not bool(error),
                    "message": success_message,
                    "error": error,
                    "provider": getattr(agent_settings, "ai_provider", "echo"),
                    "model": getattr(agent_settings, "ai_model", "echo"),
                })
        else:
            start_time = time.time()
            try:
                backend = get_backend()
                if test_mode == "describe_image" and "image_file" in request.FILES:
                    image_file = request.FILES["image_file"]
                    prompt = custom_pre_prompt or "Describe this image in detail."
                    ai_response = backend.describe_image(image_file=image_file, prompt=prompt)
                    result = ai_response.text()
                else:
                    if not context_text:
                        raise ValueError("متن ورودی (Context Text) نباید خالی باشد.")

                    pre_prompt = custom_pre_prompt
                    if selected_prompt_uuid:
                        try:
                            prompt_obj = Prompt.objects.get(uuid=selected_prompt_uuid)
                            pre_prompt = prompt_obj.prompt_value
                        except Prompt.DoesNotExist:
                            pass

                    if not pre_prompt:
                        pre_prompt = "You are a professional editor. Improve the following text for clarity, correctness, and flow:"

                    from wagtail_ai.services import TextProcessingService
                    service = TextProcessingService(backend=backend)
                    service_result = service.process_text(
                        text=context_text,
                        method="replace",
                        custom_instruction=pre_prompt,
                    )
                    result = service_result.result_text
            except Exception as e:
                error = f"خطا در پردازش هوش مصنوعی: {e}"
                logger.exception("AI processing error in playground")

            execution_time = round(time.time() - start_time, 2)

            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("format") == "json":
                return JsonResponse({
                    "success": not bool(error),
                    "result": result,
                    "error": error,
                    "execution_time": execution_time,
                })

    # Safely resolve backend for display
    try:
        backend = get_backend()
        backend_name = backend.__class__.__name__
        backend_module = backend.__class__.__module__
        backend_settings = getattr(backend, "config", None)
    except Exception as e:
        logger.warning(f"Failed to get AI backend: {e}")
        backend_name = "Echo (تستی)"
        backend_module = "wagtail_ai.ai.echo"
        backend_settings = None

    context = {
        "agent_settings": agent_settings,
        "backend_name": backend_name,
        "backend_module": backend_module,
        "backend_config": backend_settings,
        "active_provider": getattr(agent_settings, "ai_provider", "echo") if agent_settings else "echo",
        "active_model": getattr(agent_settings, "ai_model", "gpt-4o-mini") if agent_settings else "gpt-4o-mini",
        "prompts": prompts,
        "selected_prompt_uuid": selected_prompt_uuid,
        "custom_pre_prompt": custom_pre_prompt,
        "context_text": context_text,
        "test_mode": test_mode,
        "result": result,
        "error": error,
        "success_message": success_message,
        "execution_time": execution_time,
    }
    return render(request, "testapp/ai_playground.html", context)
