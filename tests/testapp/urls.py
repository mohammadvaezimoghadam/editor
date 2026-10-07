from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from .views import ai_playground

urlpatterns = [
    path("", ai_playground, name="ai_playground"),
    path("api/v1/ai/", include("wagtail_ai.api_urls")),
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    *staticfiles_urlpatterns(),
    path("wagtail/", include(wagtail_urls)),
]
