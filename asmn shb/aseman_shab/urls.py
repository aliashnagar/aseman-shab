from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


def custom_404_view(request: HttpRequest, exception):
    return render(request, "404.html", status=404)


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("store.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = custom_404_view
