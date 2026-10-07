import time
from django.shortcuts import render
from django.http import JsonResponse
from wagtail_ai.ai import get_backend
from wagtail_ai.models import Prompt, AgentSettings
from django_ai_core.contrib.agents import registry


def ai_playground(request):
    agent_settings = AgentSettings.load()
    prompts = Prompt.objects.all()
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
                agent_settings.ai_provider = request.POST.get("ai_provider", "echo")
                agent_settings.ai_model = request.POST.get("ai_model", "").strip() or "gpt-4o-mini"
                agent_settings.ai_api_key = request.POST.get("ai_api_key", "").strip()
                agent_settings.ai_api_base = request.POST.get("ai_api_base", "").strip().rstrip("/")
                agent_settings.save()
                # Clear cached LLMService so new provider settings take effect
                from wagtail_ai.agents.base import get_llm_service
                get_llm_service.cache_clear()
                success_message = f"تنظیمات پرووایدر ({agent_settings.get_ai_provider_display()}) با موفقیت ذخیره شد."
            except Exception as e:
                error = f"خطا در ذخیره تنظیمات: {e}"

            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("format") == "json":
                return JsonResponse({
                    "success": not bool(error),
                    "message": success_message,
                    "error": error,
                    "provider": agent_settings.ai_provider,
                    "model": agent_settings.ai_model,
                })
        else:
            backend = get_backend()
            start_time = time.time()
            try:
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
                            if not pre_prompt:
                                pre_prompt = prompt_obj.prompt_value
                        except Prompt.DoesNotExist:
                            pass

                    if not pre_prompt:
                        pre_prompt = "لطفاً متن زیر را بررسی و پاسخ مناسب ارائه دهید:"

                    if test_mode == "agent_feedback":
                        agent_cls = registry.get("wai_content_feedback")
                        agent_instance = agent_cls()
                        feedback_dict = agent_instance.execute(
                            content_text=context_text,
                            content_html=f"<p>{context_text}</p>",
                            content_language="Persian",
                            editor_language="Persian",
                        )
                        import json
                        result = json.dumps(feedback_dict, indent=2, ensure_ascii=False)
                    else:
                        ai_response = backend.prompt_with_context(
                            pre_prompt=pre_prompt,
                            context=context_text,
                        )
                        result = ai_response.text()

                execution_time = round((time.time() - start_time) * 1000, 2)
            except Exception as e:
                error = str(e)
                execution_time = round((time.time() - start_time) * 1000, 2)

            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("format") == "json":
                return JsonResponse({
                    "result": result,
                    "error": error,
                    "execution_time_ms": execution_time,
                    "backend": backend.__class__.__name__,
                })

    # Reload backend after potential settings change
    backend = get_backend()
    backend_settings = getattr(backend, "config", None)

    context = {
        "agent_settings": agent_settings,
        "backend_name": backend.__class__.__name__,
        "backend_module": backend.__class__.__module__,
        "backend_config": backend_settings,
        "active_provider": getattr(agent_settings, "ai_provider", "echo"),
        "active_model": getattr(agent_settings, "ai_model", "echo"),
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
