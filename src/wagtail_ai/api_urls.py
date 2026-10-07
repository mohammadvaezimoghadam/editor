"""
API URL routing for Wagtail AI REST endpoints.
"""
from django.urls import path
from .api_views import TextCompletionAPIView, PromptListAPIView

app_name = "wagtail_ai_api"

urlpatterns = [
    path("text/complete/", TextCompletionAPIView.as_view(), name="text_complete"),
    path("prompts/", PromptListAPIView.as_view(), name="prompts_list"),
]
