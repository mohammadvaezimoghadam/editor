"""
API URL routing for Wagtail AI REST endpoints.
"""
from django.urls import path
from .api_views import (
    TextCompletionAPIView,
    PromptListAPIView,
    ProofreadAPIView,
    RewriteAPIView,
    SummarizeAPIView,
    ContinueWritingAPIView,
)

app_name = "wagtail_ai_api"

urlpatterns = [
    # Universal flexible endpoint
    path("text/complete/", TextCompletionAPIView.as_view(), name="text_complete"),
    
    # Prompt listing
    path("prompts/", PromptListAPIView.as_view(), name="prompts_list"),
    
    # Specialized direct endpoints for mobile & Flutter apps
    path("proofread/", ProofreadAPIView.as_view(), name="proofread"),
    path("rewrite/", RewriteAPIView.as_view(), name="rewrite"),
    path("summarize/", SummarizeAPIView.as_view(), name="summarize"),
    path("continue/", ContinueWritingAPIView.as_view(), name="continue"),
]
