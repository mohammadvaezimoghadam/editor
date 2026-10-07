import warnings
from functools import cache
from typing import TYPE_CHECKING, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import receiver
from django.test.signals import setting_changed
from django.utils.module_loading import import_string
from django_ai_core.llm import LLMService
from wagtail.contrib.settings.models import BaseGenericSetting, BaseSiteSetting
from wagtail.models import Site

from wagtail_ai import ai
from wagtail_ai.utils.deprecation import WagtailAISettingsDeprecationWarning

if TYPE_CHECKING:
    from wagtail_ai.models import AgentSettingsMixin

_DEFAULT_MODEL_PROVIDER = "openai"
DEFAULT_PROVIDER_ALIAS = "default"


def get_providers() -> dict[str, dict[str, str]]:
    return getattr(settings, "WAGTAIL_AI", {}).get("PROVIDERS", {})


def get_provider(alias=DEFAULT_PROVIDER_ALIAS) -> dict[str, str]:
    """
    Get a provider configuration by alias.

    Args:
        alias: The provider alias to look up

    Returns:
        Provider configuration dict with ``"provider"`` and ``"model"`` keys,
        and any other keys to be passed as keyword arguments to the ``LLMService`` constructor.

    Raises:
        ``ImproperlyConfigured``: If provider not found
    """
    # Check if user configured provider and access token in AgentSettings (database)
    try:
        agent_settings = get_agent_settings()
        if (
            alias == DEFAULT_PROVIDER_ALIAS
            and agent_settings
            and getattr(agent_settings, "ai_provider", None)
            and agent_settings.ai_provider != "echo"
        ):
            prov_dict = {
                "provider": agent_settings.ai_provider,
                "model": agent_settings.ai_model or "gpt-4o-mini",
            }
            if agent_settings.ai_api_key:
                prov_dict["api_key"] = agent_settings.ai_api_key
            if agent_settings.ai_api_base:
                prov_dict["api_base"] = agent_settings.ai_api_base
            return prov_dict
    except Exception:
        pass

    providers = get_providers()
    provider = providers.get(alias)

    # Legacy fallback for backwards compatibility (only for DEFAULT_PROVIDER_ALIAS)
    if not provider and alias == DEFAULT_PROVIDER_ALIAS:
        backend = ai.get_backend()
        model = backend.config.model_id
        warnings.warn(
            f"No '{DEFAULT_PROVIDER_ALIAS}' provider configured in "
            "WAGTAIL_AI['PROVIDERS'], falling back to "
            f"'{_DEFAULT_MODEL_PROVIDER}' provider with the '{model}' model from "
            "the default backend's 'MODEL_ID' setting. This fallback behavior is "
            "deprecated and will be removed in a future release. "
            "Please configure a default provider in WAGTAIL_AI['PROVIDERS'].",
            WagtailAISettingsDeprecationWarning,
            stacklevel=2,
        )
        provider = {"provider": _DEFAULT_MODEL_PROVIDER, "model": model}
        return provider

    if not provider:
        raise ImproperlyConfigured(
            f"Provider with alias '{alias}' not found in WAGTAIL_AI['PROVIDERS']."
        )

    return provider


@cache
def get_llm_service(alias=DEFAULT_PROVIDER_ALIAS) -> LLMService:
    """
    Get an LLM service instance for the given provider alias.

    Args:
        alias: The provider alias to look up

    Returns:
        LLMService instance configured with the specified provider
    """
    return LLMService.create(**get_provider(alias))


def get_agent_settings_model() -> "type[BaseGenericSetting | BaseSiteSetting]":
    wagtail_ai_settings = getattr(settings, "WAGTAIL_AI", {})
    model_path = wagtail_ai_settings.get(
        "AGENT_SETTINGS_MODEL",
        "wagtail_ai.models.AgentSettings",
    )
    return import_string(model_path)


def get_agent_settings() -> "AgentSettingsMixin":
    model = get_agent_settings_model()
    if issubclass(model, BaseSiteSetting):
        # TODO: support multiple sites
        settings = model.for_site(site=Site.objects.first())
    else:
        settings = model.load()

    return cast("AgentSettingsMixin", settings)


@receiver(setting_changed)
def clear_caches_on_setting_change(sender, setting, **kwargs):
    if setting == "WAGTAIL_AI":
        get_llm_service.cache_clear()
