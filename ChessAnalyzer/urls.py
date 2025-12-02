from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

# app urls
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('upload/', views.upload, name='upload'),
    path('display/', views.display, name='display'),
    path('graph/', views.advantage_graph, name='advantage_graph'),
    path('analyze-online/', views.analyze_online, name='analyze_online'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
